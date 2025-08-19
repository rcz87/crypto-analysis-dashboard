#!/usr/bin/env python3
"""
Self-Improvement Engine - Automatic threshold tuning dan model retraining
ML pipeline untuk continuous improvement dari trade outcomes
"""
import logging
import time
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import pickle
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import os

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.preprocessing import StandardScaler
    import xgboost as xgb
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML libraries not available. Install scikit-learn and xgboost")

logger = logging.getLogger(__name__)

@dataclass
class ThresholdOptimization:
    symbol: str
    timeframe: str
    current_threshold: float
    optimal_threshold: float
    improvement_score: float
    win_rate_before: float
    win_rate_after: float
    profit_factor_before: float
    profit_factor_after: float
    sample_size: int
    confidence: float
    last_updated: float

@dataclass
class ModelPerformance:
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    win_rate_prediction: float
    profit_factor_prediction: float
    training_date: float
    sample_size: int
    feature_importance: Dict[str, float]

class SelfImprovementEngine:
    def __init__(self, data_dir: str = "logs"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Model storage
        self.models_dir = self.data_dir / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        # Current models
        self.confluence_model = None
        self.threshold_model = None
        self.scaler = StandardScaler()
        
        # Optimization history
        self.optimization_history = []
        self.model_performance_history = []
        
        # Tuning parameters
        self.tuning_config = {
            'min_sample_size': 30,           # Minimum trades untuk tuning
            'retraining_interval_hours': 24,  # Retrain setiap 24 jam
            'threshold_step_size': 0.05,     # 5% step untuk threshold tuning
            'max_threshold': 95.0,           # Max threshold 95%
            'min_threshold': 40.0,           # Min threshold 40%
            'validation_split': 0.2,        # 20% untuk validation
        }
        
        # Feature weights untuk confluence scoring
        self.current_weights = {
            'smc_score': 0.40,
            'orderbook_score': 0.20,
            'volatility_score': 0.10,
            'momentum_score': 0.15,
            'funding_score': 0.10,
            'news_score': 0.05
        }
        
        # Load existing models and history
        self._load_models()
        self._load_optimization_history()
        
        logger.info("Self-Improvement Engine initialized")
    
    def retrain_confluence_model(self, force_retrain: bool = False) -> ModelPerformance:
        """
        Retrain confluence scoring model dari logged trade data
        """
        try:
            if not ML_AVAILABLE:
                raise Exception("ML libraries not available")
            
            # Check if retraining needed
            if not force_retrain and not self._should_retrain():
                logger.info("Model retraining not needed yet")
                return self._get_current_model_performance()
            
            # Load training data
            training_data = self._load_training_data()
            if len(training_data) < self.tuning_config['min_sample_size']:
                raise Exception(f"Insufficient training data: {len(training_data)} < {self.tuning_config['min_sample_size']}")
            
            # Prepare features and targets
            X, y = self._prepare_training_data(training_data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.tuning_config['validation_split'], 
                random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train multiple models
            models = self._train_multiple_models(X_train_scaled, y_train)
            
            # Evaluate and select best model
            best_model, performance = self._evaluate_models(models, X_test_scaled, y_test, X_test)
            
            # Update confluence model
            self.confluence_model = best_model
            
            # Update feature weights based on importance
            self._update_feature_weights(performance.feature_importance)
            
            # Save model and performance
            self._save_models()
            self._save_performance_record(performance)
            
            logger.info(f"Model retrained successfully. Accuracy: {performance.accuracy:.3f}")
            
            return performance
            
        except Exception as e:
            logger.error(f"Model retraining error: {e}")
            return self._get_fallback_performance()
    
    def optimize_thresholds(self, symbol: str, timeframe: str = "1H") -> ThresholdOptimization:
        """
        Optimize confluence thresholds untuk specific symbol/timeframe
        """
        try:
            # Load trade history for symbol
            trade_data = self._load_symbol_trades(symbol, timeframe)
            
            if len(trade_data) < self.tuning_config['min_sample_size']:
                raise Exception(f"Insufficient trade data for {symbol}: {len(trade_data)} trades")
            
            # Current performance baseline
            current_threshold = self._get_current_threshold(symbol, timeframe)
            baseline_metrics = self._calculate_performance_metrics(trade_data, current_threshold)
            
            # Test different thresholds
            best_threshold = current_threshold
            best_metrics = baseline_metrics
            best_score = self._calculate_optimization_score(baseline_metrics)
            
            threshold_range = np.arange(
                self.tuning_config['min_threshold'],
                self.tuning_config['max_threshold'] + self.tuning_config['threshold_step_size'],
                self.tuning_config['threshold_step_size']
            )
            
            for test_threshold in threshold_range:
                if abs(test_threshold - current_threshold) < 0.01:  # Skip current
                    continue
                    
                test_metrics = self._calculate_performance_metrics(trade_data, test_threshold)
                test_score = self._calculate_optimization_score(test_metrics)
                
                if test_score > best_score:
                    best_threshold = test_threshold
                    best_metrics = test_metrics
                    best_score = test_score
            
            # Calculate improvement
            improvement_score = ((best_score - self._calculate_optimization_score(baseline_metrics)) 
                               / self._calculate_optimization_score(baseline_metrics)) * 100
            
            # Create optimization record
            optimization = ThresholdOptimization(
                symbol=symbol,
                timeframe=timeframe,
                current_threshold=current_threshold,
                optimal_threshold=best_threshold,
                improvement_score=improvement_score,
                win_rate_before=baseline_metrics['win_rate'],
                win_rate_after=best_metrics['win_rate'],
                profit_factor_before=baseline_metrics['profit_factor'],
                profit_factor_after=best_metrics['profit_factor'],
                sample_size=len(trade_data),
                confidence=self._calculate_confidence(len(trade_data)),
                last_updated=time.time()
            )
            
            # Save optimization
            self._save_threshold_optimization(optimization)
            
            # Apply if significant improvement
            if improvement_score > 5.0 and optimization.confidence > 0.7:
                self._apply_threshold_change(symbol, timeframe, best_threshold)
                logger.info(f"Threshold optimized for {symbol}: {current_threshold:.1f} → {best_threshold:.1f} (+{improvement_score:.1f}%)")
            
            return optimization
            
        except Exception as e:
            logger.error(f"Threshold optimization error: {e}")
            return self._get_fallback_optimization(symbol, timeframe)
    
    def get_improved_confluence_score(self, features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate improved confluence score using trained model
        """
        try:
            if not self.confluence_model or not ML_AVAILABLE:
                # Fallback to weighted average
                return self._calculate_weighted_score(features)
            
            # Prepare feature vector
            feature_vector = self._features_to_vector(features)
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            # Get prediction
            if hasattr(self.confluence_model, 'predict_proba'):
                # Probability-based score
                probabilities = self.confluence_model.predict_proba(feature_vector_scaled)[0]
                confidence_score = probabilities[1] * 100  # Probability of positive outcome
            else:
                # Decision-based score  
                decision = self.confluence_model.predict(feature_vector_scaled)[0]
                confidence_score = 75.0 if decision == 1 else 25.0
            
            # Get feature importance explanation
            explanation = self._explain_prediction(features, confidence_score)
            
            return confidence_score, explanation
            
        except Exception as e:
            logger.warning(f"Improved scoring error: {e}")
            return self._calculate_weighted_score(features)
    
    def auto_tune_system(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Automatic system tuning untuk multiple symbols
        """
        try:
            if symbols is None:
                symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT']
            
            results = {
                'tuning_timestamp': time.time(),
                'symbols_processed': [],
                'optimizations': [],
                'model_retraining': None,
                'summary': {}
            }
            
            # 1. Retrain confluence model
            try:
                model_performance = self.retrain_confluence_model()
                results['model_retraining'] = asdict(model_performance)
                logger.info("Model retraining completed")
            except Exception as e:
                logger.warning(f"Model retraining failed: {e}")
                results['model_retraining'] = {'error': str(e)}
            
            # 2. Optimize thresholds per symbol
            total_improvements = 0
            significant_improvements = 0
            
            for symbol in symbols:
                try:
                    optimization = self.optimize_thresholds(symbol, "1H")
                    results['optimizations'].append(asdict(optimization))
                    results['symbols_processed'].append(symbol)
                    
                    total_improvements += optimization.improvement_score
                    if optimization.improvement_score > 5.0:
                        significant_improvements += 1
                        
                except Exception as e:
                    logger.warning(f"Threshold optimization failed for {symbol}: {e}")
                    results['optimizations'].append({
                        'symbol': symbol,
                        'error': str(e)
                    })
            
            # 3. Summary
            results['summary'] = {
                'symbols_tuned': len(results['symbols_processed']),
                'avg_improvement': total_improvements / max(len(symbols), 1),
                'significant_improvements': significant_improvements,
                'model_accuracy': results['model_retraining'].get('accuracy', 0) if results['model_retraining'] and 'error' not in results['model_retraining'] else 0,
                'next_tuning_due': time.time() + (self.tuning_config['retraining_interval_hours'] * 3600)
            }
            
            logger.info(f"Auto-tuning completed. Avg improvement: {results['summary']['avg_improvement']:.1f}%")
            
            return results
            
        except Exception as e:
            logger.error(f"Auto-tuning error: {e}")
            return {'error': str(e), 'timestamp': time.time()}
    
    def get_improvement_status(self) -> Dict[str, Any]:
        """
        Get current improvement system status
        """
        try:
            # Recent optimizations
            recent_opts = [opt for opt in self.optimization_history 
                          if time.time() - opt.get('last_updated', 0) < 86400]  # 24h
            
            # Model performance
            current_performance = self._get_current_model_performance()
            
            # Next tuning due
            last_retrain = max([p.training_date for p in self.model_performance_history], default=0)
            next_retrain_due = last_retrain + (self.tuning_config['retraining_interval_hours'] * 3600)
            
            return {
                'system_status': 'operational' if ML_AVAILABLE else 'limited_functionality',
                'model_performance': asdict(current_performance),
                'recent_optimizations': len(recent_opts),
                'avg_recent_improvement': np.mean([opt.get('improvement_score', 0) for opt in recent_opts]) if recent_opts else 0,
                'current_feature_weights': self.current_weights.copy(),
                'next_retraining_due': next_retrain_due,
                'hours_until_retrain': max(0, (next_retrain_due - time.time()) / 3600),
                'ml_libraries_available': ML_AVAILABLE,
                'total_training_samples': self._count_training_samples()
            }
            
        except Exception as e:
            logger.error(f"Improvement status error: {e}")
            return {'error': str(e)}
    
    def _should_retrain(self) -> bool:
        """Check if model retraining is due"""
        try:
            if not self.model_performance_history:
                return True
                
            last_training = max([p.training_date for p in self.model_performance_history])
            hours_since = (time.time() - last_training) / 3600
            
            return hours_since >= self.tuning_config['retraining_interval_hours']
            
        except Exception:
            return True
    
    def _load_training_data(self) -> List[Dict[str, Any]]:
        """Load training data from trade logs"""
        try:
            # Load from trade logger JSONL files
            training_data = []
            
            log_files = list(self.data_dir.glob("trade_*.jsonl"))
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            if line.strip():
                                trade_record = json.loads(line.strip())
                                if self._is_complete_training_record(trade_record):
                                    training_data.append(trade_record)
                except Exception as e:
                    logger.warning(f"Error reading {log_file}: {e}")
                    
            return training_data
            
        except Exception as e:
            logger.error(f"Training data loading error: {e}")
            return []
    
    def _is_complete_training_record(self, record: Dict[str, Any]) -> bool:
        """Check if trade record is complete for training"""
        required_fields = ['outcome', 'signal_score', 'smc_score', 'orderbook_score']
        return (record.get('outcome') in ['win', 'loss'] and
                all(field in record for field in required_fields))
    
    def _prepare_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and targets for ML training"""
        try:
            features = []
            targets = []
            
            for record in training_data:
                # Extract features
                feature_vector = [
                    record.get('smc_score', 0),
                    record.get('orderbook_score', 0),
                    record.get('volatility_score', 0),
                    record.get('momentum_score', 0),
                    record.get('funding_score', 0),
                    record.get('news_score', 0),
                    record.get('signal_score', 0),
                    record.get('risk_reward_ratio', 0),
                    record.get('position_size_usd', 0) / 1000,  # Normalize
                    record.get('market_regime_score', 50) / 100  # Normalize
                ]
                
                # Target: 1 for win, 0 for loss
                target = 1 if record['outcome'] == 'win' else 0
                
                features.append(feature_vector)
                targets.append(target)
            
            return np.array(features), np.array(targets)
            
        except Exception as e:
            logger.error(f"Training data preparation error: {e}")
            return np.array([]), np.array([])
    
    def _train_multiple_models(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Train multiple ML models"""
        models = {}
        
        try:
            # Logistic Regression
            models['logistic'] = LogisticRegression(random_state=42)
            models['logistic'].fit(X_train, y_train)
            
            # Random Forest
            models['random_forest'] = RandomForestClassifier(
                n_estimators=100, random_state=42, max_depth=10
            )
            models['random_forest'].fit(X_train, y_train)
            
            # XGBoost (if available)
            if 'xgb' in globals():
                models['xgboost'] = xgb.XGBClassifier(
                    n_estimators=100, random_state=42, max_depth=6
                )
                models['xgboost'].fit(X_train, y_train)
                
        except Exception as e:
            logger.error(f"Model training error: {e}")
            
        return models
    
    def _evaluate_models(self, models: Dict[str, Any], X_test: np.ndarray, 
                        y_test: np.ndarray, X_test_original: np.ndarray) -> Tuple[Any, ModelPerformance]:
        """Evaluate models and select best one"""
        try:
            best_model = None
            best_performance = None
            best_score = 0
            
            for model_name, model in models.items():
                try:
                    # Predictions
                    y_pred = model.predict(X_test)
                    
                    # Metrics
                    accuracy = np.mean(y_pred == y_test)
                    
                    # Cross-validation score
                    cv_scores = cross_val_score(model, X_test, y_test, cv=3)
                    cv_mean = np.mean(cv_scores)
                    
                    # Feature importance
                    if hasattr(model, 'feature_importances_'):
                        importance = model.feature_importances_
                    elif hasattr(model, 'coef_'):
                        importance = np.abs(model.coef_[0])
                    else:
                        importance = np.ones(X_test.shape[1]) / X_test.shape[1]
                    
                    feature_names = ['smc', 'orderbook', 'volatility', 'momentum', 'funding', 'news', 'signal', 'rr', 'size', 'regime']
                    feature_importance = dict(zip(feature_names, importance))
                    
                    # Create performance record
                    performance = ModelPerformance(
                        model_name=model_name,
                        accuracy=accuracy,
                        precision=accuracy,  # Simplified
                        recall=accuracy,     # Simplified
                        f1_score=accuracy,   # Simplified
                        win_rate_prediction=np.mean(y_pred),
                        profit_factor_prediction=1.5,  # Estimated
                        training_date=time.time(),
                        sample_size=len(y_test),
                        feature_importance=feature_importance
                    )
                    
                    # Score model (combination of accuracy and CV)
                    model_score = (accuracy * 0.7) + (cv_mean * 0.3)
                    
                    if model_score > best_score:
                        best_score = model_score
                        best_model = model
                        best_performance = performance
                        
                except Exception as e:
                    logger.warning(f"Model evaluation error for {model_name}: {e}")
                    continue
            
            if best_model is None:
                raise Exception("No models successfully evaluated")
                
            return best_model, best_performance
            
        except Exception as e:
            logger.error(f"Model evaluation error: {e}")
            # Return fallback
            return models.get('logistic'), self._get_fallback_performance()
    
    def _calculate_weighted_score(self, features: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """Fallback weighted score calculation"""
        try:
            score = 0.0
            for feature_name, weight in self.current_weights.items():
                feature_value = features.get(feature_name, 0)
                score += feature_value * weight
            
            explanation = {
                'method': 'weighted_average',
                'weights_used': self.current_weights,
                'feature_contributions': {
                    name: features.get(name, 0) * weight 
                    for name, weight in self.current_weights.items()
                }
            }
            
            return score, explanation
            
        except Exception as e:
            logger.error(f"Weighted score calculation error: {e}")
            return 50.0, {'error': str(e)}
    
    def _save_models(self):
        """Save trained models"""
        try:
            if self.confluence_model:
                model_file = self.models_dir / "confluence_model.pkl"
                with open(model_file, 'wb') as f:
                    pickle.dump(self.confluence_model, f)
                    
            # Save scaler
            scaler_file = self.models_dir / "scaler.pkl"
            with open(scaler_file, 'wb') as f:
                pickle.dump(self.scaler, f)
                
            # Save weights
            weights_file = self.models_dir / "feature_weights.json"
            with open(weights_file, 'w') as f:
                json.dump(self.current_weights, f, indent=2)
                
        except Exception as e:
            logger.error(f"Model saving error: {e}")
    
    def _load_models(self):
        """Load existing models"""
        try:
            model_file = self.models_dir / "confluence_model.pkl" 
            if model_file.exists():
                with open(model_file, 'rb') as f:
                    self.confluence_model = pickle.load(f)
                    
            scaler_file = self.models_dir / "scaler.pkl"
            if scaler_file.exists():
                with open(scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)
                    
            weights_file = self.models_dir / "feature_weights.json"
            if weights_file.exists():
                with open(weights_file, 'r') as f:
                    self.current_weights = json.load(f)
                    
        except Exception as e:
            logger.warning(f"Model loading error: {e}")
    
    def _get_fallback_performance(self) -> ModelPerformance:
        """Get fallback performance when training fails"""
        return ModelPerformance(
            model_name="fallback",
            accuracy=0.5,
            precision=0.5,
            recall=0.5,
            f1_score=0.5,
            win_rate_prediction=0.5,
            profit_factor_prediction=1.0,
            training_date=time.time(),
            sample_size=0,
            feature_importance={}
        )
    
    def _count_training_samples(self) -> int:
        """Count available training samples"""
        try:
            return len(self._load_training_data())
        except:
            return 0
    
    def _features_to_vector(self, features: Dict[str, float]) -> List[float]:
        """Convert feature dict to vector"""
        return [
            features.get('smc_score', 0),
            features.get('orderbook_score', 0), 
            features.get('volatility_score', 0),
            features.get('momentum_score', 0),
            features.get('funding_score', 0),
            features.get('news_score', 0),
            features.get('signal_score', 0),
            features.get('risk_reward_ratio', 0),
            features.get('position_size_usd', 1000) / 1000,
            features.get('market_regime_score', 50) / 100
        ]
    
    def _get_current_model_performance(self) -> ModelPerformance:
        """Get current model performance"""
        if self.model_performance_history:
            return self.model_performance_history[-1]
        return self._get_fallback_performance()
    
    def _save_performance_record(self, performance: ModelPerformance):
        """Save performance record"""
        try:
            self.model_performance_history.append(performance)
            
            # Save to file
            perf_file = self.models_dir / "performance_history.json"
            with open(perf_file, 'w') as f:
                json.dump([asdict(p) for p in self.model_performance_history], f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Performance record saving error: {e}")
    
    def _load_optimization_history(self):
        """Load optimization history"""
        try:
            opt_file = self.data_dir / "threshold_optimizations.json"
            if opt_file.exists():
                with open(opt_file, 'r') as f:
                    self.optimization_history = json.load(f)
        except Exception as e:
            logger.warning(f"Optimization history loading error: {e}")
    
    def _get_fallback_optimization(self, symbol: str, timeframe: str) -> ThresholdOptimization:
        """Get fallback optimization result"""
        return ThresholdOptimization(
            symbol=symbol,
            timeframe=timeframe,
            current_threshold=60.0,
            optimal_threshold=60.0,
            improvement_score=0.0,
            win_rate_before=0.5,
            win_rate_after=0.5,
            profit_factor_before=1.0,
            profit_factor_after=1.0,
            sample_size=0,
            confidence=0.0,
            last_updated=time.time()
        )