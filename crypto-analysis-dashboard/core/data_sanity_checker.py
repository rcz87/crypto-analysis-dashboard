#!/usr/bin/env python3
"""
Data Sanity Checker - Comprehensive data validation and quality control
Deteksi gap/NaN/lag, fallback cache, staleness labeling
"""
import logging
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DataQualityReport:
    timestamp: float
    data_source: str
    quality_score: float  # 0-100
    issues: List[str]
    is_stale: bool
    staleness_seconds: float
    has_gaps: bool
    has_nans: bool
    latency_ms: float
    fallback_used: bool

class DataSanityChecker:
    def __init__(self, cache_dir: str = "logs/data_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Quality thresholds
        self.thresholds = {
            'max_staleness_seconds': 30,      # 30s max untuk real-time data
            'max_latency_ms': 2000,           # 2s max untuk API response  
            'min_quality_score': 70,          # 70/100 minimum quality
            'max_gap_percentage': 5,          # 5% max missing data points
            'max_price_jump_percentage': 10,  # 10% max price jump detection
        }
        
        # Cache untuk fallback
        self.data_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        
        # Quality tracking
        self.quality_history = []
        self.max_history = 1000
        
    def validate_market_data(self, 
                           data: Dict[str, Any],
                           data_source: str,
                           request_timestamp: float = None) -> DataQualityReport:
        """
        Comprehensive market data validation
        """
        try:
            if request_timestamp is None:
                request_timestamp = time.time()
            
            current_time = time.time()
            issues = []
            quality_score = 100.0
            fallback_used = False
            
            # 1. Staleness check
            data_timestamp = data.get('timestamp', current_time)
            staleness_seconds = current_time - data_timestamp
            is_stale = staleness_seconds > self.thresholds['max_staleness_seconds']
            
            if is_stale:
                issues.append(f"Data stale by {staleness_seconds:.1f}s")
                quality_score -= 20
            
            # 2. Latency check
            latency_ms = (current_time - request_timestamp) * 1000
            if latency_ms > self.thresholds['max_latency_ms']:
                issues.append(f"High latency: {latency_ms:.1f}ms")
                quality_score -= 15
                
            # 3. NaN detection
            has_nans = self._detect_nans(data)
            if has_nans:
                issues.append("NaN values detected")
                quality_score -= 25
                
            # 4. Gap detection  
            has_gaps, gap_percentage = self._detect_gaps(data)
            if has_gaps:
                issues.append(f"Data gaps: {gap_percentage:.1f}%")
                quality_score -= (gap_percentage * 2)  # 2 points per % gap
                
            # 5. Price jump detection
            has_jumps, max_jump = self._detect_price_jumps(data)
            if has_jumps:
                issues.append(f"Abnormal price jump: {max_jump:.1f}%")
                quality_score -= 10
                
            # 6. Volume anomaly detection
            has_vol_anomaly = self._detect_volume_anomaly(data)
            if has_vol_anomaly:
                issues.append("Volume anomaly detected")
                quality_score -= 5
                
            # 7. Check if fallback cache needed
            if quality_score < self.thresholds['min_quality_score']:
                cached_data = self._get_cached_data(data_source)
                if cached_data and not self._is_cache_stale(cached_data):
                    # Use cached data instead
                    fallback_used = True
                    issues.append("Using fallback cache data")
                    quality_score = max(quality_score, 75)  # Boost score for cache usage
                    
            # Ensure quality score bounds
            quality_score = max(0.0, min(100.0, quality_score))
            
            # Create report
            report = DataQualityReport(
                timestamp=current_time,
                data_source=data_source,
                quality_score=quality_score,
                issues=issues,
                is_stale=is_stale,
                staleness_seconds=staleness_seconds,
                has_gaps=has_gaps,
                has_nans=has_nans,
                latency_ms=latency_ms,
                fallback_used=fallback_used
            )
            
            # Cache good quality data
            if quality_score >= self.thresholds['min_quality_score'] and not fallback_used:
                self._cache_data(data_source, data, current_time)
                
            # Track quality history
            self._track_quality(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return DataQualityReport(
                timestamp=time.time(),
                data_source=data_source,
                quality_score=0.0,
                issues=[f"Validation error: {str(e)}"],
                is_stale=True,
                staleness_seconds=999,
                has_gaps=True,
                has_nans=True,
                latency_ms=999,
                fallback_used=False
            )
    
    def _detect_nans(self, data: Dict[str, Any]) -> bool:
        """Detect NaN values in market data"""
        try:
            # Check common numeric fields
            numeric_fields = ['current_price', 'volume', 'high', 'low', 'open', 'close']
            
            for field in numeric_fields:
                if field in data:
                    value = data[field]
                    if isinstance(value, (int, float)) and (np.isnan(value) or np.isinf(value)):
                        return True
                    elif isinstance(value, list):
                        if any(np.isnan(x) or np.isinf(x) for x in value if isinstance(x, (int, float))):
                            return True
                            
            # Check OHLCV data if present
            if 'ohlcv' in data:
                ohlcv = data['ohlcv']
                if isinstance(ohlcv, list):
                    for candle in ohlcv:
                        if isinstance(candle, list) and len(candle) >= 5:
                            if any(np.isnan(x) or np.isinf(x) for x in candle[1:6]):  # OHLCV values
                                return True
                                
            return False
            
        except Exception as e:
            logger.warning(f"NaN detection error: {e}")
            return True  # Conservative: assume NaN if error
    
    def _detect_gaps(self, data: Dict[str, Any]) -> Tuple[bool, float]:
        """Detect gaps in time series data"""
        try:
            if 'ohlcv' not in data or not isinstance(data['ohlcv'], list):
                return False, 0.0
                
            ohlcv = data['ohlcv']
            if len(ohlcv) < 10:  # Need minimum data for gap detection
                return False, 0.0
                
            timestamps = [candle[0] for candle in ohlcv if isinstance(candle, list) and len(candle) > 0]
            if len(timestamps) < 10:
                return False, 0.0
                
            # Calculate expected interval (assume 1H timeframe = 3600s)
            intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
            if not intervals:
                return False, 0.0
                
            expected_interval = np.median(intervals)
            
            # Count gaps (intervals significantly larger than expected)
            gaps = sum(1 for interval in intervals if interval > expected_interval * 1.5)
            gap_percentage = (gaps / len(intervals)) * 100
            
            has_gaps = gap_percentage > self.thresholds['max_gap_percentage']
            return has_gaps, gap_percentage
            
        except Exception as e:
            logger.warning(f"Gap detection error: {e}")
            return True, 100.0  # Conservative: assume gaps if error
    
    def _detect_price_jumps(self, data: Dict[str, Any]) -> Tuple[bool, float]:
        """Detect abnormal price jumps"""
        try:
            if 'ohlcv' not in data or not isinstance(data['ohlcv'], list):
                return False, 0.0
                
            ohlcv = data['ohlcv']
            if len(ohlcv) < 5:
                return False, 0.0
                
            closes = []
            for candle in ohlcv:
                if isinstance(candle, list) and len(candle) >= 5:
                    close = candle[4]  # Close price
                    if isinstance(close, (int, float)) and not np.isnan(close):
                        closes.append(close)
                        
            if len(closes) < 5:
                return False, 0.0
                
            # Calculate price changes
            price_changes = []
            for i in range(1, len(closes)):
                if closes[i-1] != 0:
                    change_pct = abs((closes[i] - closes[i-1]) / closes[i-1]) * 100
                    price_changes.append(change_pct)
                    
            if not price_changes:
                return False, 0.0
                
            max_jump = max(price_changes)
            has_jumps = max_jump > self.thresholds['max_price_jump_percentage']
            
            return has_jumps, max_jump
            
        except Exception as e:
            logger.warning(f"Price jump detection error: {e}")
            return False, 0.0
    
    def _detect_volume_anomaly(self, data: Dict[str, Any]) -> bool:
        """Detect volume anomalies"""
        try:
            if 'ohlcv' not in data or not isinstance(data['ohlcv'], list):
                return False
                
            ohlcv = data['ohlcv']
            if len(ohlcv) < 10:
                return False
                
            volumes = []
            for candle in ohlcv:
                if isinstance(candle, list) and len(candle) >= 6:
                    volume = candle[5]  # Volume
                    if isinstance(volume, (int, float)) and volume >= 0:
                        volumes.append(volume)
                        
            if len(volumes) < 10:
                return False
                
            # Check for zero volume periods (suspicious)
            zero_volume_count = sum(1 for v in volumes if v == 0)
            zero_volume_pct = (zero_volume_count / len(volumes)) * 100
            
            if zero_volume_pct > 20:  # More than 20% zero volume
                return True
                
            # Check for extreme volume spikes
            median_volume = np.median(volumes)
            if median_volume > 0:
                max_volume = max(volumes)
                volume_spike = max_volume / median_volume
                if volume_spike > 50:  # 50x spike is suspicious
                    return True
                    
            return False
            
        except Exception as e:
            logger.warning(f"Volume anomaly detection error: {e}")
            return False
    
    def _get_cached_data(self, data_source: str) -> Optional[Dict[str, Any]]:
        """Get cached data for fallback"""
        try:
            if data_source in self.data_cache:
                cached_entry = self.data_cache[data_source]
                if not self._is_cache_stale(cached_entry):
                    return cached_entry['data']
            return None
            
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
            return None
    
    def _is_cache_stale(self, cached_entry: Dict[str, Any]) -> bool:
        """Check if cached data is stale"""
        try:
            cache_age = time.time() - cached_entry.get('timestamp', 0)
            return cache_age > self.cache_ttl
            
        except Exception:
            return True
    
    def _cache_data(self, data_source: str, data: Dict[str, Any], timestamp: float):
        """Cache good quality data"""
        try:
            self.data_cache[data_source] = {
                'data': data.copy(),
                'timestamp': timestamp,
                'quality': 'good'
            }
            
            # Limit cache size
            if len(self.data_cache) > 50:
                # Remove oldest entry
                oldest_key = min(self.data_cache.keys(), 
                               key=lambda k: self.data_cache[k]['timestamp'])
                del self.data_cache[oldest_key]
                
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    def _track_quality(self, report: DataQualityReport):
        """Track quality history for monitoring"""
        try:
            self.quality_history.append({
                'timestamp': report.timestamp,
                'source': report.data_source,
                'quality_score': report.quality_score,
                'issues_count': len(report.issues),
                'is_stale': report.is_stale,
                'latency_ms': report.latency_ms
            })
            
            # Limit history size
            if len(self.quality_history) > self.max_history:
                self.quality_history = self.quality_history[-self.max_history:]
                
        except Exception as e:
            logger.warning(f"Quality tracking error: {e}")
    
    def get_quality_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get data quality summary for specified period"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            recent_reports = [r for r in self.quality_history if r['timestamp'] > cutoff_time]
            
            if not recent_reports:
                return {
                    'period_hours': hours,
                    'total_validations': 0,
                    'avg_quality_score': 0.0,
                    'stale_data_percentage': 0.0,
                    'avg_latency_ms': 0.0,
                    'most_common_issues': []
                }
            
            # Calculate statistics
            quality_scores = [r['quality_score'] for r in recent_reports]
            latencies = [r['latency_ms'] for r in recent_reports]
            stale_count = sum(1 for r in recent_reports if r['is_stale'])
            
            return {
                'period_hours': hours,
                'total_validations': len(recent_reports),
                'avg_quality_score': round(np.mean(quality_scores), 1),
                'min_quality_score': round(min(quality_scores), 1),
                'stale_data_percentage': round((stale_count / len(recent_reports)) * 100, 1),
                'avg_latency_ms': round(np.mean(latencies), 1),
                'max_latency_ms': round(max(latencies), 1),
                'data_sources': len(set(r['source'] for r in recent_reports))
            }
            
        except Exception as e:
            logger.error(f"Quality summary error: {e}")
            return {'error': str(e)}
    
    def should_block_signal(self, quality_report: DataQualityReport) -> Tuple[bool, str]:
        """Determine if signal should be blocked based on data quality"""
        try:
            if quality_report.quality_score < self.thresholds['min_quality_score']:
                return True, f"Data quality too low: {quality_report.quality_score:.1f}/100"
                
            if quality_report.is_stale and quality_report.staleness_seconds > 60:
                return True, f"Data too stale: {quality_report.staleness_seconds:.1f}s old"
                
            if quality_report.has_nans:
                return True, "Data contains NaN values"
                
            if quality_report.latency_ms > 5000:  # 5s is too slow for trading
                return True, f"Data latency too high: {quality_report.latency_ms:.1f}ms"
                
            return False, "Data quality acceptable"
            
        except Exception as e:
            logger.error(f"Signal blocking check error: {e}")
            return True, f"Quality check error: {str(e)}"
    
    def get_fallback_recommendation(self, quality_report: DataQualityReport) -> Dict[str, Any]:
        """Get recommendation for handling poor quality data"""
        try:
            recommendations = []
            actions = []
            
            if quality_report.is_stale:
                recommendations.append("Use cached data if available")
                actions.append("cache_fallback")
                
            if quality_report.has_gaps:
                recommendations.append("Interpolate missing data points")
                actions.append("interpolation")
                
            if quality_report.has_nans:
                recommendations.append("Replace NaN with previous valid values")
                actions.append("nan_replacement")
                
            if quality_report.latency_ms > 2000:
                recommendations.append("Switch to backup data provider")
                actions.append("provider_fallback")
                
            return {
                'quality_score': quality_report.quality_score,
                'recommendations': recommendations,
                'suggested_actions': actions,
                'risk_level': 'high' if quality_report.quality_score < 50 else 'medium' if quality_report.quality_score < 70 else 'low'
            }
            
        except Exception as e:
            logger.error(f"Fallback recommendation error: {e}")
            return {'error': str(e)}