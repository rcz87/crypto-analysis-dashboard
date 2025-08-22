"""
Risk Management with ATR-based Stop Loss and Take Profit
Professional position sizing and risk management
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RiskManagementATR:
    """
    Advanced risk management system using:
    - ATR (Average True Range) for volatility-based SL/TP
    - Position sizing based on account risk
    - Risk/Reward ratio optimization
    - Kelly Criterion for optimal position sizing
    - Maximum drawdown protection
    """
    
    def __init__(self, account_balance: float = 10000, risk_per_trade: float = 2.0):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade  # Percentage of account to risk
        self.min_rr_ratio = 1.5  # Minimum risk/reward ratio
        self.max_position_size = 0.1  # Max 10% of account per position
        self.atr_multiplier_sl = 2.0  # ATR multiplier for stop loss
        self.atr_multiplier_tp = 3.0  # ATR multiplier for take profit
        self.logger = logging.getLogger(f"{__name__}.RiskManagementATR")
        self.logger.info(f"💰 Risk Management initialized - Balance: ${account_balance:,.2f}, Risk: {risk_per_trade}%")
    
    def calculate_risk_parameters(self, df: pd.DataFrame, entry_price: float = None,
                                  signal_type: str = 'BUY', confidence: float = 70) -> Dict[str, Any]:
        """
        Calculate comprehensive risk management parameters
        """
        try:
            if df is None or len(df) < 20:
                return self._get_default_risk_params()
            
            # Ensure numeric types
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Use current price if entry not specified
            current_price = float(df['close'].iloc[-1])
            entry_price = entry_price or current_price
            
            # Calculate ATR
            atr_value = self._calculate_atr(df)
            
            # Calculate volatility metrics
            volatility = self._calculate_volatility_metrics(df)
            
            # Adjust ATR multipliers based on volatility
            sl_multiplier, tp_multiplier = self._adjust_multipliers_by_volatility(
                volatility, confidence
            )
            
            # Calculate stop loss and take profit levels
            if signal_type == 'BUY':
                stop_loss = entry_price - (atr_value * sl_multiplier)
                take_profit_1 = entry_price + (atr_value * tp_multiplier * 0.5)  # First target
                take_profit_2 = entry_price + (atr_value * tp_multiplier)  # Second target
                take_profit_3 = entry_price + (atr_value * tp_multiplier * 1.5)  # Extended target
            else:  # SELL
                stop_loss = entry_price + (atr_value * sl_multiplier)
                take_profit_1 = entry_price - (atr_value * tp_multiplier * 0.5)
                take_profit_2 = entry_price - (atr_value * tp_multiplier)
                take_profit_3 = entry_price - (atr_value * tp_multiplier * 1.5)
            
            # Calculate position size
            position_size = self._calculate_position_size(
                entry_price, stop_loss, confidence
            )
            
            # Calculate risk/reward ratios
            risk_amount = abs(entry_price - stop_loss)
            reward_1 = abs(take_profit_1 - entry_price)
            reward_2 = abs(take_profit_2 - entry_price)
            reward_3 = abs(take_profit_3 - entry_price)
            
            # Kelly Criterion for optimal position sizing
            kelly_fraction = self._calculate_kelly_criterion(
                confidence / 100, reward_2 / risk_amount
            )
            
            # Maximum loss calculation
            max_loss_amount = position_size['dollar_amount'] * (risk_amount / entry_price)
            
            return {
                'entry_price': float(entry_price),
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
                    'kelly_optimal': kelly_fraction
                },
                'risk_metrics': {
                    'atr': float(atr_value),
                    'risk_amount': float(risk_amount),
                    'risk_percentage': float((risk_amount / entry_price) * 100),
                    'max_loss_dollar': float(max_loss_amount),
                    'max_loss_percentage': float((max_loss_amount / self.account_balance) * 100)
                },
                'reward_metrics': {
                    'rr_ratio_tp1': float(reward_1 / risk_amount),
                    'rr_ratio_tp2': float(reward_2 / risk_amount),
                    'rr_ratio_tp3': float(reward_3 / risk_amount),
                    'expected_profit_tp2': float(position_size['dollar_amount'] * (reward_2 / entry_price))
                },
                'volatility': volatility,
                'trailing_stop': {
                    'enabled': confidence > 75,
                    'distance': float(atr_value * 1.5),
                    'activation_price': float(take_profit_1)  # Activate after TP1
                },
                'scaling_strategy': self._generate_scaling_strategy(
                    signal_type, confidence, volatility['regime']
                ),
                'risk_level': self._determine_risk_level(volatility, confidence),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Risk calculation error: {e}")
            return self._get_default_risk_params()
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range
        """
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # True Range calculation
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # ATR is the rolling mean of True Range
            atr = true_range.rolling(window=period).mean()
            
            return float(atr.iloc[-1])
            
        except Exception as e:
            self.logger.error(f"ATR calculation error: {e}")
            # Return a safe default based on current price
            return float(df['close'].iloc[-1] * 0.02)  # 2% of price as default
    
    def _calculate_volatility_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate comprehensive volatility metrics
        """
        try:
            returns = df['close'].pct_change().dropna()
            
            # Historical volatility (standard deviation of returns)
            volatility_daily = float(returns.std())
            volatility_annualized = float(volatility_daily * np.sqrt(365))
            
            # Volatility regime
            if volatility_daily < 0.01:
                regime = 'LOW'
            elif volatility_daily < 0.02:
                regime = 'NORMAL'
            elif volatility_daily < 0.03:
                regime = 'HIGH'
            else:
                regime = 'EXTREME'
            
            # Average daily range
            daily_range = (df['high'] - df['low']) / df['low']
            avg_daily_range = float(daily_range.mean())
            
            # Recent volatility vs historical
            recent_vol = float(returns.iloc[-5:].std())
            historical_vol = float(returns.iloc[-20:].std())
            vol_expansion = recent_vol > historical_vol * 1.5
            
            return {
                'daily': volatility_daily,
                'annualized': volatility_annualized,
                'regime': regime,
                'avg_daily_range_pct': avg_daily_range * 100,
                'volatility_expanding': vol_expansion,
                'recent_vs_historical': recent_vol / historical_vol if historical_vol > 0 else 1
            }
            
        except Exception as e:
            self.logger.error(f"Volatility calculation error: {e}")
            return {
                'daily': 0.02,
                'annualized': 0.365,
                'regime': 'NORMAL',
                'avg_daily_range_pct': 2.0,
                'volatility_expanding': False,
                'recent_vs_historical': 1.0
            }
    
    def _adjust_multipliers_by_volatility(self, volatility: Dict, confidence: float) -> Tuple[float, float]:
        """
        Adjust ATR multipliers based on volatility regime and confidence
        """
        base_sl = self.atr_multiplier_sl
        base_tp = self.atr_multiplier_tp
        
        # Adjust for volatility regime
        if volatility['regime'] == 'LOW':
            sl_mult = base_sl * 0.8  # Tighter stop in low volatility
            tp_mult = base_tp * 0.9
        elif volatility['regime'] == 'HIGH':
            sl_mult = base_sl * 1.2  # Wider stop in high volatility
            tp_mult = base_tp * 1.1
        elif volatility['regime'] == 'EXTREME':
            sl_mult = base_sl * 1.5  # Much wider stop in extreme volatility
            tp_mult = base_tp * 1.2
        else:  # NORMAL
            sl_mult = base_sl
            tp_mult = base_tp
        
        # Adjust for confidence
        if confidence > 80:
            sl_mult *= 0.9  # Tighter stop with high confidence
            tp_mult *= 1.1  # Higher target
        elif confidence < 60:
            sl_mult *= 1.1  # Wider stop with low confidence
            tp_mult *= 0.9  # Lower target
        
        # Adjust for volatility expansion
        if volatility['volatility_expanding']:
            sl_mult *= 1.1  # Give more room during volatility expansion
        
        return sl_mult, tp_mult
    
    def _calculate_position_size(self, entry_price: float, stop_loss: float, 
                                 confidence: float) -> Dict[str, Any]:
        """
        Calculate position size based on risk management rules
        """
        try:
            # Risk amount in dollars
            risk_amount_per_trade = self.account_balance * (self.risk_per_trade / 100)
            
            # Adjust risk based on confidence
            confidence_multiplier = min(1.5, confidence / 70)  # Scale up to 1.5x at 100% confidence
            adjusted_risk = risk_amount_per_trade * confidence_multiplier
            
            # Calculate position size based on stop loss distance
            stop_distance = abs(entry_price - stop_loss)
            stop_distance_pct = stop_distance / entry_price
            
            # Position size in dollars
            position_dollar = adjusted_risk / stop_distance_pct
            
            # Apply maximum position size limit
            max_position_dollar = self.account_balance * self.max_position_size
            position_dollar = min(position_dollar, max_position_dollar)
            
            # Calculate units
            units = position_dollar / entry_price
            
            return {
                'units': float(units),
                'dollar_amount': float(position_dollar),
                'percentage': float((position_dollar / self.account_balance) * 100)
            }
            
        except Exception as e:
            self.logger.error(f"Position sizing error: {e}")
            return {
                'units': 0,
                'dollar_amount': 0,
                'percentage': 0
            }
    
    def _calculate_kelly_criterion(self, win_probability: float, avg_win_loss_ratio: float) -> float:
        """
        Calculate Kelly Criterion for optimal position sizing
        f* = (p * b - q) / b
        where:
        f* = fraction of capital to wager
        p = probability of winning
        q = probability of losing (1 - p)
        b = ratio of win to loss
        """
        try:
            p = win_probability
            q = 1 - p
            b = avg_win_loss_ratio
            
            if b <= 0:
                return 0
            
            kelly_fraction = (p * b - q) / b
            
            # Apply Kelly fraction with safety factor (usually 0.25 to 0.5 of full Kelly)
            safety_factor = 0.25
            safe_kelly = kelly_fraction * safety_factor
            
            # Cap at maximum position size
            return float(min(max(0, safe_kelly), self.max_position_size))
            
        except Exception as e:
            self.logger.error(f"Kelly calculation error: {e}")
            return 0.02  # Default to 2% position
    
    def _generate_scaling_strategy(self, signal_type: str, confidence: float, 
                                   volatility_regime: str) -> Dict[str, Any]:
        """
        Generate position scaling strategy
        """
        strategy = {
            'scale_in': False,
            'scale_out': True,
            'entries': [],
            'exits': []
        }
        
        # Scale-in strategy for high confidence
        if confidence > 80 and volatility_regime in ['LOW', 'NORMAL']:
            strategy['scale_in'] = True
            strategy['entries'] = [
                {'percentage': 50, 'level': 'market'},
                {'percentage': 30, 'level': 'pullback_1'},  # Wait for small pullback
                {'percentage': 20, 'level': 'pullback_2'}   # Wait for deeper pullback
            ]
        else:
            strategy['entries'] = [
                {'percentage': 100, 'level': 'market'}
            ]
        
        # Scale-out strategy (always enabled)
        strategy['exits'] = [
            {'percentage': 30, 'level': 'tp1', 'action': 'take_profit'},
            {'percentage': 40, 'level': 'tp2', 'action': 'take_profit'},
            {'percentage': 30, 'level': 'tp3', 'action': 'take_profit'}
        ]
        
        return strategy
    
    def _determine_risk_level(self, volatility: Dict, confidence: float) -> str:
        """
        Determine overall risk level
        """
        risk_score = 0
        
        # Volatility contribution
        if volatility['regime'] == 'EXTREME':
            risk_score += 40
        elif volatility['regime'] == 'HIGH':
            risk_score += 25
        elif volatility['regime'] == 'NORMAL':
            risk_score += 15
        else:
            risk_score += 10
        
        # Confidence contribution (inverse)
        risk_score += (100 - confidence) * 0.4
        
        # Volatility expansion
        if volatility['volatility_expanding']:
            risk_score += 10
        
        if risk_score < 30:
            return 'LOW'
        elif risk_score < 50:
            return 'MEDIUM'
        elif risk_score < 70:
            return 'HIGH'
        else:
            return 'EXTREME'
    
    def calculate_portfolio_risk(self, open_positions: List[Dict]) -> Dict[str, Any]:
        """
        Calculate overall portfolio risk metrics
        """
        try:
            if not open_positions:
                return {
                    'total_risk_dollar': 0,
                    'total_risk_percentage': 0,
                    'correlation_risk': 'LOW',
                    'max_drawdown_risk': 0,
                    'positions_at_risk': 0
                }
            
            total_risk = 0
            total_exposure = 0
            
            for position in open_positions:
                risk = abs(position['entry'] - position['stop_loss']) * position['units']
                total_risk += risk
                total_exposure += position['entry'] * position['units']
            
            total_risk_pct = (total_risk / self.account_balance) * 100
            
            # Correlation risk (simplified - in reality would check actual correlations)
            correlation_risk = 'HIGH' if len(open_positions) > 5 else 'MEDIUM' if len(open_positions) > 3 else 'LOW'
            
            # Maximum drawdown risk
            max_dd_risk = min(total_risk_pct * 2, 20)  # Assume 2x risk as potential drawdown
            
            return {
                'total_risk_dollar': float(total_risk),
                'total_risk_percentage': float(total_risk_pct),
                'total_exposure': float(total_exposure),
                'exposure_percentage': float((total_exposure / self.account_balance) * 100),
                'correlation_risk': correlation_risk,
                'max_drawdown_risk': float(max_dd_risk),
                'positions_at_risk': len(open_positions),
                'risk_per_position': float(total_risk / len(open_positions)) if open_positions else 0
            }
            
        except Exception as e:
            self.logger.error(f"Portfolio risk calculation error: {e}")
            return {
                'total_risk_dollar': 0,
                'total_risk_percentage': 0,
                'correlation_risk': 'UNKNOWN',
                'max_drawdown_risk': 0,
                'positions_at_risk': 0
            }
    
    def update_account_balance(self, new_balance: float):
        """Update account balance for position sizing"""
        self.account_balance = new_balance
        self.logger.info(f"Account balance updated to ${new_balance:,.2f}")
    
    def _get_default_risk_params(self) -> Dict[str, Any]:
        """Return default risk parameters when calculation fails"""
        return {
            'entry_price': 0,
            'stop_loss': 0,
            'take_profit_levels': {'tp1': 0, 'tp2': 0, 'tp3': 0},
            'position_sizing': {
                'units': 0,
                'dollar_amount': 0,
                'percentage_of_account': 0,
                'kelly_optimal': 0
            },
            'risk_metrics': {
                'atr': 0,
                'risk_amount': 0,
                'risk_percentage': 0,
                'max_loss_dollar': 0,
                'max_loss_percentage': 0
            },
            'reward_metrics': {
                'rr_ratio_tp1': 0,
                'rr_ratio_tp2': 0,
                'rr_ratio_tp3': 0,
                'expected_profit_tp2': 0
            },
            'volatility': {
                'daily': 0,
                'annualized': 0,
                'regime': 'UNKNOWN',
                'avg_daily_range_pct': 0,
                'volatility_expanding': False,
                'recent_vs_historical': 1
            },
            'trailing_stop': {
                'enabled': False,
                'distance': 0,
                'activation_price': 0
            },
            'scaling_strategy': {
                'scale_in': False,
                'scale_out': False,
                'entries': [],
                'exits': []
            },
            'risk_level': 'UNKNOWN',
            'timestamp': datetime.now().isoformat()
        }