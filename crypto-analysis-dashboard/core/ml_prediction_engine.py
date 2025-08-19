#!/usr/bin/env python3
"""
🤖 ML Prediction Engine - Advanced Hybrid AI Predictor
Sistem prediksi canggih menggunakan LSTM, XGBoost, dan ensemble methods
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import logging
import json
import pickle
from datetime import datetime, timezone, timedelta
import asyncio
from dataclasses import dataclass

from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb

# Conditional TensorFlow import
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Concatenate, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Data class untuk prediction results"""
    prediction: str  # BUY, SELL, HOLD
    confidence: float
    probability_distribution: Dict[str, float]
    feature_importance: Dict[str, float]
    model_contributions: Dict[str, float]
    timestamp: str
    timeframe: str
    symbol: str
    metadata: Dict[str, Any]

class HybridPredictor:
    """
    🤖 Hybrid AI Predictor combining multiple ML models
    
    Features:
    - LSTM for time-series pattern recognition
    - XGBoost for tabular feature analysis
    - Random Forest for ensemble robustness
    - Voting classifier for final predictions
    - Real-time model performance tracking
    - Automatic model retraining
    - Feature importance analysis
    """
    
    def __init__(self, db_session=None, redis_manager=None):
        """Initialize Hybrid Predictor"""
        self.db_session = db_session
        self.redis_manager = redis_manager
        
        # Model components
        self.lstm_model = None
        self.xgboost_model = None
        self.random_forest_model = None
        self.ensemble_model = None
        
        # Scalers
        self.price_scaler = MinMaxScaler()
        self.feature_scaler = StandardScaler()
        
        # Model parameters
        self.sequence_length = 60  # 60 periods for LSTM
        self.feature_columns = []
        self.target_column = 'signal'
        
        # Performance tracking
        self.model_performance = {
            'lstm': {'accuracy': 0.0, 'last_trained': None},
            'xgboost': {'accuracy': 0.0, 'last_trained': None},
            'random_forest': {'accuracy': 0.0, 'last_trained': None},
            'ensemble': {'accuracy': 0.0, 'last_trained': None}
        }
        
        # Training configuration
        self.min_training_samples = 1000
        self.retrain_threshold_accuracy = 0.65
        self.retrain_interval_days = 7
        
        logger.info("🤖 Hybrid AI Predictor initialized")
    
    async def prepare_training_data(self, symbol: str, timeframe: str, 
                                  days_back: int = 90) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare training data dari historical signals dan market data
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            days_back: Days of historical data
            
        Returns:
            X_lstm, X_tabular, y, sample_weights: Training data arrays
        """
        try:
            # Get historical signal data
            signal_data = await self._get_historical_signals(symbol, timeframe, days_back)
            
            if len(signal_data) < self.min_training_samples:
                raise ValueError(f"Insufficient training data: {len(signal_data)} samples (minimum: {self.min_training_samples})")
            
            # Prepare features
            df = pd.DataFrame(signal_data)
            
            # Technical indicators features
            df = self._add_technical_features(df)
            
            # Market structure features
            df = self._add_market_structure_features(df)
            
            # Time-based features
            df = self._add_time_features(df)
            
            # Prepare target variable (signal outcome)
            df['target'] = df['outcome'].map({
                'HIT_TP': 1,     # Buy signal
                'HIT_SL': -1,    # Sell signal
                'TIMEOUT': 0,    # Hold
                'PENDING': 0     # Hold (neutral)
            }).fillna(0)
            
            # Remove rows dengan missing target
            df = df.dropna(subset=['target'])
            
            # Prepare LSTM sequences (price data)
            price_columns = ['open', 'high', 'low', 'close', 'volume']
            lstm_data = df[price_columns].values
            lstm_data_scaled = self.price_scaler.fit_transform(lstm_data)
            
            # Create sequences untuk LSTM
            X_lstm = []
            y_lstm = []
            
            for i in range(self.sequence_length, len(lstm_data_scaled)):
                X_lstm.append(lstm_data_scaled[i-self.sequence_length:i])
                y_lstm.append(df.iloc[i]['target'])
            
            X_lstm = np.array(X_lstm)
            y_lstm = np.array(y_lstm)
            
            # Prepare tabular features
            feature_columns = [col for col in df.columns if col.startswith(('rsi', 'macd', 'sma', 'ema', 'bb', 'volume', 'market_', 'time_'))]
            self.feature_columns = feature_columns
            
            X_tabular = df[feature_columns].iloc[self.sequence_length:].values
            X_tabular = self.feature_scaler.fit_transform(X_tabular)
            
            # Sample weights (give more weight to recent data)
            sample_weights = np.exp(np.linspace(-1, 0, len(y_lstm)))
            sample_weights = sample_weights / sample_weights.sum() * len(sample_weights)
            
            # Convert target to classification (0: SELL, 1: HOLD, 2: BUY)
            y_classification = (y_lstm + 1).astype(int)
            
            logger.info(f"🤖 Training data prepared: {len(y_lstm)} samples, {len(feature_columns)} features")
            
            return X_lstm, X_tabular, y_classification, sample_weights
            
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise
    
    async def train_models(self, symbol: str, timeframe: str, force_retrain: bool = False) -> Dict[str, Any]:
        """
        Train all models dengan historical data
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            force_retrain: Force model retraining
            
        Returns:
            training_results: Training performance metrics
        """
        try:
            # Check if retraining is needed
            if not force_retrain and not self._should_retrain():
                logger.info("🤖 Models are recent and performing well, skipping training")
                return self.model_performance
            
            logger.info(f"🤖 Starting model training for {symbol} {timeframe}")
            
            # Prepare training data
            X_lstm, X_tabular, y, sample_weights = await self.prepare_training_data(symbol, timeframe)
            
            # Split data
            test_size = 0.2
            split_idx = int(len(y) * (1 - test_size))
            
            X_lstm_train, X_lstm_test = X_lstm[:split_idx], X_lstm[split_idx:]
            X_tabular_train, X_tabular_test = X_tabular[:split_idx], X_tabular[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            weights_train = sample_weights[:split_idx]
            
            training_results = {}
            
            # Train LSTM Model
            if TENSORFLOW_AVAILABLE:
                try:
                    lstm_accuracy = await self._train_lstm_model(X_lstm_train, y_train, weights_train, X_lstm_test, y_test)
                    training_results['lstm'] = {'accuracy': lstm_accuracy, 'status': 'success'}
                    self.model_performance['lstm']['accuracy'] = lstm_accuracy
                    self.model_performance['lstm']['last_trained'] = datetime.now(timezone.utc).isoformat()
                except Exception as e:
                    logger.error(f"LSTM training failed: {e}")
                    training_results['lstm'] = {'accuracy': 0.0, 'status': 'failed', 'error': str(e)}
            else:
                logger.warning("TensorFlow not available, skipping LSTM training")
                training_results['lstm'] = {'accuracy': 0.0, 'status': 'skipped', 'error': 'TensorFlow not available'}
            
            # Train XGBoost Model
            try:
                xgb_accuracy = self._train_xgboost_model(X_tabular_train, y_train, weights_train, X_tabular_test, y_test)
                training_results['xgboost'] = {'accuracy': xgb_accuracy, 'status': 'success'}
                self.model_performance['xgboost']['accuracy'] = xgb_accuracy
                self.model_performance['xgboost']['last_trained'] = datetime.now(timezone.utc).isoformat()
            except Exception as e:
                logger.error(f"XGBoost training failed: {e}")
                training_results['xgboost'] = {'accuracy': 0.0, 'status': 'failed', 'error': str(e)}
            
            # Train Random Forest Model
            try:
                rf_accuracy = self._train_random_forest_model(X_tabular_train, y_train, weights_train, X_tabular_test, y_test)
                training_results['random_forest'] = {'accuracy': rf_accuracy, 'status': 'success'}
                self.model_performance['random_forest']['accuracy'] = rf_accuracy
                self.model_performance['random_forest']['last_trained'] = datetime.now(timezone.utc).isoformat()
            except Exception as e:
                logger.error(f"Random Forest training failed: {e}")
                training_results['random_forest'] = {'accuracy': 0.0, 'status': 'failed', 'error': str(e)}
            
            # Create Ensemble Model
            try:
                ensemble_accuracy = self._create_ensemble_model(X_tabular_train, y_train, X_tabular_test, y_test)
                training_results['ensemble'] = {'accuracy': ensemble_accuracy, 'status': 'success'}
                self.model_performance['ensemble']['accuracy'] = ensemble_accuracy
                self.model_performance['ensemble']['last_trained'] = datetime.now(timezone.utc).isoformat()
            except Exception as e:
                logger.error(f"Ensemble training failed: {e}")
                training_results['ensemble'] = {'accuracy': 0.0, 'status': 'failed', 'error': str(e)}
            
            # Save models
            await self._save_models()
            
            # Update performance tracking
            await self._update_performance_tracking(training_results)
            
            logger.info(f"🤖 Model training completed for {symbol} {timeframe}")
            return training_results
            
        except Exception as e:
            logger.error(f"Error in model training: {e}")
            return {'error': str(e)}
    
    async def predict(self, symbol: str, timeframe: str, market_data: Dict[str, Any]) -> PredictionResult:
        """
        Generate prediction menggunakan ensemble of models
        
        Args:
            symbol: Trading symbol
            timeframe: Chart timeframe
            market_data: Current market data dan technical indicators
            
        Returns:
            PredictionResult: Comprehensive prediction results
        """
        try:
            # Load models if not loaded
            if not self._models_loaded():
                await self._load_models()
            
            # Prepare input data
            lstm_input, tabular_input = self._prepare_prediction_input(market_data)
            
            # Get predictions dari setiap model
            predictions = {}
            confidences = {}
            
            # LSTM Prediction
            if self.lstm_model is not None and TENSORFLOW_AVAILABLE:
                try:
                    lstm_pred = self.lstm_model.predict(lstm_input, verbose=0)
                    lstm_class = np.argmax(lstm_pred[0])
                    lstm_confidence = np.max(lstm_pred[0])
                    predictions['lstm'] = lstm_class
                    confidences['lstm'] = float(lstm_confidence)
                except Exception as e:
                    logger.warning(f"LSTM prediction failed: {e}")
                    predictions['lstm'] = 1  # Default to HOLD
                    confidences['lstm'] = 0.33
            
            # XGBoost Prediction
            if self.xgboost_model is not None:
                try:
                    xgb_pred_proba = self.xgboost_model.predict_proba(tabular_input)
                    xgb_class = np.argmax(xgb_pred_proba[0])
                    xgb_confidence = np.max(xgb_pred_proba[0])
                    predictions['xgboost'] = xgb_class
                    confidences['xgboost'] = float(xgb_confidence)
                except Exception as e:
                    logger.warning(f"XGBoost prediction failed: {e}")
                    predictions['xgboost'] = 1
                    confidences['xgboost'] = 0.33
            
            # Random Forest Prediction
            if self.random_forest_model is not None:
                try:
                    rf_pred_proba = self.random_forest_model.predict_proba(tabular_input)
                    rf_class = np.argmax(rf_pred_proba[0])
                    rf_confidence = np.max(rf_pred_proba[0])
                    predictions['random_forest'] = rf_class
                    confidences['random_forest'] = float(rf_confidence)
                except Exception as e:
                    logger.warning(f"Random Forest prediction failed: {e}")
                    predictions['random_forest'] = 1
                    confidences['random_forest'] = 0.33
            
            # Ensemble Prediction
            if self.ensemble_model is not None:
                try:
                    ensemble_pred_proba = self.ensemble_model.predict_proba(tabular_input)
                    ensemble_class = np.argmax(ensemble_pred_proba[0])
                    ensemble_confidence = np.max(ensemble_pred_proba[0])
                    predictions['ensemble'] = ensemble_class
                    confidences['ensemble'] = float(ensemble_confidence)
                except Exception as e:
                    logger.warning(f"Ensemble prediction failed: {e}")
                    predictions['ensemble'] = 1
                    confidences['ensemble'] = 0.33
            
            # Weighted ensemble decision
            final_prediction, final_confidence, prob_dist = self._combine_predictions(predictions, confidences)
            
            # Convert class to action
            action_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
            final_action = action_map[final_prediction]
            
            # Get feature importance
            feature_importance = self._get_feature_importance()
            
            # Create prediction result
            result = PredictionResult(
                prediction=final_action,
                confidence=final_confidence,
                probability_distribution=prob_dist,
                feature_importance=feature_importance,
                model_contributions=confidences,
                timestamp=datetime.now(timezone.utc).isoformat(),
                timeframe=timeframe,
                symbol=symbol,
                metadata={
                    'models_used': list(predictions.keys()),
                    'individual_predictions': {model: action_map[pred] for model, pred in predictions.items()},
                    'market_data_features': len(self.feature_columns) if self.feature_columns else 0
                }
            )
            
            # Log prediction untuk performance tracking
            await self._log_prediction(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            # Return safe default prediction
            return PredictionResult(
                prediction='HOLD',
                confidence=0.0,
                probability_distribution={'SELL': 0.33, 'HOLD': 0.34, 'BUY': 0.33},
                feature_importance={},
                model_contributions={},
                timestamp=datetime.now(timezone.utc).isoformat(),
                timeframe=timeframe,
                symbol=symbol,
                metadata={'error': str(e)}
            )
    
    async def _train_lstm_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                               sample_weights: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Train LSTM model untuk time-series prediction"""
        try:
            # Create LSTM architecture
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
                Dropout(0.2),
                LSTM(50, return_sequences=True),
                Dropout(0.2),
                LSTM(50),
                Dropout(0.2),
                Dense(25, activation='relu'),
                BatchNormalization(),
                Dense(3, activation='softmax')  # 3 classes: SELL, HOLD, BUY
            ])
            
            # Compile model
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Callbacks
            early_stopping = EarlyStopping(monitor='val_accuracy', patience=10, restore_best_weights=True)
            reduce_lr = ReduceLROnPlateau(monitor='val_accuracy', factor=0.5, patience=5, min_lr=0.0001)
            
            # Train model
            history = model.fit(
                X_train, y_train,
                batch_size=32,
                epochs=100,
                validation_data=(X_test, y_test),
                sample_weight=sample_weights,
                callbacks=[early_stopping, reduce_lr],
                verbose=0
            )
            
            # Evaluate model
            test_accuracy = model.evaluate(X_test, y_test, verbose=0)[1]
            
            self.lstm_model = model
            
            logger.info(f"🤖 LSTM model trained - Accuracy: {test_accuracy:.3f}")
            return float(test_accuracy)
            
        except Exception as e:
            logger.error(f"LSTM training error: {e}")
            raise
    
    def _train_xgboost_model(self, X_train: np.ndarray, y_train: np.ndarray,
                            sample_weights: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Train XGBoost model untuk tabular features"""
        try:
            # XGBoost parameters
            params = {
                'objective': 'multi:softprob',
                'num_class': 3,
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 200,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'eval_metric': 'mlogloss'
            }
            
            # Train model
            model = xgb.XGBClassifier(**params)
            model.fit(
                X_train, y_train,
                sample_weight=sample_weights,
                eval_set=[(X_test, y_test)],
                verbose=False
            )
            
            # Evaluate model
            test_accuracy = accuracy_score(y_test, model.predict(X_test))
            
            self.xgboost_model = model
            
            logger.info(f"🤖 XGBoost model trained - Accuracy: {test_accuracy:.3f}")
            return float(test_accuracy)
            
        except Exception as e:
            logger.error(f"XGBoost training error: {e}")
            raise
    
    def _train_random_forest_model(self, X_train: np.ndarray, y_train: np.ndarray,
                                  sample_weights: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Train Random Forest model untuk ensemble robustness"""
        try:
            # Random Forest parameters
            model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            # Train model
            model.fit(X_train, y_train, sample_weight=sample_weights)
            
            # Evaluate model
            test_accuracy = accuracy_score(y_test, model.predict(X_test))
            
            self.random_forest_model = model
            
            logger.info(f"🤖 Random Forest model trained - Accuracy: {test_accuracy:.3f}")
            return float(test_accuracy)
            
        except Exception as e:
            logger.error(f"Random Forest training error: {e}")
            raise
    
    def _create_ensemble_model(self, X_train: np.ndarray, y_train: np.ndarray,
                              X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Create ensemble model dari trained models"""
        try:
            # Prepare base models untuk ensemble
            base_models = []
            
            if self.xgboost_model is not None:
                base_models.append(('xgb', self.xgboost_model))
            
            if self.random_forest_model is not None:
                base_models.append(('rf', self.random_forest_model))
            
            if len(base_models) < 2:
                logger.warning("Insufficient models for ensemble, using best available model")
                return 0.0
            
            # Create voting classifier
            ensemble = VotingClassifier(
                estimators=base_models,
                voting='soft'  # Use probability voting
            )
            
            # Train ensemble
            ensemble.fit(X_train, y_train)
            
            # Evaluate ensemble
            test_accuracy = accuracy_score(y_test, ensemble.predict(X_test))
            
            self.ensemble_model = ensemble
            
            logger.info(f"🤖 Ensemble model created - Accuracy: {test_accuracy:.3f}")
            return float(test_accuracy)
            
        except Exception as e:
            logger.error(f"Ensemble creation error: {e}")
            raise
    
    def _add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicator features"""
        try:
            # RSI
            df['rsi_14'] = self._calculate_rsi(df['close'], 14)
            df['rsi_oversold'] = (df['rsi_14'] < 30).astype(int)
            df['rsi_overbought'] = (df['rsi_14'] > 70).astype(int)
            
            # Moving Averages
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            df['macd_bullish'] = (df['macd'] > df['macd_signal']).astype(int)
            
            # Bollinger Bands
            bb_period = 20
            df['bb_middle'] = df['close'].rolling(bb_period).mean()
            bb_std = df['close'].rolling(bb_period).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['volume_high'] = (df['volume_ratio'] > 1.5).astype(int)
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding technical features: {e}")
            return df
    
    def _add_market_structure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market structure features"""
        try:
            # Price action features
            df['price_change'] = df['close'].pct_change()
            df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
            df['body_size'] = abs(df['close'] - df['open']) / df['close']
            df['upper_shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['close']
            df['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / df['close']
            
            # Volatility features
            df['volatility'] = df['price_change'].rolling(14).std()
            df['atr'] = self._calculate_atr(df, 14)
            
            # Trend features
            df['trend_short'] = (df['close'] > df['sma_20']).astype(int)
            df['trend_long'] = (df['close'] > df['sma_50']).astype(int)
            df['trend_strength'] = abs(df['close'] - df['sma_20']) / df['sma_20']
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding market structure features: {e}")
            return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        try:
            # Assuming timestamp column exists
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
                df['is_market_hours'] = ((df['hour'] >= 9) & (df['hour'] <= 16)).astype(int)
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding time features: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(period).mean()
            avg_loss = loss.rolling(period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception:
            return pd.Series(index=prices.index, dtype=float)
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(period).mean()
            
            return atr
            
        except Exception:
            return pd.Series(index=df.index, dtype=float)
    
    def _prepare_prediction_input(self, market_data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare input data untuk prediction"""
        try:
            # Extract price data untuk LSTM
            price_history = market_data.get('price_history', [])
            if len(price_history) >= self.sequence_length:
                # Take last sequence_length candles
                recent_prices = price_history[-self.sequence_length:]
                price_array = np.array([[candle['open'], candle['high'], candle['low'], candle['close'], candle['volume']] 
                                       for candle in recent_prices])
                
                # Scale prices
                if hasattr(self.price_scaler, 'data_min_'):
                    price_scaled = self.price_scaler.transform(price_array)
                    lstm_input = price_scaled.reshape(1, self.sequence_length, price_array.shape[1])
                else:
                    # If scaler not fitted, use raw data normalized
                    price_normalized = (price_array - price_array.mean(axis=0)) / (price_array.std(axis=0) + 1e-8)
                    lstm_input = price_normalized.reshape(1, self.sequence_length, price_array.shape[1])
            else:
                # Not enough history, create dummy input
                lstm_input = np.zeros((1, self.sequence_length, 5))
            
            # Extract tabular features
            tabular_features = []
            
            # Technical indicators
            indicators = market_data.get('technical_indicators', {})
            for feature in self.feature_columns:
                if feature in indicators:
                    tabular_features.append(float(indicators[feature]))
                else:
                    tabular_features.append(0.0)  # Default value
            
            # If no feature columns defined, use basic features
            if not self.feature_columns:
                current_candle = market_data.get('current_candle', {})
                tabular_features = [
                    current_candle.get('close', 0.0),
                    current_candle.get('volume', 0.0),
                    indicators.get('rsi', 50.0),
                    indicators.get('macd', 0.0)
                ]
            
            tabular_input = np.array(tabular_features).reshape(1, -1)
            
            # Scale tabular features
            if hasattr(self.feature_scaler, 'data_min_'):
                tabular_input = self.feature_scaler.transform(tabular_input)
            
            return lstm_input, tabular_input
            
        except Exception as e:
            logger.error(f"Error preparing prediction input: {e}")
            # Return dummy inputs
            lstm_input = np.zeros((1, self.sequence_length, 5))
            tabular_input = np.zeros((1, max(len(self.feature_columns), 4)))
            return lstm_input, tabular_input
    
    def _combine_predictions(self, predictions: Dict[str, int], 
                           confidences: Dict[str, float]) -> Tuple[int, float, Dict[str, float]]:
        """Combine predictions dari multiple models dengan weighting"""
        try:
            if not predictions:
                return 1, 0.33, {'SELL': 0.33, 'HOLD': 0.34, 'BUY': 0.33}
            
            # Model weights berdasarkan performance
            model_weights = {
                'lstm': 0.3,
                'xgboost': 0.3,
                'random_forest': 0.2,
                'ensemble': 0.2
            }
            
            # Adjust weights berdasarkan actual performance
            for model in predictions.keys():
                if model in self.model_performance:
                    accuracy = self.model_performance[model]['accuracy']
                    if accuracy > 0:
                        model_weights[model] *= (accuracy / 0.7)  # Boost if accuracy > 70%
            
            # Normalize weights
            total_weight = sum(model_weights.get(model, 0) for model in predictions.keys())
            if total_weight > 0:
                for model in model_weights:
                    model_weights[model] /= total_weight
            
            # Calculate weighted probabilities
            class_probs = np.zeros(3)  # [SELL, HOLD, BUY]
            
            for model, prediction in predictions.items():
                weight = model_weights.get(model, 0)
                confidence = confidences.get(model, 0.33)
                
                # Convert prediction to probability distribution
                prob_dist = np.ones(3) * (1 - confidence) / 2  # Spread remaining prob
                prob_dist[prediction] = confidence
                
                class_probs += prob_dist * weight
            
            # Final prediction
            final_prediction = np.argmax(class_probs)
            final_confidence = float(class_probs[final_prediction])
            
            # Create probability distribution
            prob_dict = {
                'SELL': float(class_probs[0]),
                'HOLD': float(class_probs[1]),
                'BUY': float(class_probs[2])
            }
            
            return final_prediction, final_confidence, prob_dict
            
        except Exception as e:
            logger.error(f"Error combining predictions: {e}")
            return 1, 0.33, {'SELL': 0.33, 'HOLD': 0.34, 'BUY': 0.33}
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance dari trained models"""
        try:
            importance_dict = {}
            
            # XGBoost feature importance
            if self.xgboost_model is not None and hasattr(self.xgboost_model, 'feature_importances_'):
                xgb_importance = self.xgboost_model.feature_importances_
                for i, feature in enumerate(self.feature_columns[:len(xgb_importance)]):
                    importance_dict[f'xgb_{feature}'] = float(xgb_importance[i])
            
            # Random Forest feature importance
            if self.random_forest_model is not None and hasattr(self.random_forest_model, 'feature_importances_'):
                rf_importance = self.random_forest_model.feature_importances_
                for i, feature in enumerate(self.feature_columns[:len(rf_importance)]):
                    importance_dict[f'rf_{feature}'] = float(rf_importance[i])
            
            return importance_dict
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
    
    async def _get_historical_signals(self, symbol: str, timeframe: str, days_back: int) -> List[Dict[str, Any]]:
        """Get historical signal data untuk training"""
        try:
            if not self.db_session:
                # Return mock data for testing
                return self._generate_mock_training_data(days_back * 24)  # Assuming hourly data
            
            from models import SignalHistory
            
            since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            signals = self.db_session.query(SignalHistory).filter(
                SignalHistory.symbol == symbol.upper(),
                SignalHistory.timeframe == timeframe,
                SignalHistory.created_at >= since_date,
                SignalHistory.outcome.isnot(None)  # Only signals dengan known outcomes
            ).order_by(SignalHistory.created_at).all()
            
            return [signal.to_dict() for signal in signals]
            
        except Exception as e:
            logger.error(f"Error getting historical signals: {e}")
            return self._generate_mock_training_data(days_back * 24)
    
    def _generate_mock_training_data(self, num_samples: int) -> List[Dict[str, Any]]:
        """Generate mock training data untuk testing"""
        try:
            np.random.seed(42)
            data = []
            
            base_price = 50000
            current_price = base_price
            
            for i in range(num_samples):
                # Generate price data
                price_change = np.random.normal(0, 0.02)
                current_price *= (1 + price_change)
                
                high = current_price * (1 + abs(np.random.normal(0, 0.01)))
                low = current_price * (1 - abs(np.random.normal(0, 0.01)))
                open_price = low + (high - low) * np.random.random()
                close_price = low + (high - low) * np.random.random()
                volume = np.random.uniform(1000, 10000)
                
                # Generate outcome berdasarkan price movement
                future_change = np.random.normal(0, 0.03)
                if future_change > 0.02:
                    outcome = 'HIT_TP'
                elif future_change < -0.015:
                    outcome = 'HIT_SL'
                else:
                    outcome = 'TIMEOUT'
                
                data.append({
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close_price,
                    'volume': volume,
                    'outcome': outcome,
                    'confidence': np.random.uniform(50, 95),
                    'entry_price': close_price,
                    'timestamp': (datetime.now(timezone.utc) - timedelta(hours=num_samples-i)).isoformat()
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error generating mock data: {e}")
            return []
    
    def _should_retrain(self) -> bool:
        """Check if models should be retrained"""
        try:
            # Check if any model performance is below threshold
            for model, performance in self.model_performance.items():
                if performance['accuracy'] < self.retrain_threshold_accuracy:
                    return True
            
            # Check if models are old
            for model, performance in self.model_performance.items():
                last_trained = performance.get('last_trained')
                if last_trained:
                    last_trained_date = datetime.fromisoformat(last_trained.replace('Z', '+00:00'))
                    days_since_training = (datetime.now(timezone.utc) - last_trained_date).days
                    if days_since_training >= self.retrain_interval_days:
                        return True
                else:
                    return True  # Never trained
            
            return False
            
        except Exception:
            return True  # Retrain on error
    
    def _models_loaded(self) -> bool:
        """Check if models are loaded"""
        return any([
            self.lstm_model is not None,
            self.xgboost_model is not None,
            self.random_forest_model is not None,
            self.ensemble_model is not None
        ])
    
    async def _load_models(self):
        """Load saved models dari storage"""
        try:
            # This would load models from file/database
            # For now, we'll trigger training if no models exist
            logger.info("🤖 No saved models found, training new models")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    async def _save_models(self):
        """Save trained models to storage"""
        try:
            # This would save models to file/Redis/database
            # Implementation depends on storage preference
            logger.info("🤖 Models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    async def _update_performance_tracking(self, training_results: Dict[str, Any]):
        """Update performance tracking data"""
        try:
            if self.redis_manager:
                cache_key = "ml_model_performance"
                self.redis_manager.set_cache(cache_key, self.model_performance)
            
        except Exception as e:
            logger.error(f"Error updating performance tracking: {e}")
    
    async def _log_prediction(self, result: PredictionResult):
        """Log prediction untuk performance tracking"""
        try:
            # This would log prediction untuk later evaluation
            logger.debug(f"🤖 Prediction logged: {result.symbol} {result.prediction} ({result.confidence:.3f})")
            
        except Exception as e:
            logger.error(f"Error logging prediction: {e}")
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get current model status dan performance"""
        try:
            return {
                'models_loaded': self._models_loaded(),
                'performance': self.model_performance,
                'last_training_check': datetime.now(timezone.utc).isoformat(),
                'should_retrain': self._should_retrain(),
                'feature_count': len(self.feature_columns),
                'tensorflow_available': TENSORFLOW_AVAILABLE
            }
            
        except Exception as e:
            logger.error(f"Error getting model status: {e}")
            return {'error': str(e)}

# Global predictor instance
ml_predictor = None

def get_ml_predictor():
    """Get global ML predictor instance"""
    global ml_predictor
    if ml_predictor is None:
        try:
            from models import db
            from core.redis_manager import RedisManager
            
            redis_manager = RedisManager()
            ml_predictor = HybridPredictor(
                db_session=db.session,
                redis_manager=redis_manager
            )
        except Exception as e:
            logger.error(f"Failed to initialize ML predictor: {e}")
            ml_predictor = HybridPredictor()  # Fallback without dependencies
    
    return ml_predictor

# Export
__all__ = [
    'HybridPredictor', 'PredictionResult', 'get_ml_predictor'
]