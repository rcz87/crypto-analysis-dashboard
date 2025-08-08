"""
Risk Management Calculator
Provides position sizing, risk calculation, and capital protection features
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class RiskManager:
    """
    Advanced risk management system for trading
    - Position sizing based on account balance
    - Risk per trade calculation (1-2% rule)
    - Leverage recommendation based on volatility
    - Stop loss and take profit optimization
    """
    
    def __init__(self):
        # Default risk parameters (can be customized)
        self.default_risk_percent = 1.0  # 1% risk per trade
        self.max_risk_percent = 2.0      # Maximum 2% risk allowed
        self.default_leverage = 1        # No leverage by default
        self.max_leverage = 10           # Maximum 10x leverage
        
        # Account settings (can be overridden)
        self.default_account_balance = float(os.environ.get('DEFAULT_ACCOUNT_BALANCE', 10000))
        
        logger.info("💰 Risk Manager initialized with capital protection features")
    
    def calculate_position_size(self, 
                              entry_price: float,
                              stop_loss: float,
                              account_balance: Optional[float] = None,
                              risk_percent: Optional[float] = None) -> Dict[str, Any]:
        """
        Calculate optimal position size based on risk management rules
        """
        try:
            # Use provided values or defaults
            balance = account_balance or self.default_account_balance
            risk_pct = risk_percent or self.default_risk_percent
            
            # Validate risk percentage
            if risk_pct > self.max_risk_percent:
                logger.warning(f"Risk percent {risk_pct}% exceeds maximum {self.max_risk_percent}%")
                risk_pct = self.max_risk_percent
            
            # Calculate risk amount in USD
            risk_amount = balance * (risk_pct / 100)
            
            # Calculate position size
            price_difference = abs(entry_price - stop_loss)
            risk_per_unit = price_difference
            
            if risk_per_unit > 0:
                position_size = risk_amount / risk_per_unit
                position_value = position_size * entry_price
            else:
                position_size = 0
                position_value = 0
            
            # Calculate leverage needed
            leverage_needed = position_value / balance if balance > 0 else 0
            recommended_leverage = min(max(1, round(leverage_needed)), self.max_leverage)
            
            return {
                'position_size': round(position_size, 6),
                'position_value_usd': round(position_value, 2),
                'risk_amount_usd': round(risk_amount, 2),
                'risk_percent': risk_pct,
                'leverage_needed': round(leverage_needed, 2),
                'recommended_leverage': recommended_leverage,
                'max_loss_usd': round(risk_amount, 2),
                'account_balance': balance,
                'calculation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Position size calculation error: {e}")
            return {
                'error': str(e),
                'position_size': 0,
                'recommended_leverage': 1
            }
    
    def calculate_risk_reward_ratio(self,
                                  entry_price: float,
                                  stop_loss: float,
                                  take_profit: float) -> Dict[str, Any]:
        """
        Calculate risk/reward ratio and trade quality
        """
        try:
            # Calculate risk and reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            # Calculate ratio
            if risk > 0:
                rr_ratio = reward / risk
            else:
                rr_ratio = 0
            
            # Evaluate trade quality
            if rr_ratio >= 3:
                quality = 'EXCELLENT'
                recommendation = 'Highly favorable risk/reward ratio'
            elif rr_ratio >= 2:
                quality = 'GOOD'
                recommendation = 'Favorable risk/reward ratio'
            elif rr_ratio >= 1.5:
                quality = 'ACCEPTABLE'
                recommendation = 'Acceptable risk/reward ratio'
            else:
                quality = 'POOR'
                recommendation = 'Consider wider take profit or tighter stop loss'
            
            return {
                'risk_reward_ratio': round(rr_ratio, 2),
                'risk_amount': round(risk, 6),
                'reward_amount': round(reward, 6),
                'trade_quality': quality,
                'recommendation': recommendation,
                'minimum_win_rate': round(1 / (1 + rr_ratio) * 100, 1)  # Break-even win rate
            }
            
        except Exception as e:
            logger.error(f"Risk/reward calculation error: {e}")
            return {
                'risk_reward_ratio': 0,
                'trade_quality': 'ERROR',
                'error': str(e)
            }
    
    def recommend_leverage_by_volatility(self, 
                                       atr: float,
                                       current_price: float) -> Dict[str, Any]:
        """
        Recommend leverage based on market volatility (ATR)
        """
        try:
            # Calculate volatility percentage
            volatility_pct = (atr / current_price) * 100
            
            # Leverage recommendation based on volatility
            if volatility_pct < 1:
                # Low volatility
                max_safe_leverage = 10
                recommended = 5
                risk_level = 'LOW'
            elif volatility_pct < 2:
                # Medium volatility
                max_safe_leverage = 5
                recommended = 3
                risk_level = 'MEDIUM'
            elif volatility_pct < 3:
                # High volatility
                max_safe_leverage = 3
                recommended = 2
                risk_level = 'HIGH'
            else:
                # Extreme volatility
                max_safe_leverage = 2
                recommended = 1
                risk_level = 'EXTREME'
            
            return {
                'volatility_percent': round(volatility_pct, 2),
                'risk_level': risk_level,
                'recommended_leverage': recommended,
                'max_safe_leverage': max_safe_leverage,
                'warning': 'High leverage increases liquidation risk' if recommended > 3 else None
            }
            
        except Exception as e:
            logger.error(f"Leverage recommendation error: {e}")
            return {
                'recommended_leverage': 1,
                'risk_level': 'UNKNOWN',
                'error': str(e)
            }
    
    def calculate_liquidation_price(self,
                                  entry_price: float,
                                  leverage: int,
                                  position_type: str = 'LONG') -> Dict[str, Any]:
        """
        Calculate liquidation price for leveraged positions
        """
        try:
            # Maintenance margin requirement (usually 0.5% for crypto)
            maintenance_margin = 0.005
            
            # Calculate liquidation price
            if position_type.upper() == 'LONG':
                # Long position liquidation
                liquidation_price = entry_price * (1 - (1 / leverage) + maintenance_margin)
                distance_percent = ((entry_price - liquidation_price) / entry_price) * 100
            else:
                # Short position liquidation
                liquidation_price = entry_price * (1 + (1 / leverage) - maintenance_margin)
                distance_percent = ((liquidation_price - entry_price) / entry_price) * 100
            
            # Safety assessment
            if distance_percent > 20:
                safety = 'SAFE'
            elif distance_percent > 10:
                safety = 'MODERATE'
            else:
                safety = 'RISKY'
            
            return {
                'liquidation_price': round(liquidation_price, 6),
                'distance_from_entry': round(distance_percent, 2),
                'safety_level': safety,
                'leverage': leverage,
                'position_type': position_type
            }
            
        except Exception as e:
            logger.error(f"Liquidation calculation error: {e}")
            return {
                'liquidation_price': 0,
                'error': str(e)
            }
    
    def generate_risk_report(self,
                           signal_data: Dict[str, Any],
                           account_balance: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate comprehensive risk management report for a signal
        """
        try:
            balance = account_balance or self.default_account_balance
            
            # Extract signal data
            entry_price = signal_data.get('entry_price', 0)
            stop_loss = signal_data.get('stop_loss', 0)
            take_profit = signal_data.get('take_profit', 0)
            atr = signal_data.get('atr', entry_price * 0.02)  # Default 2% if no ATR
            
            # Calculate all risk metrics
            position_sizing = self.calculate_position_size(
                entry_price, stop_loss, balance
            )
            
            risk_reward = self.calculate_risk_reward_ratio(
                entry_price, stop_loss, take_profit
            )
            
            leverage_recommendation = self.recommend_leverage_by_volatility(
                atr, entry_price
            )
            
            # Use recommended leverage for liquidation calculation
            recommended_leverage = leverage_recommendation['recommended_leverage']
            liquidation_info = self.calculate_liquidation_price(
                entry_price, recommended_leverage, 
                'LONG' if signal_data.get('direction') == 'BUY' else 'SHORT'
            )
            
            # Compile comprehensive report
            return {
                'risk_assessment': {
                    'overall_risk': self._assess_overall_risk(risk_reward, leverage_recommendation),
                    'position_sizing': position_sizing,
                    'risk_reward': risk_reward,
                    'leverage': leverage_recommendation,
                    'liquidation': liquidation_info
                },
                'recommendations': {
                    'position_size': position_sizing['position_size'],
                    'leverage': recommended_leverage,
                    'max_loss_usd': position_sizing['max_loss_usd'],
                    'risk_per_trade': position_sizing['risk_percent']
                },
                'warnings': self._generate_warnings(risk_reward, leverage_recommendation),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Risk report generation error: {e}")
            return {
                'error': str(e),
                'recommendations': {
                    'position_size': 0,
                    'leverage': 1,
                    'warning': 'Unable to calculate risk metrics'
                }
            }
    
    def _assess_overall_risk(self, risk_reward: Dict, leverage: Dict) -> str:
        """Assess overall trade risk"""
        rr_ratio = risk_reward.get('risk_reward_ratio', 0)
        risk_level = leverage.get('risk_level', 'UNKNOWN')
        
        if rr_ratio >= 2 and risk_level in ['LOW', 'MEDIUM']:
            return 'LOW_RISK'
        elif rr_ratio >= 1.5 or risk_level == 'MEDIUM':
            return 'MEDIUM_RISK'
        else:
            return 'HIGH_RISK'
    
    def _generate_warnings(self, risk_reward: Dict, leverage: Dict) -> List[str]:
        """Generate risk warnings based on analysis"""
        warnings = []
        
        if risk_reward.get('risk_reward_ratio', 0) < 1.5:
            warnings.append("⚠️ Low risk/reward ratio - Consider adjusting targets")
        
        if leverage.get('risk_level') in ['HIGH', 'EXTREME']:
            warnings.append("⚠️ High market volatility - Reduce position size")
        
        if leverage.get('recommended_leverage', 1) > 5:
            warnings.append("⚠️ High leverage recommended - Monitor closely")
        
        return warnings