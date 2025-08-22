"""
Personalized Risk Profiles
Allows users to choose risk profiles: Conservative, Moderate, Aggressive
Automatically adjusts SL/TP, position sizing, and scaling strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from core.risk_management_atr import RiskManagementATR

logger = logging.getLogger(__name__)

class PersonalizedRiskProfiles:
    """
    Risk profile management system with three levels:
    - Conservative: Low risk, tight stops, smaller positions
    - Moderate: Balanced risk/reward
    - Aggressive: Higher risk tolerance, wider stops, larger positions
    """
    
    # Risk profile configurations
    PROFILES = {
        'CONSERVATIVE': {
            'name': 'Conservative',
            'description': 'Low risk, capital preservation focused',
            'risk_per_trade': 1.0,  # 1% per trade
            'max_position_size': 0.05,  # Max 5% of account
            'sl_multiplier': 1.5,  # Tighter stops
            'tp_multiplier': 2.0,  # Conservative targets
            'min_rr_ratio': 2.0,  # Minimum 1:2 R:R
            'max_open_trades': 3,
            'kelly_factor': 0.15,  # Very conservative Kelly
            'scaling_enabled': False,
            'trailing_stop_activation': 0.75,  # Activate at 75% of TP1
            'volatility_filter': 'NORMAL',  # Trade only in normal volatility
            'confidence_threshold': 80  # Need high confidence
        },
        'MODERATE': {
            'name': 'Moderate',
            'description': 'Balanced risk and reward approach',
            'risk_per_trade': 2.0,  # 2% per trade
            'max_position_size': 0.10,  # Max 10% of account
            'sl_multiplier': 2.0,  # Standard stops
            'tp_multiplier': 3.0,  # Standard targets
            'min_rr_ratio': 1.5,  # Minimum 1:1.5 R:R
            'max_open_trades': 5,
            'kelly_factor': 0.25,  # Standard Kelly
            'scaling_enabled': True,
            'trailing_stop_activation': 1.0,  # Activate at TP1
            'volatility_filter': 'HIGH',  # Trade up to high volatility
            'confidence_threshold': 70  # Moderate confidence needed
        },
        'AGGRESSIVE': {
            'name': 'Aggressive',
            'description': 'High risk, high reward seeking',
            'risk_per_trade': 3.0,  # 3% per trade
            'max_position_size': 0.15,  # Max 15% of account
            'sl_multiplier': 2.5,  # Wider stops
            'tp_multiplier': 4.0,  # Aggressive targets
            'min_rr_ratio': 1.0,  # Minimum 1:1 R:R
            'max_open_trades': 8,
            'kelly_factor': 0.35,  # Aggressive Kelly
            'scaling_enabled': True,
            'trailing_stop_activation': 1.5,  # Activate at 150% of TP1
            'volatility_filter': 'EXTREME',  # Trade in any volatility
            'confidence_threshold': 60  # Lower confidence acceptable
        }
    }
    
    def __init__(self, profile: str = 'MODERATE', account_balance: float = 10000):
        self.current_profile = profile.upper()
        self.account_balance = account_balance
        self.active_positions = []
        
        # Validate profile
        if self.current_profile not in self.PROFILES:
            self.current_profile = 'MODERATE'
            logger.warning(f"Invalid profile, defaulting to MODERATE")
        
        # Initialize risk manager with profile settings
        profile_config = self.PROFILES[self.current_profile]
        self.risk_manager = RiskManagementATR(
            account_balance=account_balance,
            risk_per_trade=profile_config['risk_per_trade']
        )
        
        self.logger = logging.getLogger(f"{__name__}.PersonalizedRiskProfiles")
        self.logger.info(f"🎯 Risk Profile initialized: {self.current_profile} - {profile_config['name']}")
    
    def get_profile_settings(self) -> Dict[str, Any]:
        """Get current profile settings"""
        return self.PROFILES[self.current_profile].copy()
    
    def calculate_personalized_risk(self, df: pd.DataFrame, 
                                   signal_type: str = 'BUY',
                                   confidence: float = 70,
                                   entry_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculate risk parameters based on user's risk profile
        """
        try:
            profile = self.PROFILES[self.current_profile]
            
            # Check if trade meets profile requirements
            if confidence < profile['confidence_threshold']:
                return {
                    'allowed': False,
                    'reason': f"Confidence {confidence}% below threshold {profile['confidence_threshold']}%",
                    'profile': self.current_profile
                }
            
            # Check volatility filter
            volatility = self._assess_volatility(df)
            if not self._volatility_acceptable(volatility['regime'], profile['volatility_filter']):
                return {
                    'allowed': False,
                    'reason': f"Volatility {volatility['regime']} exceeds profile limit {profile['volatility_filter']}",
                    'profile': self.current_profile
                }
            
            # Check open positions limit
            if len(self.active_positions) >= profile['max_open_trades']:
                return {
                    'allowed': False,
                    'reason': f"Maximum {profile['max_open_trades']} open trades reached",
                    'profile': self.current_profile
                }
            
            # Calculate position parameters
            current_price = entry_price or float(df['close'].iloc[-1])
            atr = self._calculate_atr(df)
            
            # Profile-specific adjustments
            sl_distance = atr * profile['sl_multiplier']
            tp_distance = atr * profile['tp_multiplier']
            
            # Calculate levels
            if signal_type == 'BUY':
                stop_loss = current_price - sl_distance
                take_profit_1 = current_price + (tp_distance * 0.5)
                take_profit_2 = current_price + tp_distance
                take_profit_3 = current_price + (tp_distance * 1.5)
            else:
                stop_loss = current_price + sl_distance
                take_profit_1 = current_price - (tp_distance * 0.5)
                take_profit_2 = current_price - tp_distance
                take_profit_3 = current_price - (tp_distance * 1.5)
            
            # Calculate position size based on profile
            position_size = self._calculate_profile_position_size(
                current_price, stop_loss, profile, confidence
            )
            
            # Calculate risk metrics
            risk_amount = abs(current_price - stop_loss)
            reward_amount = abs(take_profit_2 - current_price)
            rr_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
            
            # Check minimum R:R ratio
            if rr_ratio < profile['min_rr_ratio']:
                return {
                    'allowed': False,
                    'reason': f"R:R ratio {rr_ratio:.2f} below minimum {profile['min_rr_ratio']}",
                    'profile': self.current_profile
                }
            
            # Scaling strategy based on profile
            scaling_strategy = self._get_scaling_strategy(profile, confidence)
            
            return {
                'allowed': True,
                'profile': self.current_profile,
                'profile_name': profile['name'],
                'entry_price': float(current_price),
                'stop_loss': float(stop_loss),
                'take_profit_levels': {
                    'tp1': float(take_profit_1),
                    'tp2': float(take_profit_2),
                    'tp3': float(take_profit_3)
                },
                'position_sizing': {
                    'units': position_size['units'],
                    'dollar_amount': position_size['dollar_amount'],
                    'percentage_of_account': position_size['percentage'],
                    'risk_per_trade': profile['risk_per_trade']
                },
                'risk_metrics': {
                    'risk_amount': float(risk_amount),
                    'risk_percentage': float((risk_amount / current_price) * 100),
                    'max_loss': float(position_size['dollar_amount'] * (risk_amount / current_price)),
                    'rr_ratio': float(rr_ratio)
                },
                'scaling_strategy': scaling_strategy,
                'trailing_stop': {
                    'enabled': confidence > 75,
                    'activation': float(take_profit_1 * profile['trailing_stop_activation']),
                    'distance': float(atr * 1.5)
                },
                'volatility': volatility,
                'confidence_score': confidence,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Personalized risk calculation error: {e}")
            return {
                'allowed': False,
                'error': str(e),
                'profile': self.current_profile
            }
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate ATR for volatility-based stops"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            return float(atr.iloc[-1])
        except:
            return float(df['close'].iloc[-1] * 0.02)
    
    def _assess_volatility(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess current market volatility"""
        try:
            returns = df['close'].pct_change().dropna()
            volatility_daily = float(returns.std())
            
            if volatility_daily < 0.01:
                regime = 'LOW'
            elif volatility_daily < 0.02:
                regime = 'NORMAL'
            elif volatility_daily < 0.03:
                regime = 'HIGH'
            else:
                regime = 'EXTREME'
            
            return {
                'regime': regime,
                'daily': volatility_daily,
                'annualized': volatility_daily * np.sqrt(365)
            }
        except:
            return {'regime': 'NORMAL', 'daily': 0.02, 'annualized': 0.365}
    
    def _volatility_acceptable(self, current_regime: str, profile_limit: str) -> bool:
        """Check if current volatility is acceptable for profile"""
        volatility_levels = ['LOW', 'NORMAL', 'HIGH', 'EXTREME']
        
        current_idx = volatility_levels.index(current_regime)
        limit_idx = volatility_levels.index(profile_limit)
        
        return current_idx <= limit_idx
    
    def _calculate_profile_position_size(self, entry_price: float, stop_loss: float,
                                        profile: Dict, confidence: float) -> Dict[str, Any]:
        """Calculate position size based on profile settings"""
        try:
            # Base risk amount
            risk_amount = self.account_balance * (profile['risk_per_trade'] / 100)
            
            # Adjust for confidence
            confidence_factor = min(1.2, confidence / 70)
            adjusted_risk = risk_amount * confidence_factor
            
            # Apply Kelly Criterion with profile factor
            kelly_optimal = self._calculate_kelly(confidence / 100, profile['kelly_factor'])
            if kelly_optimal > 0:
                adjusted_risk *= kelly_optimal
            
            # Calculate position
            stop_distance = abs(entry_price - stop_loss)
            stop_distance_pct = stop_distance / entry_price
            
            position_dollar = adjusted_risk / stop_distance_pct
            
            # Apply maximum position size limit
            max_position = self.account_balance * profile['max_position_size']
            position_dollar = min(position_dollar, max_position)
            
            units = position_dollar / entry_price
            
            return {
                'units': float(units),
                'dollar_amount': float(position_dollar),
                'percentage': float((position_dollar / self.account_balance) * 100)
            }
        except:
            return {'units': 0, 'dollar_amount': 0, 'percentage': 0}
    
    def _calculate_kelly(self, win_prob: float, kelly_factor: float) -> float:
        """Calculate Kelly fraction with safety factor"""
        try:
            p = win_prob
            q = 1 - p
            b = 2  # Assume 2:1 win/loss ratio
            
            if b <= 0:
                return 0
            
            kelly = (p * b - q) / b
            safe_kelly = kelly * kelly_factor
            
            return max(0, min(safe_kelly, 0.25))
        except:
            return 0.02
    
    def _get_scaling_strategy(self, profile: Dict, confidence: float) -> Dict[str, Any]:
        """Get scaling strategy based on profile"""
        if not profile['scaling_enabled']:
            return {
                'enabled': False,
                'entries': [{'percentage': 100, 'level': 'market'}],
                'exits': [{'percentage': 100, 'level': 'tp2'}]
            }
        
        # Conservative scaling
        if self.current_profile == 'CONSERVATIVE':
            return {
                'enabled': False,
                'entries': [{'percentage': 100, 'level': 'market'}],
                'exits': [
                    {'percentage': 50, 'level': 'tp1'},
                    {'percentage': 50, 'level': 'tp2'}
                ]
            }
        
        # Moderate scaling
        elif self.current_profile == 'MODERATE':
            return {
                'enabled': True,
                'entries': [
                    {'percentage': 60, 'level': 'market'},
                    {'percentage': 40, 'level': 'pullback'}
                ],
                'exits': [
                    {'percentage': 30, 'level': 'tp1'},
                    {'percentage': 40, 'level': 'tp2'},
                    {'percentage': 30, 'level': 'tp3'}
                ]
            }
        
        # Aggressive scaling
        else:
            return {
                'enabled': True,
                'entries': [
                    {'percentage': 40, 'level': 'market'},
                    {'percentage': 30, 'level': 'pullback_1'},
                    {'percentage': 30, 'level': 'pullback_2'}
                ],
                'exits': [
                    {'percentage': 20, 'level': 'tp1'},
                    {'percentage': 30, 'level': 'tp2'},
                    {'percentage': 30, 'level': 'tp3'},
                    {'percentage': 20, 'level': 'runner'}
                ]
            }
    
    def change_profile(self, new_profile: str) -> Dict[str, Any]:
        """Change risk profile"""
        new_profile = new_profile.upper()
        
        if new_profile not in self.PROFILES:
            return {
                'success': False,
                'error': f"Invalid profile. Choose from: {list(self.PROFILES.keys())}"
            }
        
        old_profile = self.current_profile
        self.current_profile = new_profile
        
        # Update risk manager
        profile_config = self.PROFILES[new_profile]
        self.risk_manager.risk_per_trade = profile_config['risk_per_trade']
        self.risk_manager.max_position_size = profile_config['max_position_size']
        
        self.logger.info(f"Risk profile changed from {old_profile} to {new_profile}")
        
        return {
            'success': True,
            'old_profile': old_profile,
            'new_profile': new_profile,
            'settings': self.get_profile_settings()
        }
    
    def add_position(self, position: Dict[str, Any]):
        """Track active position"""
        self.active_positions.append({
            **position,
            'opened_at': datetime.now().isoformat()
        })
    
    def remove_position(self, position_id: str):
        """Remove closed position"""
        self.active_positions = [
            p for p in self.active_positions 
            if p.get('id') != position_id
        ]
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get comprehensive profile summary"""
        profile = self.PROFILES[self.current_profile]
        
        return {
            'current_profile': self.current_profile,
            'profile_details': profile,
            'account_balance': self.account_balance,
            'active_positions': len(self.active_positions),
            'max_positions': profile['max_open_trades'],
            'total_risk_exposure': self._calculate_total_exposure(),
            'available_risk': self._calculate_available_risk(),
            'recommendations': self._get_profile_recommendations()
        }
    
    def _calculate_total_exposure(self) -> float:
        """Calculate total risk exposure from active positions"""
        total = sum(p.get('risk_amount', 0) for p in self.active_positions)
        return float(total)
    
    def _calculate_available_risk(self) -> float:
        """Calculate available risk budget"""
        profile = self.PROFILES[self.current_profile]
        max_risk = self.account_balance * (profile['risk_per_trade'] * profile['max_open_trades'] / 100)
        used_risk = self._calculate_total_exposure()
        return float(max(0, max_risk - used_risk))
    
    def _get_profile_recommendations(self) -> List[str]:
        """Get recommendations based on current profile"""
        recommendations = []
        
        if self.current_profile == 'CONSERVATIVE':
            recommendations.extend([
                "Focus on high-probability setups only",
                "Wait for strong confluence before entering",
                "Consider reducing position size in volatile markets",
                "Take partial profits early to secure gains"
            ])
        elif self.current_profile == 'MODERATE':
            recommendations.extend([
                "Balance risk across multiple positions",
                "Use scaling strategies for better entries",
                "Monitor correlation between open positions",
                "Adjust position size based on market conditions"
            ])
        else:  # AGGRESSIVE
            recommendations.extend([
                "Ensure proper risk management despite larger positions",
                "Consider hedging in extreme volatility",
                "Monitor total portfolio exposure carefully",
                "Have exit strategy for black swan events"
            ])
        
        return recommendations