"""
Overfitting Prevention System - Mencegah Model Overfitting
Implementasi comprehensive untuk mencegah overfitting pada ML models
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, accuracy_score

logger = logging.getLogger(__name__)

class ModelHealthStatus(Enum):
    """Status kesehatan model"""
    HEALTHY = "healthy"
    WARNING = "warning"
    OVERFITTED = "overfitted"
    DEGRADED = "degraded"
    CRITICAL = "critical"

@dataclass
class ModelValidationResult:
    """Hasil validasi model"""
    health_status: ModelHealthStatus
    overfitting_score: float
    validation_metrics: Dict[str, float]
    train_metrics: Dict[str, float]
    generalization_gap: float
    recommendations: List[str]
    requires_retraining: bool
    metadata: Dict[str, Any]

class OverfittingPreventionSystem:
    """
    System comprehensive untuk mencegah dan mendeteksi overfitting
    Implementasi validasi out-of-sample, regularization monitoring, dan model drift detection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_history = []
        self.model_performance_history = {}
        
        # Thresholds untuk overfitting detection
        self.thresholds = {
            'generalization_gap_threshold': 0.15,  # 15% gap antara train/val
            'performance_degradation_threshold': 0.10,  # 10% degradasi
            'min_validation_samples': 50,
            'train_val_correlation_threshold': 0.8,
            'stability_window_days': 7,
            'critical_accuracy_drop': 0.20,  # 20% drop = critical
            'overfitting_score_threshold': 0.7
        }
        
        # Configuration untuk validation strategy
        self.validation_config = {
            'time_series_splits': 5,
            'validation_ratio': 0.2,
            'hold_out_ratio': 0.1,
            'rolling_window_validation': True,
            'cross_validation_enabled': True,
            'early_stopping_patience': 10,
            'regularization_monitoring': True
        }
        
        # Regularization techniques configuration
        self.regularization_config = {
            'l1_regularization': True,
            'l2_regularization': True,
            'dropout_monitoring': True,
            'batch_normalization': True,
            'data_augmentation': False,  # Not applicable for time series
            'ensemble_validation': True
        }
        
        logger.info("🔒 Overfitting Prevention System initialized")
    
    def validate_model_health(self, 
                             model_data: Dict[str, Any],
                             train_predictions: List[float],
                             train_actuals: List[float],
                             val_predictions: List[float],
                             val_actuals: List[float],
                             test_predictions: Optional[List[float]] = None,
                             test_actuals: Optional[List[float]] = None) -> ModelValidationResult:
        """
        Comprehensive validation untuk model health dan overfitting detection
        """
        try:
            recommendations = []
            
            # 1. Calculate performance metrics
            train_metrics = self._calculate_metrics(train_predictions, train_actuals)
            val_metrics = self._calculate_metrics(val_predictions, val_actuals)
            
            test_metrics = {}
            if test_predictions and test_actuals:
                test_metrics = self._calculate_metrics(test_predictions, test_actuals)
            
            # 2. Calculate generalization gap
            generalization_gap = self._calculate_generalization_gap(train_metrics, val_metrics)
            
            # 3. Overfitting score calculation
            overfitting_score = self._calculate_overfitting_score(
                train_metrics, val_metrics, test_metrics, model_data
            )
            
            # 4. Model stability analysis
            stability_analysis = self._analyze_model_stability(model_data)
            
            # 5. Performance trend analysis
            trend_analysis = self._analyze_performance_trends(model_data.get('model_id', 'unknown'))
            
            # 6. Generate recommendations
            recommendations = self._generate_recommendations(
                overfitting_score, generalization_gap, stability_analysis, trend_analysis
            )
            
            # 7. Determine health status
            health_status = self._determine_health_status(overfitting_score, generalization_gap, trend_analysis)
            
            # 8. Retraining decision
            requires_retraining = self._should_retrain(health_status, overfitting_score, trend_analysis)
            
            result = ModelValidationResult(
                health_status=health_status,
                overfitting_score=overfitting_score,
                validation_metrics=val_metrics,
                train_metrics=train_metrics,
                generalization_gap=generalization_gap,
                recommendations=recommendations,
                requires_retraining=requires_retraining,
                metadata={
                    'validation_timestamp': datetime.now().isoformat(),
                    'model_id': model_data.get('model_id', 'unknown'),
                    'stability_analysis': stability_analysis,
                    'trend_analysis': trend_analysis,
                    'test_metrics': test_metrics
                }
            )
            
            # Store validation result
            self.validation_history.append(result)
            self._update_model_history(model_data.get('model_id', 'unknown'), result)
            
            logger.info(f"✅ Model validation completed: {health_status.value} status")
            return result
            
        except Exception as e:
            logger.error(f"Error during model validation: {e}")
            return ModelValidationResult(
                health_status=ModelHealthStatus.CRITICAL,
                overfitting_score=1.0,
                validation_metrics={},
                train_metrics={},
                generalization_gap=1.0,
                recommendations=["Model validation failed - immediate attention required"],
                requires_retraining=True,
                metadata={'error': str(e)}
            )
    
    def _calculate_metrics(self, predictions: List[float], actuals: List[float]) -> Dict[str, float]:
        """
        Calculate comprehensive performance metrics
        """
        try:
            if not predictions or not actuals or len(predictions) != len(actuals):
                return {}
            
            predictions = np.array(predictions)
            actuals = np.array(actuals)
            
            # Regression metrics
            mse = mean_squared_error(actuals, predictions)
            rmse = np.sqrt(mse)
            mae = np.mean(np.abs(actuals - predictions))
            
            # R-squared
            ss_res = np.sum((actuals - predictions) ** 2)
            ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100 if np.all(actuals != 0) else 0
            
            # Direction accuracy (for trading)
            direction_actual = np.diff(actuals) > 0
            direction_pred = np.diff(predictions) > 0
            direction_accuracy = np.mean(direction_actual == direction_pred) if len(direction_actual) > 0 else 0
            
            # Volatility metrics
            pred_volatility = np.std(predictions)
            actual_volatility = np.std(actuals)
            volatility_ratio = pred_volatility / actual_volatility if actual_volatility != 0 else 0
            
            return {
                'mse': float(mse),
                'rmse': float(rmse),
                'mae': float(mae),
                'r2': float(r2),
                'mape': float(mape),
                'direction_accuracy': float(direction_accuracy),
                'volatility_ratio': float(volatility_ratio),
                'prediction_std': float(pred_volatility),
                'actual_std': float(actual_volatility)
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}
    
    def _calculate_generalization_gap(self, train_metrics: Dict[str, float], val_metrics: Dict[str, float]) -> float:
        """
        Calculate generalization gap antara training dan validation performance
        """
        try:
            if not train_metrics or not val_metrics:
                return 1.0
            
            # Use R2 as primary metric for generalization gap
            train_r2 = train_metrics.get('r2', 0)
            val_r2 = val_metrics.get('r2', 0)
            
            # Calculate gap (positive = overfitting)
            r2_gap = train_r2 - val_r2
            
            # Also consider direction accuracy gap
            train_dir = train_metrics.get('direction_accuracy', 0)
            val_dir = val_metrics.get('direction_accuracy', 0)
            dir_gap = train_dir - val_dir
            
            # Weighted average of gaps
            generalization_gap = 0.7 * r2_gap + 0.3 * dir_gap
            
            # Normalize to 0-1 scale
            return max(0, min(generalization_gap, 1.0))
            
        except Exception as e:
            logger.error(f"Error calculating generalization gap: {e}")
            return 1.0
    
    def _calculate_overfitting_score(self, 
                                   train_metrics: Dict[str, float],
                                   val_metrics: Dict[str, float],
                                   test_metrics: Dict[str, float],
                                   model_data: Dict[str, Any]) -> float:
        """
        Calculate comprehensive overfitting score (0-1, higher = more overfitted)
        """
        try:
            overfitting_indicators = []
            
            # 1. Generalization gap indicator
            gap = self._calculate_generalization_gap(train_metrics, val_metrics)
            overfitting_indicators.append(gap * 0.4)  # 40% weight
            
            # 2. Training accuracy vs validation accuracy
            train_r2 = train_metrics.get('r2', 0)
            val_r2 = val_metrics.get('r2', 0)
            
            if train_r2 > 0.9 and val_r2 < 0.6:  # High train, low val
                overfitting_indicators.append(0.3)  # Strong overfitting signal
            elif train_r2 > val_r2 + 0.2:  # Significant gap
                overfitting_indicators.append(0.2)
            else:
                overfitting_indicators.append(0.0)
            
            # 3. Volatility consistency
            train_vol_ratio = train_metrics.get('volatility_ratio', 1.0)
            val_vol_ratio = val_metrics.get('volatility_ratio', 1.0)
            vol_inconsistency = abs(train_vol_ratio - val_vol_ratio)
            overfitting_indicators.append(min(vol_inconsistency, 0.2))  # 20% max
            
            # 4. Model complexity indicators
            model_complexity = model_data.get('complexity_score', 0.5)
            if model_complexity > 0.8:  # Very complex model
                overfitting_indicators.append(0.1)
            else:
                overfitting_indicators.append(0.0)
            
            # 5. Test set performance (if available)
            if test_metrics:
                test_r2 = test_metrics.get('r2', 0)
                if val_r2 - test_r2 > 0.15:  # Validation better than test
                    overfitting_indicators.append(0.1)
                else:
                    overfitting_indicators.append(0.0)
            
            # Calculate weighted average
            total_score = sum(overfitting_indicators)
            return min(total_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating overfitting score: {e}")
            return 1.0
    
    def _analyze_model_stability(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze model stability over time
        """
        try:
            stability_analysis = {
                'stability_score': 0.5,
                'performance_variance': 0.0,
                'trend': 'stable',
                'issues': []
            }
            
            # Get recent performance history
            model_id = model_data.get('model_id', 'unknown')
            recent_performances = self._get_recent_performances(model_id)
            
            if len(recent_performances) < 3:
                stability_analysis['issues'].append("Insufficient history for stability analysis")
                return stability_analysis
            
            # Calculate performance variance
            r2_scores = [perf['validation_metrics'].get('r2', 0) for perf in recent_performances]
            performance_variance = np.var(r2_scores)
            stability_analysis['performance_variance'] = float(performance_variance)
            
            # Stability score (lower variance = higher stability)
            if performance_variance < 0.01:
                stability_analysis['stability_score'] = 0.9
                stability_analysis['trend'] = 'very_stable'
            elif performance_variance < 0.05:
                stability_analysis['stability_score'] = 0.7
                stability_analysis['trend'] = 'stable'
            elif performance_variance < 0.1:
                stability_analysis['stability_score'] = 0.5
                stability_analysis['trend'] = 'somewhat_unstable'
            else:
                stability_analysis['stability_score'] = 0.2
                stability_analysis['trend'] = 'unstable'
                stability_analysis['issues'].append("High performance variance detected")
            
            # Trend analysis
            if len(r2_scores) >= 5:
                recent_trend = np.polyfit(range(len(r2_scores)), r2_scores, 1)[0]
                if recent_trend < -0.05:
                    stability_analysis['trend'] = 'declining'
                    stability_analysis['issues'].append("Declining performance trend")
                elif recent_trend > 0.05:
                    stability_analysis['trend'] = 'improving'
            
            return stability_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing model stability: {e}")
            return {'stability_score': 0.0, 'issues': [f"Analysis error: {str(e)}"]}
    
    def _analyze_performance_trends(self, model_id: str) -> Dict[str, Any]:
        """
        Analyze performance trends untuk model drift detection
        """
        try:
            trend_analysis = {
                'drift_detected': False,
                'performance_change': 0.0,
                'trend_direction': 'stable',
                'days_since_peak': 0,
                'recommendations': []
            }
            
            recent_performances = self._get_recent_performances(model_id, days=30)
            
            if len(recent_performances) < 5:
                return trend_analysis
            
            # Calculate performance change over time
            performances = [perf['validation_metrics'].get('r2', 0) for perf in recent_performances]
            
            # Linear trend
            x = np.arange(len(performances))
            slope, intercept = np.polyfit(x, performances, 1)
            
            trend_analysis['performance_change'] = float(slope * len(performances))
            
            # Determine trend direction
            if slope < -0.01:  # Declining trend
                trend_analysis['trend_direction'] = 'declining'
                trend_analysis['drift_detected'] = True
                trend_analysis['recommendations'].append("Model drift detected - consider retraining")
            elif slope > 0.01:  # Improving trend
                trend_analysis['trend_direction'] = 'improving'
            else:
                trend_analysis['trend_direction'] = 'stable'
            
            # Days since peak performance
            if performances:
                peak_idx = np.argmax(performances)
                trend_analysis['days_since_peak'] = len(performances) - peak_idx - 1
                
                if trend_analysis['days_since_peak'] > 14:  # 2 weeks since peak
                    trend_analysis['recommendations'].append("Performance has not improved for 2+ weeks")
            
            # Recent performance drop
            if len(performances) >= 7:
                recent_avg = np.mean(performances[-3:])  # Last 3 days
                older_avg = np.mean(performances[-7:-3])  # Previous 4 days
                
                performance_drop = (older_avg - recent_avg) / older_avg if older_avg > 0 else 0
                
                if performance_drop > self.thresholds['performance_degradation_threshold']:
                    trend_analysis['drift_detected'] = True
                    trend_analysis['recommendations'].append(f"Recent performance drop: {performance_drop:.2%}")
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {'drift_detected': True, 'recommendations': [f"Trend analysis error: {str(e)}"]}
    
    def _generate_recommendations(self, 
                                overfitting_score: float,
                                generalization_gap: float,
                                stability_analysis: Dict[str, Any],
                                trend_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations berdasarkan analysis results
        """
        recommendations = []
        
        try:
            # Overfitting recommendations
            if overfitting_score > self.thresholds['overfitting_score_threshold']:
                recommendations.append("High overfitting detected - implement regularization techniques")
                recommendations.append("Reduce model complexity or increase training data")
                recommendations.append("Apply dropout or early stopping")
            elif overfitting_score > 0.5:
                recommendations.append("Moderate overfitting risk - monitor closely")
                recommendations.append("Consider cross-validation for better generalization")
            
            # Generalization gap recommendations
            if generalization_gap > self.thresholds['generalization_gap_threshold']:
                recommendations.append(f"Large generalization gap ({generalization_gap:.2%}) - review training process")
                recommendations.append("Implement out-of-sample validation")
            
            # Stability recommendations
            stability_score = stability_analysis.get('stability_score', 0.5)
            if stability_score < 0.5:
                recommendations.append("Model stability issues detected")
                recommendations.append("Consider ensemble methods for more stable predictions")
            
            # Trend-based recommendations
            if trend_analysis.get('drift_detected', False):
                recommendations.append("Model drift detected - schedule retraining")
                recommendations.append("Monitor data distribution changes")
            
            # Performance-specific recommendations
            days_since_peak = trend_analysis.get('days_since_peak', 0)
            if days_since_peak > 21:  # 3 weeks
                recommendations.append("Performance stagnation - consider model refresh")
            
            # Add general best practices if no specific issues
            if not recommendations:
                recommendations.append("Model health is good - continue monitoring")
                recommendations.append("Maintain regular validation schedule")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations - manual review required"]
    
    def _determine_health_status(self, 
                               overfitting_score: float,
                               generalization_gap: float,
                               trend_analysis: Dict[str, Any]) -> ModelHealthStatus:
        """
        Determine overall model health status
        """
        try:
            # Critical conditions
            if overfitting_score > 0.9 or generalization_gap > 0.3:
                return ModelHealthStatus.CRITICAL
            
            # Overfitted conditions
            if overfitting_score > self.thresholds['overfitting_score_threshold']:
                return ModelHealthStatus.OVERFITTED
            
            # Degraded conditions
            if trend_analysis.get('drift_detected', False):
                performance_change = trend_analysis.get('performance_change', 0)
                if performance_change < -0.2:  # Significant decline
                    return ModelHealthStatus.DEGRADED
            
            # Warning conditions
            if (overfitting_score > 0.5 or 
                generalization_gap > 0.1 or 
                trend_analysis.get('days_since_peak', 0) > 14):
                return ModelHealthStatus.WARNING
            
            # Healthy
            return ModelHealthStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Error determining health status: {e}")
            return ModelHealthStatus.CRITICAL
    
    def _should_retrain(self, 
                       health_status: ModelHealthStatus,
                       overfitting_score: float,
                       trend_analysis: Dict[str, Any]) -> bool:
        """
        Determine jika model perlu retraining
        """
        try:
            # Critical cases always need retraining
            if health_status in [ModelHealthStatus.CRITICAL, ModelHealthStatus.OVERFITTED]:
                return True
            
            # Degraded performance
            if health_status == ModelHealthStatus.DEGRADED:
                return True
            
            # Drift detection
            if trend_analysis.get('drift_detected', False):
                performance_change = trend_analysis.get('performance_change', 0)
                if performance_change < -0.15:  # 15% decline
                    return True
            
            # Long time since peak
            if trend_analysis.get('days_since_peak', 0) > 30:  # 1 month
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error determining retraining need: {e}")
            return True  # Err on the side of caution
    
    def _get_recent_performances(self, model_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent performance history untuk model
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if model_id not in self.model_performance_history:
                return []
            
            recent_performances = [
                perf for perf in self.model_performance_history[model_id]
                if datetime.fromisoformat(perf['timestamp']) > cutoff_date
            ]
            
            return sorted(recent_performances, key=lambda x: x['timestamp'])
            
        except Exception as e:
            logger.error(f"Error getting recent performances: {e}")
            return []
    
    def _update_model_history(self, model_id: str, validation_result: ModelValidationResult):
        """
        Update model performance history
        """
        try:
            if model_id not in self.model_performance_history:
                self.model_performance_history[model_id] = []
            
            history_entry = {
                'timestamp': validation_result.metadata['validation_timestamp'],
                'health_status': validation_result.health_status.value,
                'overfitting_score': validation_result.overfitting_score,
                'validation_metrics': validation_result.validation_metrics,
                'train_metrics': validation_result.train_metrics,
                'generalization_gap': validation_result.generalization_gap
            }
            
            self.model_performance_history[model_id].append(history_entry)
            
            # Keep only last 100 entries per model
            if len(self.model_performance_history[model_id]) > 100:
                self.model_performance_history[model_id] = self.model_performance_history[model_id][-100:]
            
        except Exception as e:
            logger.error(f"Error updating model history: {e}")
    
    def get_overfitting_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Analytics untuk overfitting prevention performance
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
                'health_distribution': {},
                'avg_overfitting_score': np.mean([val.overfitting_score for val in recent_validations]),
                'avg_generalization_gap': np.mean([val.generalization_gap for val in recent_validations]),
                'retraining_rate': sum(1 for val in recent_validations if val.requires_retraining) / len(recent_validations),
                'models_monitored': len(set(val.metadata.get('model_id', 'unknown') for val in recent_validations))
            }
            
            # Health distribution
            health_statuses = [val.health_status.value for val in recent_validations]
            analytics['health_distribution'] = {status: health_statuses.count(status) for status in set(health_statuses)}
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating overfitting analytics: {e}")
            return {'error': str(e)}

# Create singleton instance  
overfitting_prevention = OverfittingPreventionSystem()