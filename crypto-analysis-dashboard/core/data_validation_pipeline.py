"""
Advanced Data Validation Pipeline - Mengatasi Data Quality & Bias Issues
Pipeline comprehensive untuk cleaning, validating, dan filtering data crypto
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DataQualityLevel(Enum):
    """Level kualitas data"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    REJECTED = "rejected"

@dataclass
class DataValidationResult:
    """Hasil validasi data"""
    is_valid: bool
    quality_level: DataQualityLevel
    confidence_score: float
    issues_found: List[str]
    cleaned_data: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]

class AdvancedDataValidator:
    """
    Validator sophisticated untuk data cryptocurrency
    Mendeteksi noise, manipulation, anomalies, dan bias
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_history = []
        self.anomaly_patterns = {}
        self.manipulation_indicators = {}
        
        # Thresholds untuk detection
        self.thresholds = {
            'price_spike_threshold': 0.20,  # 20% spike dalam 1 menit
            'volume_anomaly_threshold': 5.0,  # 5x volume normal
            'funding_rate_extreme': 0.005,   # 0.5% funding rate
            'liquidation_cascade_threshold': 100,  # $100M liquidations
            'wash_trading_correlation': 0.95,
            'pump_dump_velocity': 0.15,      # 15% dalam 5 menit
            'min_data_points': 10,
            'max_outlier_ratio': 0.05        # 5% outliers maksimal
        }
        
        # Patterns manipulation yang dikenal
        self.manipulation_patterns = {
            'pump_and_dump': {
                'rapid_price_increase': True,
                'volume_spike': True,
                'followed_by_dump': True,
                'social_media_hype': True
            },
            'wash_trading': {
                'high_volume_low_movement': True,
                'repetitive_patterns': True,
                'cross_exchange_correlation': True
            },
            'liquidation_hunting': {
                'price_spikes_to_liquidation_levels': True,
                'immediate_reversal': True,
                'low_volume_move': True
            },
            'stop_hunting': {
                'brief_spike_below_support': True,
                'immediate_recovery': True,
                'pattern_repetition': True
            }
        }
        
        logger.info("🔍 Advanced Data Validation Pipeline initialized")
    
    def validate_market_data(self, 
                            price_data: Dict[str, Any],
                            volume_data: Dict[str, Any],
                            additional_data: Optional[Dict[str, Any]] = None) -> DataValidationResult:
        """
        Validasi comprehensive untuk market data
        """
        try:
            issues_found = []
            confidence_score = 1.0
            cleaned_data = {}
            
            # 1. Basic Data Quality Checks
            basic_issues = self._validate_basic_quality(price_data, volume_data)
            issues_found.extend(basic_issues)
            if basic_issues:
                confidence_score -= 0.2
            
            # 2. Price Anomaly Detection
            price_anomalies = self._detect_price_anomalies(price_data)
            if price_anomalies:
                issues_found.extend(price_anomalies)
                confidence_score -= 0.3
            
            # 3. Volume Validation
            volume_issues = self._validate_volume_data(volume_data)
            if volume_issues:
                issues_found.extend(volume_issues)
                confidence_score -= 0.2
            
            # 4. Manipulation Detection
            manipulation_score = self._detect_market_manipulation(price_data, volume_data)
            if manipulation_score > 0.7:
                issues_found.append(f"High manipulation probability: {manipulation_score:.2f}")
                confidence_score -= 0.4
            
            # 5. Cross-Validation dengan multiple sources
            if additional_data:
                cross_val_issues = self._cross_validate_sources(price_data, additional_data)
                if cross_val_issues:
                    issues_found.extend(cross_val_issues)
                    confidence_score -= 0.15
            
            # 6. Temporal Consistency Check
            temporal_issues = self._check_temporal_consistency(price_data)
            if temporal_issues:
                issues_found.extend(temporal_issues)
                confidence_score -= 0.1
            
            # Clean data jika diperlukan
            if issues_found:
                cleaned_data = self._clean_problematic_data(price_data, volume_data, issues_found)
            else:
                cleaned_data = {'price_data': price_data, 'volume_data': volume_data}
            
            # Determine quality level
            quality_level = self._determine_quality_level(confidence_score, issues_found)
            is_valid = quality_level != DataQualityLevel.REJECTED
            
            result = DataValidationResult(
                is_valid=is_valid,
                quality_level=quality_level,
                confidence_score=max(0.0, confidence_score),
                issues_found=issues_found,
                cleaned_data=cleaned_data if is_valid else None,
                metadata={
                    'validation_timestamp': datetime.now().isoformat(),
                    'data_source': price_data.get('source', 'unknown'),
                    'validation_version': '1.0'
                }
            )
            
            # Store for pattern learning
            self.validation_history.append(result)
            
            logger.info(f"✅ Data validation completed: {quality_level.value} quality")
            return result
            
        except Exception as e:
            logger.error(f"Error during data validation: {e}")
            return DataValidationResult(
                is_valid=False,
                quality_level=DataQualityLevel.REJECTED,
                confidence_score=0.0,
                issues_found=[f"Validation error: {str(e)}"],
                cleaned_data=None,
                metadata={'error': str(e)}
            )
    
    def _validate_basic_quality(self, price_data: Dict[str, Any], volume_data: Dict[str, Any]) -> List[str]:
        """
        Validasi kualitas dasar data
        """
        issues = []
        
        try:
            # Check for missing data
            if not price_data.get('prices'):
                issues.append("Missing price data")
            
            if not volume_data.get('volumes'):
                issues.append("Missing volume data")
            
            # Check data length consistency
            price_count = len(price_data.get('prices', []))
            volume_count = len(volume_data.get('volumes', []))
            
            if abs(price_count - volume_count) > 2:
                issues.append(f"Price/volume data length mismatch: {price_count} vs {volume_count}")
            
            # Check for minimum data points
            if price_count < self.thresholds['min_data_points']:
                issues.append(f"Insufficient data points: {price_count} < {self.thresholds['min_data_points']}")
            
            # Check for null values
            prices = price_data.get('prices', [])
            if prices:
                null_count = sum(1 for p in prices if p is None or np.isnan(float(p)) if p is not None)
                if null_count > 0:
                    issues.append(f"Found {null_count} null price values")
            
            # Check for negative values
            if prices:
                negative_count = sum(1 for p in prices if p is not None and float(p) < 0)
                if negative_count > 0:
                    issues.append(f"Found {negative_count} negative price values")
            
            return issues
            
        except Exception as e:
            return [f"Basic validation error: {str(e)}"]
    
    def _detect_price_anomalies(self, price_data: Dict[str, Any]) -> List[str]:
        """
        Deteksi anomali pada price data
        """
        anomalies = []
        
        try:
            prices = [float(p) for p in price_data.get('prices', []) if p is not None]
            timestamps = price_data.get('timestamps', [])
            
            if len(prices) < 3:
                return anomalies
            
            # Calculate price changes
            price_changes = []
            for i in range(1, len(prices)):
                change = (prices[i] - prices[i-1]) / prices[i-1]
                price_changes.append(change)
            
            # Detect extreme spikes
            for i, change in enumerate(price_changes):
                if abs(change) > self.thresholds['price_spike_threshold']:
                    anomalies.append(f"Extreme price spike detected: {change:.2%} at index {i+1}")
            
            # Detect statistical outliers using IQR
            if len(price_changes) > 4:
                q1 = np.percentile(price_changes, 25)
                q3 = np.percentile(price_changes, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = [i for i, change in enumerate(price_changes) 
                           if change < lower_bound or change > upper_bound]
                
                outlier_ratio = len(outliers) / len(price_changes)
                if outlier_ratio > self.thresholds['max_outlier_ratio']:
                    anomalies.append(f"High outlier ratio: {outlier_ratio:.2%}")
            
            # Detect impossible price movements (gaps)
            for i in range(1, len(prices)):
                price_ratio = prices[i] / prices[i-1]
                if price_ratio > 2.0 or price_ratio < 0.5:  # 100% up or 50% down
                    anomalies.append(f"Impossible price gap: {price_ratio:.2f}x at index {i}")
            
            return anomalies
            
        except Exception as e:
            return [f"Price anomaly detection error: {str(e)}"]
    
    def _validate_volume_data(self, volume_data: Dict[str, Any]) -> List[str]:
        """
        Validasi volume data untuk deteksi wash trading dll
        """
        issues = []
        
        try:
            volumes = [float(v) for v in volume_data.get('volumes', []) if v is not None]
            
            if len(volumes) < 3:
                return issues
            
            # Check for negative volumes
            negative_volumes = sum(1 for v in volumes if v < 0)
            if negative_volumes > 0:
                issues.append(f"Found {negative_volumes} negative volume values")
            
            # Detect volume anomalies
            mean_volume = np.mean(volumes)
            for i, volume in enumerate(volumes):
                if volume > mean_volume * self.thresholds['volume_anomaly_threshold']:
                    issues.append(f"Volume spike detected: {volume:.2f} vs avg {mean_volume:.2f}")
            
            # Check for zero volume periods
            zero_volumes = sum(1 for v in volumes if v == 0)
            zero_ratio = zero_volumes / len(volumes)
            if zero_ratio > 0.1:  # 10% zero volumes
                issues.append(f"High zero volume ratio: {zero_ratio:.2%}")
            
            # Volume consistency check
            volume_std = np.std(volumes)
            volume_cv = volume_std / mean_volume if mean_volume > 0 else 0
            if volume_cv > 5.0:  # Very high coefficient of variation
                issues.append(f"Extremely volatile volume pattern: CV = {volume_cv:.2f}")
            
            return issues
            
        except Exception as e:
            return [f"Volume validation error: {str(e)}"]
    
    def _detect_market_manipulation(self, price_data: Dict[str, Any], volume_data: Dict[str, Any]) -> float:
        """
        Deteksi manipulation patterns menggunakan multiple indicators
        Returns manipulation probability score (0-1)
        """
        try:
            manipulation_score = 0.0
            indicators_checked = 0
            
            prices = [float(p) for p in price_data.get('prices', []) if p is not None]
            volumes = [float(v) for v in volume_data.get('volumes', []) if v is not None]
            
            if len(prices) < 5 or len(volumes) < 5:
                return 0.0
            
            # 1. Pump and Dump Detection
            price_changes = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            volume_changes = [(volumes[i] - volumes[i-1]) / volumes[i-1] for i in range(1, min(len(volumes), len(prices)))]
            
            # Look for rapid price increase with volume spike followed by dump
            for i in range(2, len(price_changes)):
                rapid_increase = price_changes[i-1] > 0.1 and price_changes[i-2] > 0.05  # 10% then 5%
                volume_spike = i-1 < len(volume_changes) and volume_changes[i-1] > 2.0  # 200% volume increase
                followed_by_dump = price_changes[i] < -0.05  # 5% drop
                
                if rapid_increase and volume_spike and followed_by_dump:
                    manipulation_score += 0.4
                    indicators_checked += 1
                    break
            
            # 2. Wash Trading Detection
            # Look for high volume with minimal price movement
            total_volume = sum(volumes)
            price_range = max(prices) - min(prices)
            avg_price = np.mean(prices)
            relative_range = price_range / avg_price
            
            if total_volume > 0 and relative_range < 0.02:  # Less than 2% price movement
                volume_to_movement_ratio = total_volume / relative_range
                if volume_to_movement_ratio > 1000000:  # Arbitrary threshold
                    manipulation_score += 0.3
                    indicators_checked += 1
            
            # 3. Stop Hunting Detection
            # Look for brief spikes that immediately reverse
            for i in range(2, len(prices)-1):
                spike_down = (prices[i] - prices[i-1]) / prices[i-1] < -0.03  # 3% down
                immediate_recovery = (prices[i+1] - prices[i]) / prices[i] > 0.025  # 2.5% recovery
                
                if spike_down and immediate_recovery:
                    manipulation_score += 0.2
                    indicators_checked += 1
                    break
            
            # 4. Liquidation Cascade Detection
            # Look for cascading price movements with specific patterns
            cascade_moves = 0
            for i in range(1, len(price_changes)):
                if abs(price_changes[i]) > 0.05:  # 5% move
                    cascade_moves += 1
            
            if cascade_moves > len(price_changes) * 0.3:  # 30% of moves are large
                manipulation_score += 0.25
                indicators_checked += 1
            
            # Normalize score
            if indicators_checked > 0:
                manipulation_score = min(manipulation_score, 1.0)
            
            return manipulation_score
            
        except Exception as e:
            logger.error(f"Error detecting manipulation: {e}")
            return 0.0
    
    def _cross_validate_sources(self, primary_data: Dict[str, Any], additional_data: Dict[str, Any]) -> List[str]:
        """
        Cross-validate data dengan multiple sources
        """
        issues = []
        
        try:
            primary_prices = [float(p) for p in primary_data.get('prices', []) if p is not None]
            additional_prices = [float(p) for p in additional_data.get('prices', []) if p is not None]
            
            if len(primary_prices) < 3 or len(additional_prices) < 3:
                return issues
            
            # Compare price trends
            min_length = min(len(primary_prices), len(additional_prices))
            primary_subset = primary_prices[:min_length]
            additional_subset = additional_prices[:min_length]
            
            # Calculate correlation
            if len(primary_subset) > 1:
                correlation = np.corrcoef(primary_subset, additional_subset)[0, 1]
                if correlation < 0.8:  # Low correlation between sources
                    issues.append(f"Low correlation between data sources: {correlation:.2f}")
            
            # Check for significant price differences
            price_differences = []
            for i in range(min_length):
                diff = abs(primary_subset[i] - additional_subset[i]) / primary_subset[i]
                price_differences.append(diff)
            
            avg_diff = np.mean(price_differences)
            if avg_diff > 0.05:  # 5% average difference
                issues.append(f"High price discrepancy between sources: {avg_diff:.2%}")
            
            return issues
            
        except Exception as e:
            return [f"Cross-validation error: {str(e)}"]
    
    def _check_temporal_consistency(self, price_data: Dict[str, Any]) -> List[str]:
        """
        Check temporal consistency of timestamps
        """
        issues = []
        
        try:
            timestamps = price_data.get('timestamps', [])
            
            if len(timestamps) < 2:
                return issues
            
            # Check for chronological order
            for i in range(1, len(timestamps)):
                if timestamps[i] <= timestamps[i-1]:
                    issues.append(f"Non-chronological timestamps at index {i}")
                    break
            
            # Check for gaps in data
            time_diffs = []
            for i in range(1, len(timestamps)):
                if isinstance(timestamps[i], str):
                    curr_time = datetime.fromisoformat(timestamps[i].replace('Z', '+00:00'))
                    prev_time = datetime.fromisoformat(timestamps[i-1].replace('Z', '+00:00'))
                else:
                    curr_time = datetime.fromtimestamp(timestamps[i])
                    prev_time = datetime.fromtimestamp(timestamps[i-1])
                
                diff = (curr_time - prev_time).total_seconds()
                time_diffs.append(diff)
            
            if time_diffs:
                median_diff = np.median(time_diffs)
                for i, diff in enumerate(time_diffs):
                    if diff > median_diff * 5:  # 5x longer than median
                        issues.append(f"Large time gap detected: {diff:.0f}s at index {i+1}")
            
            return issues
            
        except Exception as e:
            return [f"Temporal consistency error: {str(e)}"]
    
    def _clean_problematic_data(self, price_data: Dict[str, Any], volume_data: Dict[str, Any], issues: List[str]) -> Dict[str, Any]:
        """
        Clean data berdasarkan issues yang ditemukan
        """
        try:
            cleaned_price_data = price_data.copy()
            cleaned_volume_data = volume_data.copy()
            
            prices = [float(p) for p in price_data.get('prices', []) if p is not None]
            volumes = [float(v) for v in volume_data.get('volumes', []) if v is not None]
            
            # Remove outliers using IQR method
            if len(prices) > 4:
                q1 = np.percentile(prices, 25)
                q3 = np.percentile(prices, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                cleaned_prices = []
                cleaned_volumes = []
                
                for i, price in enumerate(prices):
                    if lower_bound <= price <= upper_bound:
                        cleaned_prices.append(price)
                        if i < len(volumes):
                            cleaned_volumes.append(volumes[i])
                
                cleaned_price_data['prices'] = cleaned_prices
                cleaned_volume_data['volumes'] = cleaned_volumes
            
            # Add cleaning metadata
            cleaning_metadata = {
                'original_length': len(prices),
                'cleaned_length': len(cleaned_price_data.get('prices', [])),
                'issues_addressed': issues,
                'cleaning_timestamp': datetime.now().isoformat()
            }
            
            return {
                'price_data': cleaned_price_data,
                'volume_data': cleaned_volume_data,
                'cleaning_metadata': cleaning_metadata
            }
            
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            return {'price_data': price_data, 'volume_data': volume_data}
    
    def _determine_quality_level(self, confidence_score: float, issues: List[str]) -> DataQualityLevel:
        """
        Determine overall quality level berdasarkan confidence score dan issues
        """
        if confidence_score >= 0.9 and len(issues) == 0:
            return DataQualityLevel.EXCELLENT
        elif confidence_score >= 0.7 and len(issues) <= 2:
            return DataQualityLevel.GOOD
        elif confidence_score >= 0.5 and len(issues) <= 5:
            return DataQualityLevel.FAIR
        elif confidence_score >= 0.3:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.REJECTED
    
    def get_validation_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Analytics untuk validation performance
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_validations = [
                val for val in self.validation_history 
                if datetime.fromisoformat(val.metadata['validation_timestamp']) > cutoff_date
            ]
            
            if not recent_validations:
                return {'message': 'No validations in the specified period'}
            
            analytics = {
                'total_validations': len(recent_validations),
                'quality_distribution': {},
                'avg_confidence': np.mean([val.confidence_score for val in recent_validations]),
                'rejection_rate': 0,
                'common_issues': {}
            }
            
            # Quality distribution
            qualities = [val.quality_level.value for val in recent_validations]
            analytics['quality_distribution'] = {quality: qualities.count(quality) for quality in set(qualities)}
            
            # Rejection rate
            rejections = sum(1 for val in recent_validations if not val.is_valid)
            analytics['rejection_rate'] = rejections / len(recent_validations)
            
            # Common issues
            all_issues = []
            for val in recent_validations:
                all_issues.extend(val.issues_found)
            
            analytics['common_issues'] = {
                issue: all_issues.count(issue) 
                for issue in set(all_issues)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating validation analytics: {e}")
            return {'error': str(e)}

# Create singleton instance
data_validator = AdvancedDataValidator()