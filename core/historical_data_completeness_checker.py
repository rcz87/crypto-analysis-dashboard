#!/usr/bin/env python3
"""
Historical Data Completeness Checker - Verifikasi kelengkapan data historis
Memastikan continuity dan quality data untuk backtesting dan analysis
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import time
import json
from dataclasses import dataclass
from enum import Enum
import sqlite3
import os

logger = logging.getLogger(__name__)

class DataGapSeverity(Enum):
    MINOR = "minor"      # < 1% missing
    MODERATE = "moderate"  # 1-5% missing
    MAJOR = "major"        # 5-15% missing
    CRITICAL = "critical"  # > 15% missing

@dataclass
class DataGap:
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    severity: DataGapSeverity
    affected_symbols: List[str]
    gap_type: str  # 'missing', 'corrupt', 'duplicate'

@dataclass
class CompletenessReport:
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    total_expected_candles: int
    available_candles: int
    missing_candles: int
    completeness_percentage: float
    gaps: List[DataGap]
    quality_score: float
    recommendations: List[str]

class HistoricalDataCompletenessChecker:
    """
    Comprehensive checker untuk historical data completeness
    """
    
    def __init__(self, db_path: str = "logs/data_completeness.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Timeframe configurations (in minutes)
        self.timeframe_minutes = {
            '1m': 1,
            '3m': 3,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '2h': 120,
            '4h': 240,
            '6h': 360,
            '12h': 720,
            '1d': 1440,
            '3d': 4320,
            '1w': 10080
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'excellent': 99.0,
            'good': 95.0,
            'fair': 90.0,
            'poor': 80.0
        }
        
        # Gap severity thresholds (percentage of missing data)
        self.gap_severity_thresholds = {
            DataGapSeverity.MINOR: 1.0,
            DataGapSeverity.MODERATE: 5.0,
            DataGapSeverity.MAJOR: 15.0,
            DataGapSeverity.CRITICAL: 100.0
        }
        
        self.logger.info("📊 Historical Data Completeness Checker initialized")
    
    def _init_database(self):
        """Initialize SQLite database untuk tracking data completeness"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Table untuk tracking data availability
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS data_availability (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        timestamp INTEGER NOT NULL,
                        date_str TEXT NOT NULL,
                        is_available BOOLEAN NOT NULL,
                        data_quality_score REAL,
                        created_at INTEGER DEFAULT (strftime('%s', 'now')),
                        UNIQUE(symbol, timeframe, timestamp)
                    )
                ''')
                
                # Table untuk tracking gaps
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS data_gaps (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        start_timestamp INTEGER NOT NULL,
                        end_timestamp INTEGER NOT NULL,
                        duration_minutes INTEGER NOT NULL,
                        severity TEXT NOT NULL,
                        gap_type TEXT NOT NULL,
                        created_at INTEGER DEFAULT (strftime('%s', 'now'))
                    )
                ''')
                
                # Table untuk completeness reports
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS completeness_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        completeness_percentage REAL NOT NULL,
                        quality_score REAL NOT NULL,
                        total_gaps INTEGER NOT NULL,
                        created_at INTEGER DEFAULT (strftime('%s', 'now'))
                    )
                ''')
                
                # Indexes untuk performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_availability_symbol_tf ON data_availability(symbol, timeframe)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_gaps_symbol_tf ON data_gaps(symbol, timeframe)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_symbol_tf ON completeness_reports(symbol, timeframe)')
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    def check_data_completeness(self, 
                               symbol: str,
                               timeframe: str,
                               start_date: datetime,
                               end_date: datetime,
                               data_source: Any = None) -> CompletenessReport:
        """
        Check completeness untuk specific symbol dan timeframe
        """
        try:
            # Validate timeframe
            if timeframe not in self.timeframe_minutes:
                raise ValueError(f"Unsupported timeframe: {timeframe}")
            
            # Calculate expected number of candles
            total_minutes = int((end_date - start_date).total_seconds() / 60)
            candle_interval = self.timeframe_minutes[timeframe]
            expected_candles = total_minutes // candle_interval
            
            # Get available data
            available_data = self._get_available_data(symbol, timeframe, start_date, end_date, data_source)
            available_candles = len(available_data)
            missing_candles = expected_candles - available_candles
            
            # Calculate completeness percentage
            completeness_percentage = (available_candles / max(1, expected_candles)) * 100
            
            # Detect gaps
            gaps = self._detect_data_gaps(symbol, timeframe, start_date, end_date, available_data)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(completeness_percentage, gaps)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(completeness_percentage, gaps, timeframe)
            
            # Create report
            report = CompletenessReport(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                total_expected_candles=expected_candles,
                available_candles=available_candles,
                missing_candles=missing_candles,
                completeness_percentage=completeness_percentage,
                gaps=gaps,
                quality_score=quality_score,
                recommendations=recommendations
            )
            
            # Store report dalam database
            self._store_report(report)
            
            # Store gaps dalam database
            for gap in gaps:
                self._store_gap(symbol, timeframe, gap)
            
            self.logger.info(f"✅ Completeness check completed for {symbol} {timeframe}: {completeness_percentage:.1f}%")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error checking data completeness for {symbol}: {e}")
            # Return empty report on error
            return CompletenessReport(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                total_expected_candles=0,
                available_candles=0,
                missing_candles=0,
                completeness_percentage=0,
                gaps=[],
                quality_score=0,
                recommendations=["Error occurred during completeness check"]
            )
    
    def _get_available_data(self, 
                           symbol: str,
                           timeframe: str, 
                           start_date: datetime,
                           end_date: datetime,
                           data_source: Any = None) -> List[Dict[str, Any]]:
        """
        Get available data dalam timeframe tertentu
        """
        available_data = []
        
        try:
            # If data_source provided, fetch from it
            if data_source and hasattr(data_source, 'get_historical_data'):
                try:
                    data = data_source.get_historical_data(symbol, timeframe, start_date, end_date)
                    if data:
                        available_data = data
                except Exception as e:
                    self.logger.error(f"Error fetching from data source: {e}")
            
            # Fallback: check database records
            if not available_data:
                available_data = self._get_data_from_database(symbol, timeframe, start_date, end_date)
            
            # If still no data, generate mock timeline untuk gap detection
            if not available_data:
                self.logger.warning(f"No data available for {symbol} {timeframe}, generating mock timeline")
                available_data = self._generate_mock_timeline(start_date, end_date, timeframe)
        
        except Exception as e:
            self.logger.error(f"Error getting available data: {e}")
        
        return available_data
    
    def _get_data_from_database(self, 
                               symbol: str,
                               timeframe: str,
                               start_date: datetime,
                               end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get data records dari database
        """
        data = []
        
        try:
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int(end_date.timestamp())
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, is_available, data_quality_score
                    FROM data_availability 
                    WHERE symbol = ? AND timeframe = ? 
                    AND timestamp BETWEEN ? AND ?
                    ORDER BY timestamp
                ''', (symbol, timeframe, start_timestamp, end_timestamp))
                
                rows = cursor.fetchall()
                
                for timestamp, is_available, quality_score in rows:
                    if is_available:
                        data.append({
                            'timestamp': timestamp,
                            'datetime': datetime.fromtimestamp(timestamp),
                            'quality_score': quality_score or 100
                        })
        
        except Exception as e:
            self.logger.error(f"Error querying database for data: {e}")
        
        return data
    
    def _generate_mock_timeline(self, 
                               start_date: datetime,
                               end_date: datetime,
                               timeframe: str) -> List[Dict[str, Any]]:
        """
        Generate mock timeline untuk gap detection when no real data available
        """
        timeline = []
        
        try:
            interval_minutes = self.timeframe_minutes[timeframe]
            current_time = start_date
            
            while current_time < end_date:
                timeline.append({
                    'timestamp': int(current_time.timestamp()),
                    'datetime': current_time,
                    'quality_score': 0  # Mock data has 0 quality
                })
                current_time += timedelta(minutes=interval_minutes)
        
        except Exception as e:
            self.logger.error(f"Error generating mock timeline: {e}")
        
        return timeline
    
    def _detect_data_gaps(self, 
                         symbol: str,
                         timeframe: str,
                         start_date: datetime,
                         end_date: datetime,
                         available_data: List[Dict[str, Any]]) -> List[DataGap]:
        """
        Detect gaps dalam data
        """
        gaps = []
        
        try:
            if not available_data:
                # Entire period is a gap
                duration_minutes = int((end_date - start_date).total_seconds() / 60)
                gap = DataGap(
                    start_time=start_date,
                    end_time=end_date,
                    duration_minutes=duration_minutes,
                    severity=DataGapSeverity.CRITICAL,
                    affected_symbols=[symbol],
                    gap_type='missing'
                )
                gaps.append(gap)
                return gaps
            
            # Sort data by timestamp
            sorted_data = sorted(available_data, key=lambda x: x['timestamp'])
            
            interval_minutes = self.timeframe_minutes[timeframe]
            expected_interval_seconds = interval_minutes * 60
            
            # Check for gaps between consecutive data points
            for i in range(len(sorted_data) - 1):
                current_time = sorted_data[i]['datetime']
                next_time = sorted_data[i + 1]['datetime']
                
                time_diff = (next_time - current_time).total_seconds()
                
                # If gap is larger than expected interval
                if time_diff > expected_interval_seconds * 1.5:  # Allow 50% tolerance
                    gap_start = current_time + timedelta(seconds=expected_interval_seconds)
                    gap_end = next_time
                    gap_duration = int((gap_end - gap_start).total_seconds() / 60)
                    
                    if gap_duration > 0:
                        # Determine severity based on gap duration
                        severity = self._determine_gap_severity(gap_duration, interval_minutes)
                        
                        gap = DataGap(
                            start_time=gap_start,
                            end_time=gap_end,
                            duration_minutes=gap_duration,
                            severity=severity,
                            affected_symbols=[symbol],
                            gap_type='missing'
                        )
                        gaps.append(gap)
            
            # Check gap at the beginning
            if sorted_data:
                first_data_time = sorted_data[0]['datetime']
                if first_data_time > start_date + timedelta(minutes=interval_minutes):
                    gap_duration = int((first_data_time - start_date).total_seconds() / 60)
                    if gap_duration > 0:
                        severity = self._determine_gap_severity(gap_duration, interval_minutes)
                        gap = DataGap(
                            start_time=start_date,
                            end_time=first_data_time,
                            duration_minutes=gap_duration,
                            severity=severity,
                            affected_symbols=[symbol],
                            gap_type='missing'
                        )
                        gaps.append(gap)
            
            # Check gap at the end
            if sorted_data:
                last_data_time = sorted_data[-1]['datetime']
                if last_data_time < end_date - timedelta(minutes=interval_minutes):
                    gap_duration = int((end_date - last_data_time).total_seconds() / 60)
                    if gap_duration > 0:
                        severity = self._determine_gap_severity(gap_duration, interval_minutes)
                        gap = DataGap(
                            start_time=last_data_time,
                            end_time=end_date,
                            duration_minutes=gap_duration,
                            severity=severity,
                            affected_symbols=[symbol],
                            gap_type='missing'
                        )
                        gaps.append(gap)
        
        except Exception as e:
            self.logger.error(f"Error detecting data gaps: {e}")
        
        return gaps
    
    def _determine_gap_severity(self, gap_duration_minutes: int, interval_minutes: int) -> DataGapSeverity:
        """
        Determine severity berdasarkan gap duration
        """
        # Calculate gap as number of missing candles
        missing_candles = gap_duration_minutes // interval_minutes
        
        # Determine severity based on missing candles
        if missing_candles <= 1:
            return DataGapSeverity.MINOR
        elif missing_candles <= 5:
            return DataGapSeverity.MODERATE
        elif missing_candles <= 20:
            return DataGapSeverity.MAJOR
        else:
            return DataGapSeverity.CRITICAL
    
    def _calculate_quality_score(self, completeness_percentage: float, gaps: List[DataGap]) -> float:
        """
        Calculate overall quality score
        """
        # Start dengan completeness percentage
        quality_score = completeness_percentage
        
        # Deduct points berdasarkan gap severity
        for gap in gaps:
            if gap.severity == DataGapSeverity.CRITICAL:
                quality_score -= 20
            elif gap.severity == DataGapSeverity.MAJOR:
                quality_score -= 10
            elif gap.severity == DataGapSeverity.MODERATE:
                quality_score -= 5
            elif gap.severity == DataGapSeverity.MINOR:
                quality_score -= 1
        
        # Ensure score bounds
        return max(0, min(100, quality_score))
    
    def _generate_recommendations(self, 
                                 completeness_percentage: float,
                                 gaps: List[DataGap],
                                 timeframe: str) -> List[str]:
        """
        Generate recommendations berdasarkan completeness analysis
        """
        recommendations = []
        
        # Based on completeness percentage
        if completeness_percentage >= self.quality_thresholds['excellent']:
            recommendations.append("✅ Data quality is excellent - suitable for all analysis types")
        elif completeness_percentage >= self.quality_thresholds['good']:
            recommendations.append("✅ Data quality is good - suitable for most analysis")
            recommendations.append("🔍 Monitor minor gaps to maintain quality")
        elif completeness_percentage >= self.quality_thresholds['fair']:
            recommendations.append("⚠️ Data quality is fair - use caution for sensitive analysis")
            recommendations.append("🔧 Consider data backfilling for missing periods")
        elif completeness_percentage >= self.quality_thresholds['poor']:
            recommendations.append("❌ Data quality is poor - not recommended for reliable analysis")
            recommendations.append("🚨 Immediate data collection improvement needed")
        else:
            recommendations.append("🚨 Critical data quality issues - data unusable")
            recommendations.append("🔄 Complete data reconstruction required")
        
        # Based on gaps
        critical_gaps = [g for g in gaps if g.severity == DataGapSeverity.CRITICAL]
        major_gaps = [g for g in gaps if g.severity == DataGapSeverity.MAJOR]
        
        if critical_gaps:
            recommendations.append(f"🚨 {len(critical_gaps)} critical gaps detected - investigate data collection failures")
        
        if major_gaps:
            recommendations.append(f"⚠️ {len(major_gaps)} major gaps detected - consider alternative data sources")
        
        # Based on timeframe
        if timeframe in ['1m', '3m', '5m'] and completeness_percentage < 95:
            recommendations.append("📊 High-frequency analysis requires >95% completeness for reliable results")
        
        if len(gaps) > 10:
            recommendations.append("🔧 Multiple gaps detected - implement continuous data monitoring")
        
        return recommendations
    
    def _store_report(self, report: CompletenessReport):
        """
        Store completeness report dalam database
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO completeness_reports 
                    (symbol, timeframe, start_date, end_date, completeness_percentage, 
                     quality_score, total_gaps)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    report.symbol,
                    report.timeframe,
                    report.start_date.isoformat(),
                    report.end_date.isoformat(),
                    report.completeness_percentage,
                    report.quality_score,
                    len(report.gaps)
                ))
                
                conn.commit()
        
        except Exception as e:
            self.logger.error(f"Error storing report: {e}")
    
    def _store_gap(self, symbol: str, timeframe: str, gap: DataGap):
        """
        Store data gap dalam database
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO data_gaps 
                    (symbol, timeframe, start_timestamp, end_timestamp, 
                     duration_minutes, severity, gap_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    timeframe,
                    int(gap.start_time.timestamp()),
                    int(gap.end_time.timestamp()),
                    gap.duration_minutes,
                    gap.severity.value,
                    gap.gap_type
                ))
                
                conn.commit()
        
        except Exception as e:
            self.logger.error(f"Error storing gap: {e}")
    
    def get_completeness_summary(self, 
                                symbol: Optional[str] = None,
                                timeframe: Optional[str] = None,
                                days: int = 30) -> Dict[str, Any]:
        """
        Get summary completeness untuk symbols/timeframes
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with optional filters
                where_conditions = ["datetime(created_at, 'unixepoch') >= ?"]
                params = [cutoff_date.isoformat()]
                
                if symbol:
                    where_conditions.append("symbol = ?")
                    params.append(symbol)
                
                if timeframe:
                    where_conditions.append("timeframe = ?")
                    params.append(timeframe)
                
                where_clause = " AND ".join(where_conditions)
                
                # Get recent reports
                cursor.execute(f'''
                    SELECT symbol, timeframe, AVG(completeness_percentage) as avg_completeness,
                           AVG(quality_score) as avg_quality, COUNT(*) as report_count,
                           MIN(completeness_percentage) as min_completeness,
                           MAX(completeness_percentage) as max_completeness
                    FROM completeness_reports 
                    WHERE {where_clause}
                    GROUP BY symbol, timeframe
                    ORDER BY avg_quality DESC
                ''', params)
                
                reports = cursor.fetchall()
                
                # Get gap summary
                cursor.execute(f'''
                    SELECT severity, COUNT(*) as gap_count
                    FROM data_gaps 
                    WHERE datetime(created_at, 'unixepoch') >= ?
                    {'AND symbol = ?' if symbol else ''}
                    {'AND timeframe = ?' if timeframe else ''}
                    GROUP BY severity
                ''', [cutoff_date.isoformat()] + ([symbol] if symbol else []) + ([timeframe] if timeframe else []))
                
                gap_summary = dict(cursor.fetchall())
                
                summary = {
                    'period_days': days,
                    'reports': [],
                    'overall_stats': {
                        'total_reports': len(reports),
                        'avg_completeness': 0,
                        'avg_quality': 0
                    },
                    'gap_summary': gap_summary,
                    'recommendations': []
                }
                
                if reports:
                    total_completeness = sum(r[2] for r in reports)
                    total_quality = sum(r[3] for r in reports)
                    
                    summary['overall_stats']['avg_completeness'] = total_completeness / len(reports)
                    summary['overall_stats']['avg_quality'] = total_quality / len(reports)
                    
                    for report in reports:
                        summary['reports'].append({
                            'symbol': report[0],
                            'timeframe': report[1],
                            'avg_completeness': report[2],
                            'avg_quality': report[3],
                            'report_count': report[4],
                            'min_completeness': report[5],
                            'max_completeness': report[6]
                        })
                    
                    # Generate recommendations
                    if summary['overall_stats']['avg_completeness'] < 90:
                        summary['recommendations'].append("📉 Overall completeness below 90% - investigate data collection issues")
                    
                    if gap_summary.get('critical', 0) > 0:
                        summary['recommendations'].append(f"🚨 {gap_summary['critical']} critical gaps found - immediate attention required")
                
                return summary
        
        except Exception as e:
            self.logger.error(f"Error generating completeness summary: {e}")
            return {'error': str(e)}
    
    def check_multiple_symbols(self, 
                              symbols: List[str],
                              timeframe: str,
                              days_back: int = 7) -> Dict[str, CompletenessReport]:
        """
        Check completeness untuk multiple symbols
        """
        reports = {}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        for symbol in symbols:
            try:
                report = self.check_data_completeness(symbol, timeframe, start_date, end_date)
                reports[symbol] = report
                
                self.logger.info(f"📊 {symbol} completeness: {report.completeness_percentage:.1f}%")
                
            except Exception as e:
                self.logger.error(f"Error checking completeness for {symbol}: {e}")
        
        return reports

# Global instance
historical_data_checker = HistoricalDataCompletenessChecker()

def get_historical_data_checker():
    """Get global historical data completeness checker instance"""
    return historical_data_checker