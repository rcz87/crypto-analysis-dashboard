"""
Real-time Signal Enhancer
Enhances existing signals with live WebSocket data
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import numpy as np

logger = logging.getLogger(__name__)

class RealtimeSignalEnhancer:
    """
    Enhances trading signals with real-time data
    Adjusts entry/exit points based on live market conditions
    """
    
    def __init__(self, ws_data_manager):
        self.ws_data_manager = ws_data_manager
        self.enhanced_signals = {}
        self.signal_performance = {}
        
    def enhance_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance signal with real-time data
        """
        try:
            symbol = signal.get('symbol', '')
            
            # Get real-time market snapshot
            market_data = self.ws_data_manager.get_market_snapshot(symbol)
            
            # Get current real-time price
            current_price = market_data['price_data'].get('price', signal.get('entry_price'))
            
            # Enhanced signal with real-time adjustments
            enhanced = {
                **signal,
                'original_entry': signal.get('entry_price'),
                'enhanced_entry': self._calculate_optimal_entry(
                    signal, 
                    current_price, 
                    market_data['orderbook']
                ),
                'real_time_price': current_price,
                'price_delta': current_price - signal.get('entry_price', current_price),
                'orderbook_support': self._analyze_orderbook_support(
                    signal.get('action'),
                    market_data['orderbook']
                ),
                'liquidation_risk': self._assess_liquidation_risk(
                    market_data['recent_liquidations']
                ),
                'enhanced_confidence': self._calculate_enhanced_confidence(
                    signal.get('confidence', 70),
                    market_data
                ),
                'enhanced_stop_loss': self._calculate_dynamic_stop_loss(
                    signal,
                    current_price,
                    market_data['price_history']
                ),
                'enhanced_take_profit': self._calculate_dynamic_take_profit(
                    signal,
                    current_price,
                    market_data['orderbook']
                ),
                'enhancement_timestamp': datetime.now(timezone.utc).isoformat(),
                'market_conditions': self._assess_market_conditions(market_data)
            }
            
            # Store enhanced signal
            self.enhanced_signals[f"{symbol}_{datetime.now(timezone.utc).timestamp()}"] = enhanced
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing signal: {e}")
            return signal
    
    def _calculate_optimal_entry(self, signal: Dict, current_price: float, orderbook: Dict) -> float:
        """
        Calculate optimal entry price based on orderbook
        """
        try:
            action = signal.get('action', 'BUY')
            
            if action == 'BUY':
                # For buy signals, try to get better entry near bid
                best_bid = orderbook.get('best_bid', current_price)
                spread = orderbook.get('spread', 0)
                
                # Place order slightly above best bid for better fill
                optimal_entry = best_bid + (spread * 0.1)
                
                # Don't exceed current market price
                return min(optimal_entry, current_price)
                
            else:  # SELL
                # For sell signals, try to get better exit near ask
                best_ask = orderbook.get('best_ask', current_price)
                spread = orderbook.get('spread', 0)
                
                # Place order slightly below best ask for better fill
                optimal_entry = best_ask - (spread * 0.1)
                
                # Don't go below current market price
                return max(optimal_entry, current_price)
                
        except Exception as e:
            logger.error(f"Error calculating optimal entry: {e}")
            return current_price
    
    def _analyze_orderbook_support(self, action: str, orderbook: Dict) -> Dict[str, Any]:
        """
        Analyze orderbook support for the trade direction
        """
        try:
            imbalance = orderbook.get('imbalance_ratio', 0.5)
            bid_volume = orderbook.get('bid_volume', 0)
            ask_volume = orderbook.get('ask_volume', 0)
            
            if action == 'BUY':
                # For buy signals, we want more bid support
                support_strength = imbalance  # 0-1, higher is better
                support_level = 'STRONG' if imbalance > 0.65 else 'MODERATE' if imbalance > 0.5 else 'WEAK'
            else:
                # For sell signals, we want more ask pressure
                support_strength = 1 - imbalance  # Inverse for sells
                support_level = 'STRONG' if imbalance < 0.35 else 'MODERATE' if imbalance < 0.5 else 'WEAK'
            
            return {
                'strength': support_strength,
                'level': support_level,
                'bid_volume': bid_volume,
                'ask_volume': ask_volume,
                'imbalance_ratio': imbalance
            }
            
        except Exception as e:
            logger.error(f"Error analyzing orderbook support: {e}")
            return {'strength': 0.5, 'level': 'UNKNOWN'}
    
    def _assess_liquidation_risk(self, liquidations: List[Dict]) -> Dict[str, Any]:
        """
        Assess liquidation risk based on recent liquidations
        """
        try:
            if not liquidations:
                return {'risk_level': 'LOW', 'total_liquidations': 0}
            
            total_liquidated = sum(liq.get('amount_usd', 0) for liq in liquidations)
            long_liquidations = sum(liq.get('amount_usd', 0) for liq in liquidations if liq.get('side') == 'long')
            short_liquidations = sum(liq.get('amount_usd', 0) for liq in liquidations if liq.get('side') == 'short')
            
            # Assess risk level
            if total_liquidated > 5000000:
                risk_level = 'HIGH'
            elif total_liquidated > 1000000:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            return {
                'risk_level': risk_level,
                'total_liquidations': total_liquidated,
                'long_liquidations': long_liquidations,
                'short_liquidations': short_liquidations,
                'liquidation_bias': 'LONG' if long_liquidations > short_liquidations else 'SHORT'
            }
            
        except Exception as e:
            logger.error(f"Error assessing liquidation risk: {e}")
            return {'risk_level': 'UNKNOWN', 'total_liquidations': 0}
    
    def _calculate_enhanced_confidence(self, base_confidence: float, market_data: Dict) -> float:
        """
        Calculate enhanced confidence score based on real-time data
        """
        try:
            confidence = base_confidence
            
            # Adjust based on orderbook imbalance
            orderbook = market_data.get('orderbook', {})
            imbalance = orderbook.get('imbalance_ratio', 0.5)
            
            # Strong imbalance in favor increases confidence
            if abs(imbalance - 0.5) > 0.2:
                confidence += 5
            
            # Recent price momentum
            price_history = market_data.get('price_history', [])
            if len(price_history) >= 10:
                recent_momentum = (price_history[-1] - price_history[-10]) / price_history[-10] * 100
                if abs(recent_momentum) > 1:  # Strong momentum
                    confidence += 3
            
            # Low liquidation risk increases confidence
            recent_liquidations = market_data.get('recent_liquidations', [])
            if len(recent_liquidations) < 3:
                confidence += 2
            
            # Cap confidence at 95
            return min(confidence, 95)
            
        except Exception as e:
            logger.error(f"Error calculating enhanced confidence: {e}")
            return base_confidence
    
    def _calculate_dynamic_stop_loss(self, signal: Dict, current_price: float, price_history: List[float]) -> float:
        """
        Calculate dynamic stop loss based on volatility
        """
        try:
            action = signal.get('action', 'BUY')
            base_stop_loss = signal.get('stop_loss', current_price * 0.98)
            
            # Calculate recent volatility
            if len(price_history) >= 20:
                volatility = np.std(price_history[-20:]) / np.mean(price_history[-20:])
                
                # Adjust stop loss based on volatility
                if action == 'BUY':
                    # Wider stop in high volatility
                    adjustment = 1 - (volatility * 2)
                    dynamic_stop = current_price * max(adjustment, 0.95)
                else:  # SELL
                    adjustment = 1 + (volatility * 2)
                    dynamic_stop = current_price * min(adjustment, 1.05)
                
                # Use the more conservative stop loss
                if action == 'BUY':
                    return min(base_stop_loss, dynamic_stop)
                else:
                    return max(base_stop_loss, dynamic_stop)
            
            return base_stop_loss
            
        except Exception as e:
            logger.error(f"Error calculating dynamic stop loss: {e}")
            return signal.get('stop_loss', current_price * 0.98)
    
    def _calculate_dynamic_take_profit(self, signal: Dict, current_price: float, orderbook: Dict) -> float:
        """
        Calculate dynamic take profit based on orderbook resistance
        """
        try:
            action = signal.get('action', 'BUY')
            base_take_profit = signal.get('take_profit', current_price * 1.03)
            
            # Adjust based on orderbook resistance
            imbalance = orderbook.get('imbalance_ratio', 0.5)
            
            if action == 'BUY':
                # If heavy ask pressure, take profit earlier
                if imbalance < 0.4:
                    adjustment = 0.02  # 2% take profit
                else:
                    adjustment = 0.03  # 3% take profit
                
                return current_price * (1 + adjustment)
                
            else:  # SELL
                # If heavy bid support, take profit earlier
                if imbalance > 0.6:
                    adjustment = 0.02
                else:
                    adjustment = 0.03
                
                return current_price * (1 - adjustment)
                
        except Exception as e:
            logger.error(f"Error calculating dynamic take profit: {e}")
            return signal.get('take_profit', current_price * 1.03)
    
    def _assess_market_conditions(self, market_data: Dict) -> Dict[str, Any]:
        """
        Assess overall market conditions
        """
        try:
            conditions = {
                'volatility': 'NORMAL',
                'trend': 'NEUTRAL',
                'liquidity': 'NORMAL',
                'risk': 'MODERATE'
            }
            
            # Assess volatility
            price_history = market_data.get('price_history', [])
            if len(price_history) >= 20:
                volatility = np.std(price_history[-20:]) / np.mean(price_history[-20:])
                if volatility > 0.05:
                    conditions['volatility'] = 'HIGH'
                elif volatility < 0.01:
                    conditions['volatility'] = 'LOW'
            
            # Assess trend
            if len(price_history) >= 10:
                recent_trend = (price_history[-1] - price_history[-10]) / price_history[-10]
                if recent_trend > 0.02:
                    conditions['trend'] = 'BULLISH'
                elif recent_trend < -0.02:
                    conditions['trend'] = 'BEARISH'
            
            # Assess liquidity
            orderbook = market_data.get('orderbook', {})
            total_volume = orderbook.get('bid_volume', 0) + orderbook.get('ask_volume', 0)
            if total_volume > 1000000:
                conditions['liquidity'] = 'HIGH'
            elif total_volume < 100000:
                conditions['liquidity'] = 'LOW'
            
            return conditions
            
        except Exception as e:
            logger.error(f"Error assessing market conditions: {e}")
            return {'volatility': 'UNKNOWN', 'trend': 'UNKNOWN'}
    
    def get_signal_performance(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for enhanced signal
        """
        return self.signal_performance.get(signal_id)
    
    def update_signal_performance(self, signal_id: str, exit_price: float):
        """
        Update signal performance after exit
        """
        try:
            if signal_id in self.enhanced_signals:
                signal = self.enhanced_signals[signal_id]
                entry_price = signal.get('enhanced_entry', signal.get('original_entry'))
                
                if signal.get('action') == 'BUY':
                    pnl_percent = ((exit_price - entry_price) / entry_price) * 100
                else:
                    pnl_percent = ((entry_price - exit_price) / entry_price) * 100
                
                self.signal_performance[signal_id] = {
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl_percent': pnl_percent,
                    'enhancement_value': pnl_percent - (signal.get('expected_return', 0) * 100),
                    'exit_timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                logger.info(f"📊 Signal {signal_id} performance: {pnl_percent:.2f}%")
                
        except Exception as e:
            logger.error(f"Error updating signal performance: {e}")


# This will be initialized with the WebSocket data manager
realtime_enhancer = None