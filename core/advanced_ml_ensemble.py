"""
Advanced ML Ensemble with Transformer and Reinforcement Learning
Combines LSTM, XGBoost, Transformer, and RL for powerful predictions
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from collections import deque
import random

logger = logging.getLogger(__name__)

class TransformerPricePredictor(nn.Module):
    """
    Transformer model for price prediction
    Captures long-range dependencies in price movements
    """
    
    def __init__(self, input_dim: int = 10, d_model: int = 128, 
                 nhead: int = 8, num_layers: int = 3, dropout: float = 0.1):
        super(TransformerPricePredictor, self).__init__()
        
        self.input_projection = nn.Linear(input_dim, d_model)
        self.positional_encoding = PositionalEncoding(d_model, dropout)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Output layers for different predictions
        self.price_head = nn.Linear(d_model, 1)  # Next price
        self.direction_head = nn.Linear(d_model, 3)  # Up/Down/Neutral
        self.volatility_head = nn.Linear(d_model, 1)  # Volatility prediction
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        # Input shape: (batch_size, sequence_length, features)
        x = self.input_projection(x)
        x = self.positional_encoding(x)
        
        # Transformer encoding
        x = self.transformer(x)
        
        # Take the last sequence output for prediction
        x = x[:, -1, :]
        
        # Multiple prediction heads
        price_pred = self.price_head(x)
        direction_pred = torch.softmax(self.direction_head(x), dim=-1)
        volatility_pred = torch.sigmoid(self.volatility_head(x))
        
        return {
            'price': price_pred,
            'direction': direction_pred,
            'volatility': volatility_pred
        }

class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * 
                           (-np.log(10000.0) / d_model))
        
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)

class ReinforcementLearningTrader:
    """
    Reinforcement Learning agent for adaptive trading decisions
    Uses Deep Q-Learning (DQN) with experience replay
    """
    
    def __init__(self, state_size: int = 20, action_size: int = 3,
                 learning_rate: float = 0.001):
        self.state_size = state_size
        self.action_size = action_size  # Buy, Hold, Sell
        self.memory = deque(maxlen=2000)
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = learning_rate
        self.gamma = 0.95  # Discount factor
        
        # Neural network for Q-learning
        self.q_network = self._build_model()
        self.target_network = self._build_model()
        self.update_target_network()
        
        self.logger = logging.getLogger(f"{__name__}.RLTrader")
        self.logger.info("🤖 Reinforcement Learning Trader initialized")
    
    def _build_model(self) -> nn.Module:
        """Build Deep Q-Network"""
        model = nn.Sequential(
            nn.Linear(self.state_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, self.action_size)
        )
        return model
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay memory"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state: np.ndarray, training: bool = False) -> int:
        """
        Choose action using epsilon-greedy policy
        Returns: 0 (Sell), 1 (Hold), 2 (Buy)
        """
        if training and random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.q_network(state_tensor)
        return np.argmax(q_values.detach().numpy())
    
    def replay(self, batch_size: int = 32):
        """Train the model on a batch of experiences"""
        if len(self.memory) < batch_size:
            return
        
        batch = random.sample(self.memory, batch_size)
        states = torch.FloatTensor([e[0] for e in batch])
        actions = torch.LongTensor([e[1] for e in batch])
        rewards = torch.FloatTensor([e[2] for e in batch])
        next_states = torch.FloatTensor([e[3] for e in batch])
        dones = torch.FloatTensor([e[4] for e in batch])
        
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * (1 - dones))
        
        loss = nn.MSELoss()(current_q_values.squeeze(), target_q_values)
        
        optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def update_target_network(self):
        """Copy weights from main network to target network"""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def get_action_confidence(self, state: np.ndarray) -> Dict[str, float]:
        """Get confidence scores for each action"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        q_values = self.q_network(state_tensor).detach().numpy()[0]
        
        # Convert Q-values to probabilities using softmax
        exp_q = np.exp(q_values - np.max(q_values))
        probabilities = exp_q / exp_q.sum()
        
        return {
            'sell_confidence': float(probabilities[0]),
            'hold_confidence': float(probabilities[1]),
            'buy_confidence': float(probabilities[2]),
            'recommended_action': ['SELL', 'HOLD', 'BUY'][np.argmax(q_values)]
        }

