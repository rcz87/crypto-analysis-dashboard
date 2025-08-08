#!/usr/bin/env python3
"""
Data Cleaning & Anomaly Detection Pipeline
Automated ETL untuk data quality assurance
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import IsolationForest
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

@dataclass
class DataQualityReport:
    """Data quality assessment report"""
    total_rows: int
    clean_rows: int
    anomalies_detected: int
    missing_values: int
    duplicates_removed: int
    outliers_fixed: int
    quality_score: float
    issues: List[str]
    recommendations: List[str]

@dataclass
class AnomalyAlert:
    """Anomaly detection alert"""
    timestamp: datetime
    metric: str
    value: float
    z_score: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str

class DataCleaningPipeline:
    """
    Comprehensive data cleaning and anomaly detection pipeline
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.anomaly_threshold = 3.0  # Z-score threshold
        self.isolation_contamination = 0.1  # Expected outlier fraction
        
    def clean_market_data(self, 
                         data: pd.DataFrame,
                         source: str = 'OKX') -> Tuple[pd.DataFrame, DataQualityReport]:
        """
        Clean market data dengan multiple validation steps
        
        Args:
            data: Raw market data
            source: Data source (OKX, Binance, etc)
            
        Returns:
            Cleaned data and quality report
        """
        initial_rows = len(data)
        issues = []
        
        # Step 1: Basic validation
        data = self._validate_schema(data, issues)
        
        # Step 2: Remove duplicates
        duplicates = data.duplicated().sum()
        data = data.drop_duplicates()
        if duplicates > 0:
            issues.append(f"Removed {duplicates} duplicate rows")
        
        # Step 3: Handle missing values
        missing_before = data.isnull().sum().sum()
        data = self._handle_missing_values(data, issues)
        
        # Step 4: Fix data types
        data = self._fix_data_types(data)
        
        # Step 5: Detect and handle outliers
        outliers_fixed = self._handle_outliers(data, issues)
        
        # Step 6: Temporal consistency check
        data = self._check_temporal_consistency(data, issues)
        
        # Step 7: Price/Volume validation
        data = self._validate_price_volume(data, issues)
        
        # Calculate quality score
        clean_rows = len(data)
        quality_score = clean_rows / initial_rows if initial_rows > 0 else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, quality_score)
        
        report = DataQualityReport(
            total_rows=initial_rows,
            clean_rows=clean_rows,
            anomalies_detected=len(issues),
            missing_values=missing_before,
            duplicates_removed=duplicates,
            outliers_fixed=outliers_fixed,
            quality_score=quality_score,
            issues=issues,
            recommendations=recommendations
        )
        
        return data, report
    
    def _validate_schema(self, data: pd.DataFrame, issues: List[str]) -> pd.DataFrame:
        """Validate data schema"""
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        missing_cols = set(required_columns) - set(data.columns)
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
            # Try to fix common naming issues
            data = self._fix_column_names(data)
        
        return data
    
    def _fix_column_names(self, data: pd.DataFrame) -> pd.DataFrame:
        """Fix common column naming issues"""
        column_mapping = {
            'time': 'timestamp',
            'Time': 'timestamp',
            'date': 'timestamp',
            'Date': 'timestamp',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'vol': 'volume'
        }
        
        data = data.rename(columns=column_mapping)
        return data
    
    def _handle_missing_values(self, data: pd.DataFrame, issues: List[str]) -> pd.DataFrame:
        """Handle missing values intelligently"""
        # For price data, forward fill then backward fill
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in data.columns:
                missing = data[col].isnull().sum()
                if missing > 0:
                    data[col] = data[col].fillna(method='ffill').fillna(method='bfill')
                    issues.append(f"Filled {missing} missing values in {col}")
        
        # For volume, use 0 or median
        if 'volume' in data.columns:
            missing = data['volume'].isnull().sum()
            if missing > 0:
                data['volume'] = data['volume'].fillna(data['volume'].median())
                issues.append(f"Filled {missing} missing volume values with median")
        
        return data
    
    def _fix_data_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """Ensure correct data types"""
        # Convert timestamp
        if 'timestamp' in data.columns:
            if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
                data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Convert numeric columns
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        return data
    
    def _handle_outliers(self, data: pd.DataFrame, issues: List[str]) -> int:
        """Detect and handle outliers using multiple methods"""
        outliers_fixed = 0
        
        # Method 1: Z-score for price changes
        if 'close' in data.columns:
            price_changes = data['close'].pct_change().dropna()
            z_scores = np.abs(stats.zscore(price_changes))
            outlier_indices = price_changes.index[z_scores > self.anomaly_threshold]
            
            if len(outlier_indices) > 0:
                # Cap extreme values instead of removing
                for idx in outlier_indices:
                    if idx > 0:
                        data.loc[idx, 'close'] = data.loc[idx-1, 'close'] * 1.1  # Max 10% change
                        outliers_fixed += 1
        
        # Method 2: Isolation Forest for multivariate outliers
        if len(data) > 100:  # Need sufficient data
            features = ['open', 'high', 'low', 'close', 'volume']
            feature_data = data[features].dropna()
            
            if len(feature_data) > 0:
                iso_forest = IsolationForest(
                    contamination=self.isolation_contamination,
                    random_state=42
                )
                outliers = iso_forest.fit_predict(feature_data)
                outlier_count = (outliers == -1).sum()
                
                if outlier_count > 0:
                    issues.append(f"Detected {outlier_count} multivariate outliers")
        
        if outliers_fixed > 0:
            issues.append(f"Fixed {outliers_fixed} price spike outliers")
        
        return outliers_fixed
    
    def _check_temporal_consistency(self, data: pd.DataFrame, issues: List[str]) -> pd.DataFrame:
        """Check temporal consistency of data"""
        if 'timestamp' in data.columns:
            # Sort by timestamp
            data = data.sort_values('timestamp')
            
            # Check for gaps
            time_diff = data['timestamp'].diff()
            expected_freq = time_diff.mode()[0] if len(time_diff.mode()) > 0 else timedelta(hours=1)
            
            gaps = time_diff[time_diff > expected_freq * 2]
            if len(gaps) > 0:
                issues.append(f"Found {len(gaps)} time gaps in data")
        
        return data
    
    def _validate_price_volume(self, data: pd.DataFrame, issues: List[str]) -> pd.DataFrame:
        """Validate price and volume relationships"""
        # OHLC relationship: Low <= Open,Close <= High
        if all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            invalid_ohlc = data[
                (data['low'] > data['open']) | 
                (data['low'] > data['close']) |
                (data['high'] < data['open']) |
                (data['high'] < data['close'])
            ]
            
            if len(invalid_ohlc) > 0:
                # Fix invalid OHLC
                for idx in invalid_ohlc.index:
                    data.loc[idx, 'high'] = max(
                        data.loc[idx, ['open', 'high', 'low', 'close']]
                    )
                    data.loc[idx, 'low'] = min(
                        data.loc[idx, ['open', 'high', 'low', 'close']]
                    )
                issues.append(f"Fixed {len(invalid_ohlc)} invalid OHLC relationships")
        
        # Zero or negative prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col in data.columns:
                invalid = data[data[col] <= 0]
                if len(invalid) > 0:
                    data = data[data[col] > 0]
                    issues.append(f"Removed {len(invalid)} rows with invalid {col} prices")
        
        # Negative volume
        if 'volume' in data.columns:
            negative_vol = data[data['volume'] < 0]
            if len(negative_vol) > 0:
                data.loc[data['volume'] < 0, 'volume'] = 0
                issues.append(f"Fixed {len(negative_vol)} negative volume values")
        
        return data
    
    def _generate_recommendations(self, issues: List[str], quality_score: float) -> List[str]:
        """Generate recommendations based on issues found"""
        recommendations = []
        
        if quality_score < 0.95:
            recommendations.append("Consider using additional data sources for validation")
        
        if any('outlier' in issue for issue in issues):
            recommendations.append("Implement real-time anomaly monitoring")
        
        if any('missing' in issue for issue in issues):
            recommendations.append("Check data source connectivity and completeness")
        
        if any('gap' in issue for issue in issues):
            recommendations.append("Consider implementing data interpolation for gaps")
        
        return recommendations
    
    def detect_market_anomalies(self, 
                               data: pd.DataFrame,
                               metrics: List[str] = ['funding_rate', 'open_interest']) -> List[AnomalyAlert]:
        """
        Detect market anomalies in specific metrics
        
        Args:
            data: Market data with metrics
            metrics: List of metrics to monitor
            
        Returns:
            List of anomaly alerts
        """
        alerts = []
        
        for metric in metrics:
            if metric not in data.columns:
                continue
            
            # Calculate z-scores
            values = data[metric].dropna()
            if len(values) < 20:  # Need sufficient data
                continue
            
            z_scores = np.abs(stats.zscore(values))
            
            # Find anomalies
            anomaly_mask = z_scores > self.anomaly_threshold
            anomaly_indices = values.index[anomaly_mask]
            
            for idx in anomaly_indices:
                z_score = z_scores[values.index == idx][0]
                value = values[idx]
                
                # Determine severity
                if z_score > 5:
                    severity = 'CRITICAL'
                elif z_score > 4:
                    severity = 'HIGH'
                elif z_score > 3.5:
                    severity = 'MEDIUM'
                else:
                    severity = 'LOW'
                
                # Create alert
                alert = AnomalyAlert(
                    timestamp=data.loc[idx, 'timestamp'] if 'timestamp' in data.columns else datetime.now(),
                    metric=metric,
                    value=value,
                    z_score=z_score,
                    severity=severity,
                    description=f"{metric} spike detected: {value:.4f} (Z-score: {z_score:.2f})"
                )
                alerts.append(alert)
        
        return alerts
    
    def create_etl_pipeline(self, 
                           source_config: Dict[str, Any],
                           destination_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create automated ETL pipeline configuration
        
        Args:
            source_config: Source data configuration
            destination_config: Destination configuration
            
        Returns:
            ETL pipeline configuration
        """
        pipeline = {
            'name': 'crypto_data_etl',
            'source': source_config,
            'destination': destination_config,
            'steps': [
                {
                    'name': 'extract',
                    'type': 'data_extraction',
                    'config': {
                        'retry_attempts': 3,
                        'timeout': 30
                    }
                },
                {
                    'name': 'validate',
                    'type': 'schema_validation',
                    'config': {
                        'required_columns': ['timestamp', 'open', 'high', 'low', 'close', 'volume'],
                        'data_types': {
                            'timestamp': 'datetime',
                            'open': 'float',
                            'high': 'float',
                            'low': 'float',
                            'close': 'float',
                            'volume': 'float'
                        }
                    }
                },
                {
                    'name': 'clean',
                    'type': 'data_cleaning',
                    'config': {
                        'remove_duplicates': True,
                        'handle_missing': 'interpolate',
                        'outlier_method': 'isolation_forest'
                    }
                },
                {
                    'name': 'transform',
                    'type': 'feature_engineering',
                    'config': {
                        'add_technical_indicators': True,
                        'normalize_volume': True
                    }
                },
                {
                    'name': 'load',
                    'type': 'data_loading',
                    'config': {
                        'batch_size': 1000,
                        'update_mode': 'append'
                    }
                }
            ],
            'monitoring': {
                'alerts_enabled': True,
                'quality_threshold': 0.95,
                'anomaly_detection': True
            }
        }
        
        return pipeline

# Singleton instance
data_cleaner = DataCleaningPipeline()

if __name__ == "__main__":
    # Test with sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    sample_data = pd.DataFrame({
        'timestamp': dates,
        'open': 50000 + np.random.randn(100) * 1000,
        'high': 51000 + np.random.randn(100) * 1000,
        'low': 49000 + np.random.randn(100) * 1000,
        'close': 50000 + np.random.randn(100) * 1000,
        'volume': 1000000 + np.random.randn(100) * 100000,
        'funding_rate': 0.0001 + np.random.randn(100) * 0.0001
    })
    
    # Add some anomalies
    sample_data.loc[50, 'close'] = 100000  # Price spike
    sample_data.loc[60, 'volume'] = -1000  # Negative volume
    sample_data.loc[70, 'funding_rate'] = 0.01  # Funding spike
    
    # Clean data
    cleaned_data, report = data_cleaner.clean_market_data(sample_data)
    
    print(f"Data Quality Report:")
    print(f"Total rows: {report.total_rows}")
    print(f"Clean rows: {report.clean_rows}")
    print(f"Quality score: {report.quality_score:.2%}")
    print(f"\nIssues found:")
    for issue in report.issues:
        print(f"- {issue}")
    
    # Detect anomalies
    alerts = data_cleaner.detect_market_anomalies(sample_data)
    print(f"\nAnomaly Alerts: {len(alerts)}")
    for alert in alerts:
        print(f"- {alert.description}")