class AdvancedMLEnsemble:
    """
    Advanced ensemble combining LSTM, XGBoost, Transformer, and RL
    Provides adaptive, powerful predictions
    """
    
    def __init__(self):
        self.transformer = None
        self.rl_trader = ReinforcementLearningTrader()
        self.scaler = StandardScaler()
        
        # Model weights for ensemble (will be optimized dynamically)
        self.model_weights = {
            'lstm': 0.25,
            'xgboost': 0.25,
            'transformer': 0.35,
            'rl': 0.15
        }
        
        # Performance tracking for weight adjustment
        self.model_performance = {
            'lstm': deque(maxlen=100),
            'xgboost': deque(maxlen=100),
            'transformer': deque(maxlen=100),
            'rl': deque(maxlen=100)
        }
        
        self.logger = logging.getLogger(f"{__name__}.AdvancedMLEnsemble")
        self.logger.info("🚀 Advanced ML Ensemble initialized with Transformer & RL")
    
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for model input
        Enhanced feature engineering for better predictions
        """
        try:
            features = []
            
            # Price features
            features.append(df['close'].pct_change().fillna(0))
            features.append(df['volume'].pct_change().fillna(0))
            
            # Technical indicators
            features.append((df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std())
            features.append((df['high'] - df['low']) / df['close'])  # Volatility
            
            # Price patterns
            features.append(df['close'].rolling(5).mean() / df['close'].rolling(20).mean())
            features.append(df['volume'].rolling(5).mean() / df['volume'].rolling(20).mean())
            
            # Market microstructure
            features.append((df['high'] + df['low']) / 2 - df['close'])  # Mean reversion
            features.append(df['close'] - df['open'])  # Intraday momentum
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            features.append(100 - (100 / (1 + rs)))
            
            # Volume indicators
            features.append(df['volume'] / df['volume'].rolling(20).mean())
            
            # Stack features
            feature_matrix = np.column_stack(features)
            
            # Remove NaN rows
            feature_matrix = feature_matrix[~np.isnan(feature_matrix).any(axis=1)]
            
            # Normalize
            if len(feature_matrix) > 0:
                feature_matrix = self.scaler.fit_transform(feature_matrix)
            
            return feature_matrix
            
        except Exception as e:
            self.logger.error(f"Feature preparation error: {e}")
            return np.array([])
    
    def train_transformer(self, df: pd.DataFrame, epochs: int = 10):
        """Train transformer model on historical data"""
        try:
            features = self.prepare_features(df)
            if len(features) < 50:
                self.logger.warning("Insufficient data for transformer training")
                return
            
            # Create sequences for transformer
            sequence_length = 30
            X, y = [], []
            
            for i in range(sequence_length, len(features) - 1):
                X.append(features[i-sequence_length:i])
                # Next price change as target
                y.append(df['close'].iloc[i+1] / df['close'].iloc[i] - 1)
            
            X = torch.FloatTensor(np.array(X))
            y = torch.FloatTensor(np.array(y))
            
            # Initialize transformer if not exists
            if self.transformer is None:
                self.transformer = TransformerPricePredictor(
                    input_dim=features.shape[1]
                )
            
            # Training loop
            optimizer = optim.Adam(self.transformer.parameters(), lr=0.001)
            criterion = nn.MSELoss()
            
            self.transformer.train()
            for epoch in range(epochs):
                optimizer.zero_grad()
                outputs = self.transformer(X)
                loss = criterion(outputs['price'].squeeze(), y)
                loss.backward()
                optimizer.step()
                
                if epoch % 5 == 0:
                    self.logger.info(f"Transformer training - Epoch {epoch}, Loss: {loss.item():.6f}")
            
            self.logger.info("✅ Transformer training completed")
            
        except Exception as e:
            self.logger.error(f"Transformer training error: {e}")
    
    def get_ensemble_prediction(self, df: pd.DataFrame, 
                               lstm_pred: Optional[Dict] = None,
                               xgboost_pred: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Get ensemble prediction combining all models
        """
        try:
            predictions = {}
            confidences = {}
            
            # Get Transformer prediction
            transformer_pred = self._get_transformer_prediction(df)
            if transformer_pred:
                predictions['transformer'] = transformer_pred
                confidences['transformer'] = transformer_pred.get('confidence', 0.7)
            
            # Get RL trading decision
            rl_decision = self._get_rl_decision(df)
            if rl_decision:
                predictions['rl'] = rl_decision
                confidences['rl'] = max(
                    rl_decision['buy_confidence'],
                    rl_decision['sell_confidence'],
                    rl_decision['hold_confidence']
                )
            
            # Add LSTM prediction if provided
            if lstm_pred:
                predictions['lstm'] = lstm_pred
                confidences['lstm'] = lstm_pred.get('confidence', 0.6)
            
            # Add XGBoost prediction if provided
            if xgboost_pred:
                predictions['xgboost'] = xgboost_pred
                confidences['xgboost'] = xgboost_pred.get('confidence', 0.65)
            
            # Calculate weighted ensemble prediction
            ensemble_result = self._calculate_weighted_ensemble(predictions, confidences)
            
            # Adaptive weight adjustment based on recent performance
            self._adjust_model_weights(predictions)
            
            return {
                'ensemble_prediction': ensemble_result,
                'individual_predictions': predictions,
                'model_weights': self.model_weights.copy(),
                'model_confidences': confidences,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Ensemble prediction error: {e}")
            return {
                'error': str(e),
                'ensemble_prediction': {'action': 'HOLD', 'confidence': 0}
            }
    
    def _get_transformer_prediction(self, df: pd.DataFrame) -> Optional[Dict]:
        """Get prediction from transformer model"""
        try:
            if self.transformer is None:
                return None
            
            features = self.prepare_features(df)
            if len(features) < 30:
                return None
            
            # Prepare sequence
            sequence = torch.FloatTensor(features[-30:]).unsqueeze(0)
            
            self.transformer.eval()
            with torch.no_grad():
                output = self.transformer(sequence)
            
            price_change = output['price'].item()
            direction_probs = output['direction'].numpy()[0]
            volatility = output['volatility'].item()
            
            # Determine action
            if price_change > 0.01:  # 1% threshold
                action = 'BUY'
                confidence = direction_probs[2]  # Up probability
            elif price_change < -0.01:
                action = 'SELL'
                confidence = direction_probs[0]  # Down probability
            else:
                action = 'HOLD'
                confidence = direction_probs[1]  # Neutral probability
            
            return {
                'action': action,
                'price_change_prediction': float(price_change),
                'confidence': float(confidence),
                'volatility_prediction': float(volatility),
                'direction_probabilities': {
                    'down': float(direction_probs[0]),
                    'neutral': float(direction_probs[1]),
                    'up': float(direction_probs[2])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Transformer prediction error: {e}")
            return None
    
    def _get_rl_decision(self, df: pd.DataFrame) -> Optional[Dict]:
        """Get trading decision from RL agent"""
        try:
            features = self.prepare_features(df)
            if len(features) < 20:
                return None
            
            # Use last 20 features as state
            state = features[-20:].flatten()
            
            # Get action and confidence
            action_confidence = self.rl_trader.get_action_confidence(state)
            
            return action_confidence
            
        except Exception as e:
            self.logger.error(f"RL decision error: {e}")
            return None
    
    def _calculate_weighted_ensemble(self, predictions: Dict, 
                                    confidences: Dict) -> Dict[str, Any]:
        """Calculate weighted ensemble prediction"""
        try:
            action_scores = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            total_weight = 0
            
            for model_name, pred in predictions.items():
                if model_name not in self.model_weights:
                    continue
                
                weight = self.model_weights[model_name] * confidences.get(model_name, 0.5)
                total_weight += weight
                
                # Handle different prediction formats
                if 'action' in pred:
                    action = pred['action']
                    if action in action_scores:
                        action_scores[action] += weight
                elif 'recommended_action' in pred:
                    action = pred['recommended_action']
                    if action in action_scores:
                        action_scores[action] += weight
                
                # For RL model with separate confidences
                if 'buy_confidence' in pred:
                    action_scores['BUY'] += weight * pred['buy_confidence']
                    action_scores['SELL'] += weight * pred['sell_confidence']
                    action_scores['HOLD'] += weight * pred['hold_confidence']
            
            # Normalize scores
            if total_weight > 0:
                for action in action_scores:
                    action_scores[action] /= total_weight
            
            # Get final action
            final_action = max(action_scores, key=action_scores.get)
            final_confidence = action_scores[final_action]
            
            return {
                'action': final_action,
                'confidence': float(final_confidence),
                'action_scores': action_scores,
                'models_used': len(predictions)
            }
            
        except Exception as e:
            self.logger.error(f"Weighted ensemble calculation error: {e}")
            return {'action': 'HOLD', 'confidence': 0}
    
    def _adjust_model_weights(self, predictions: Dict):
        """
        Dynamically adjust model weights based on recent performance
        Uses exponential moving average of accuracy
        """
        try:
            # This would be called with actual vs predicted results
            # For now, we'll maintain static weights
            # In production, this would track prediction accuracy
            pass
            
        except Exception as e:
            self.logger.error(f"Weight adjustment error: {e}")
    
    def train_rl_agent(self, df: pd.DataFrame, episodes: int = 10):
        """Train RL agent on historical data"""
        try:
            features = self.prepare_features(df)
            if len(features) < 100:
                self.logger.warning("Insufficient data for RL training")
                return
            
            prices = df['close'].values[-len(features):]
            
            for episode in range(episodes):
                state_idx = 20
                total_reward = 0
                
                while state_idx < len(features) - 1:
                    # Current state
                    state = features[state_idx-20:state_idx].flatten()
                    
                    # Take action
                    action = self.rl_trader.act(state, training=True)
                    
                    # Calculate reward
                    price_change = (prices[state_idx + 1] - prices[state_idx]) / prices[state_idx]
                    
                    if action == 2:  # Buy
                        reward = price_change * 100
                    elif action == 0:  # Sell
                        reward = -price_change * 100
                    else:  # Hold
                        reward = -0.001  # Small penalty for holding
                    
                    # Next state
                    next_state = features[state_idx-19:state_idx+1].flatten()
                    done = state_idx >= len(features) - 2
                    
                    # Remember experience
                    self.rl_trader.remember(state, action, reward, next_state, done)
                    
                    # Train on batch
                    if len(self.rl_trader.memory) > 32:
                        self.rl_trader.replay(32)
                    
                    total_reward += reward
                    state_idx += 1
                
                # Update target network periodically
                if episode % 5 == 0:
                    self.rl_trader.update_target_network()
                    self.logger.info(f"RL Training - Episode {episode}, Total Reward: {total_reward:.2f}")
            
            self.logger.info("✅ RL agent training completed")
            
        except Exception as e:
            self.logger.error(f"RL training error: {e}")
    
    def get_model_importance(self) -> Dict[str, float]:
        """Get current importance/weight of each model in ensemble"""
        return {
            'lstm': self.model_weights['lstm'],
            'xgboost': self.model_weights['xgboost'],
            'transformer': self.model_weights['transformer'],
            'reinforcement_learning': self.model_weights['rl']
        }