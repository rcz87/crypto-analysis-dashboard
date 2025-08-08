"""
Signal Engine - Comprehensive Trading Signal Generator
Combines technical indicators, SMC analysis, price action, and market data
Integrated from OkxCandleTracker for Phase 1 Core Integration
"""

import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .professional_smc_analyzer import ProfessionalSMCAnalyzer
from .price_action import PriceActionAnalyzer

class SignalEngine:
    def __init__(self):
        self.smc_analyzer = ProfessionalSMCAnalyzer()
        self.price_action_analyzer = PriceActionAnalyzer()
        
        # Signal weights for different analysis types
        self.weights = {
            'technical_indicators': 0.3,
            'smc_analysis': 0.3,
            'price_action': 0.25,
            'volume_analysis': 0.15
        }
    
    def generate_comprehensive_signals(self, df, symbol: str, timeframe: str,
                                     orderbook: Dict = None, 
                                     open_interest: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive trading signals from all analysis modules"""
        
        if df is None or len(df) < 50:
            return {
                'error': 'Insufficient data for signal generation',
                'min_required': 50,
                'received': len(df) if df is not None else 0
            }
        
        try:
            # Convert DataFrame to list of dictionaries if needed
            if hasattr(df, 'to_dict'):
                data = df.to_dict('records')
            else:
                data = df
            
            # 1. SMC Analysis
            smc_result = self.smc_analyzer.analyze_comprehensive(df, symbol, timeframe)
            smc_signals = self._extract_smc_signals(smc_result)
            
            # 2. Price Action Analysis
            price_action_signals = self._analyze_price_action(data)
            
            # 3. Volume Analysis
            volume_signals = self._analyze_volume(data)
            
            # 4. Technical Indicators Analysis
            technical_signals = self._analyze_technical_indicators(data)
            
            # 5. Orderbook Analysis (if available)
            orderbook_signals = self._analyze_orderbook(orderbook) if orderbook else {}
            
            # 6. Open Interest Analysis (if available)
            oi_signals = self._analyze_open_interest(open_interest) if open_interest else {}
            
            # 7. Generate Final Signal
            final_signal = self._generate_final_signal(
                technical_signals, smc_signals, price_action_signals, 
                volume_signals, orderbook_signals, oi_signals
            )
            
            # 8. Risk Management
            risk_assessment = self._assess_risk(data, final_signal)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'timeframe': timeframe,
                'final_signal': final_signal,
                'risk_assessment': risk_assessment,
                'component_signals': {
                    'technical_indicators': technical_signals,
                    'smc_analysis': smc_signals,
                    'price_action': price_action_signals,
                    'volume_analysis': volume_signals,
                    'orderbook_analysis': orderbook_signals,
                    'open_interest_analysis': oi_signals
                },
                'confidence_score': final_signal.get('confidence', 0),
                'trade_setup': self._generate_trade_setup(final_signal, risk_assessment, data)
            }
            
        except Exception as e:
            logging.error(f"Error generating signals: {str(e)}")
            return {
                'error': f'Signal generation failed: {str(e)}',
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'timeframe': timeframe
            }
    
    def _extract_smc_signals(self, smc_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract SMC signals from professional analyzer result"""
        if not smc_result:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        signals = []
        
        # CHoCH and BOS Signals
        if smc_result.get('choch_bos_signals'):
            for signal in smc_result['choch_bos_signals'][-3:]:  # Last 3 signals
                signals.append({
                    'type': signal.get('type', 'unknown'),
                    'signal': 'buy' if signal.get('direction') == 'bullish' else 'sell',
                    'strength': min(signal.get('strength', 50), 90),
                    'price': signal.get('price', 0)
                })
        
        # Order Block Signals
        if smc_result.get('order_blocks'):
            for ob in smc_result['order_blocks'][-2:]:  # Last 2 order blocks
                ob_type = ob.get('type', 'unknown')
                if 'bullish' in ob_type.lower():
                    signals.append({
                        'type': 'order_block',
                        'signal': 'buy',
                        'strength': min(ob.get('strength', 60), 80),
                        'price': ob.get('price', 0)
                    })
                elif 'bearish' in ob_type.lower():
                    signals.append({
                        'type': 'order_block',
                        'signal': 'sell',
                        'strength': min(ob.get('strength', 60), 80),
                        'price': ob.get('price', 0)
                    })
        
        # FVG Signals
        if smc_result.get('fvg_signals'):
            for fvg in smc_result['fvg_signals'][-2:]:  # Last 2 FVG
                fvg_type = fvg.get('type', 'unknown')
                if 'bullish' in fvg_type.lower():
                    signals.append({
                        'type': 'fvg',
                        'signal': 'buy',
                        'strength': 70,
                        'price': fvg.get('price', 0)
                    })
                elif 'bearish' in fvg_type.lower():
                    signals.append({
                        'type': 'fvg',
                        'signal': 'sell',
                        'strength': 70,
                        'price': fvg.get('price', 0)
                    })
        
        # Calculate overall SMC signal
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        sell_signals = [s for s in signals if s['signal'] == 'sell']
        
        if buy_signals and len(buy_signals) > len(sell_signals):
            avg_strength = np.mean([s['strength'] for s in buy_signals])
            overall_signal = 'buy'
        elif sell_signals and len(sell_signals) > len(buy_signals):
            avg_strength = np.mean([s['strength'] for s in sell_signals])
            overall_signal = 'sell'
        else:
            avg_strength = 0
            overall_signal = 'neutral'
        
        return {
            'signal': overall_signal,
            'strength': avg_strength,
            'components': signals,
            'market_structure': smc_result.get('market_structure', {}),
            'confidence_score': smc_result.get('confidence_score', 0)
        }
    
    def _analyze_price_action(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze price action for signal generation"""
        try:
            price_action_analysis = self.price_action_analyzer.analyze_price_action(data)
            
            if not price_action_analysis:
                return {'signal': 'neutral', 'strength': 0, 'components': []}
            
            signals = []
            
            # Candlestick Pattern Signals
            if 'candlestick_patterns' in price_action_analysis:
                recent_patterns = price_action_analysis['candlestick_patterns'][-3:]
                
                for pattern in recent_patterns:
                    if 'bullish' in pattern.get('type', '').lower():
                        signals.append({
                            'type': f"pattern_{pattern.get('pattern', 'unknown')}",
                            'signal': 'buy',
                            'strength': min(pattern.get('strength', 50), 75)
                        })
                    elif 'bearish' in pattern.get('type', '').lower():
                        signals.append({
                            'type': f"pattern_{pattern.get('pattern', 'unknown')}",
                            'signal': 'sell',
                            'strength': min(pattern.get('strength', 50), 75)
                        })
            
            # Calculate overall price action signal
            buy_signals = [s for s in signals if s['signal'] == 'buy']
            sell_signals = [s for s in signals if s['signal'] == 'sell']
            
            if buy_signals and len(buy_signals) > len(sell_signals):
                avg_strength = np.mean([s['strength'] for s in buy_signals])
                overall_signal = 'buy'
            elif sell_signals and len(sell_signals) > len(buy_signals):
                avg_strength = np.mean([s['strength'] for s in sell_signals])
                overall_signal = 'sell'
            else:
                avg_strength = 0
                overall_signal = 'neutral'
            
            return {
                'signal': overall_signal,
                'strength': avg_strength,
                'components': signals,
                'current_structure': price_action_analysis.get('current_structure', {})
            }
            
        except Exception as e:
            logging.warning(f"Price action analysis failed: {e}")
            return {'signal': 'neutral', 'strength': 0, 'components': []}
    
    def _analyze_volume(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze volume for signal confirmation"""
        if len(data) < 20:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        signals = []
        
        # Volume spike analysis
        recent_volumes = [candle.get('volume', 0) for candle in data[-20:]]
        avg_volume = np.mean(recent_volumes[:-1])
        current_volume = data[-1].get('volume', 0)
        
        if current_volume > avg_volume * 2:
            # High volume suggests strong move
            price_direction = 'buy' if data[-1]['close'] > data[-2]['close'] else 'sell'
            signals.append({
                'type': 'volume_spike',
                'signal': price_direction,
                'strength': min((current_volume / avg_volume) * 20, 80)
            })
        
        # Volume trend analysis
        recent_volume_trend = np.mean(recent_volumes[-5:]) / np.mean(recent_volumes[-10:-5])
        
        if recent_volume_trend > 1.3:
            signals.append({
                'type': 'volume_trend',
                'signal': 'buy' if data[-1]['close'] > data[-5]['close'] else 'sell',
                'strength': min(recent_volume_trend * 30, 70)
            })
        
        # Calculate overall volume signal
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        sell_signals = [s for s in signals if s['signal'] == 'sell']
        
        if buy_signals and len(buy_signals) > len(sell_signals):
            avg_strength = np.mean([s['strength'] for s in buy_signals])
            overall_signal = 'buy'
        elif sell_signals and len(sell_signals) > len(buy_signals):
            avg_strength = np.mean([s['strength'] for s in sell_signals])
            overall_signal = 'sell'
        else:
            avg_strength = 0
            overall_signal = 'neutral'
        
        return {
            'signal': overall_signal,
            'strength': avg_strength,
            'components': signals,
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1
        }
    
    def _analyze_technical_indicators(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze technical indicators for signal generation"""
        signals = []
        
        # Basic RSI calculation
        closes = [candle['close'] for candle in data[-50:]]  # Last 50 closes
        if len(closes) >= 14:
            rsi = self._calculate_rsi(closes)
            
            if rsi < 30:
                signals.append({'type': 'rsi', 'signal': 'buy', 'strength': 70})
            elif rsi > 70:
                signals.append({'type': 'rsi', 'signal': 'sell', 'strength': 70})
        
        # Basic EMA trend
        if len(closes) >= 21:
            ema_21 = self._calculate_ema(closes, 21)
            ema_50 = self._calculate_ema(closes, 50) if len(closes) >= 50 else ema_21
            
            current_price = closes[-1]
            if ema_21 > ema_50 and current_price > ema_21:
                signals.append({'type': 'ema_trend', 'signal': 'buy', 'strength': 60})
            elif ema_21 < ema_50 and current_price < ema_21:
                signals.append({'type': 'ema_trend', 'signal': 'sell', 'strength': 60})
        
        # Calculate overall technical signal
        buy_signals = [s for s in signals if s['signal'] == 'buy']
        sell_signals = [s for s in signals if s['signal'] == 'sell']
        
        if buy_signals and len(buy_signals) > len(sell_signals):
            avg_strength = np.mean([s['strength'] for s in buy_signals])
            overall_signal = 'buy'
        elif sell_signals and len(sell_signals) > len(buy_signals):
            avg_strength = np.mean([s['strength'] for s in sell_signals])
            overall_signal = 'sell'
        else:
            avg_strength = 0
            overall_signal = 'neutral'
        
        return {
            'signal': overall_signal,
            'strength': avg_strength,
            'components': signals
        }
    
    def _analyze_orderbook(self, orderbook: Dict) -> Dict[str, Any]:
        """Analyze orderbook for signal generation"""
        if not orderbook:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])
        
        if not bids or not asks:
            return {'signal': 'neutral', 'strength': 0, 'components': []}
        
        # Calculate bid/ask imbalance
        bid_volume = sum(float(bid[1]) for bid in bids[:5])  # Top 5 bids
        ask_volume = sum(float(ask[1]) for ask in asks[:5])  # Top 5 asks
        
        total_volume = bid_volume + ask_volume
        if total_volume > 0:
            imbalance = (bid_volume - ask_volume) / total_volume * 100
            
            if imbalance > 20:
                return {'signal': 'buy', 'strength': min(imbalance, 80), 'components': []}
            elif imbalance < -20:
                return {'signal': 'sell', 'strength': min(abs(imbalance), 80), 'components': []}
        
        return {'signal': 'neutral', 'strength': 0, 'components': []}
    
    def _analyze_open_interest(self, open_interest: Dict) -> Dict[str, Any]:
        """Analyze open interest for signal generation"""
        # Basic OI analysis - would need more sophisticated implementation
        return {'signal': 'neutral', 'strength': 0, 'components': []}
    
    def _generate_final_signal(self, technical_signals: Dict, smc_signals: Dict, 
                             price_action_signals: Dict, volume_signals: Dict,
                             orderbook_signals: Dict, oi_signals: Dict) -> Dict[str, Any]:
        """Generate final weighted signal"""
        
        # Calculate weighted scores
        scores = {
            'buy': 0,
            'sell': 0,
            'neutral': 0
        }
        
        # Weight each signal type
        signal_types = [
            (technical_signals, self.weights['technical_indicators']),
            (smc_signals, self.weights['smc_analysis']),
            (price_action_signals, self.weights['price_action']),
            (volume_signals, self.weights['volume_analysis'])
        ]
        
        for signals, weight in signal_types:
            signal = signals.get('signal', 'neutral')
            strength = signals.get('strength', 0)
            scores[signal] += (strength / 100) * weight
        
        # Determine final signal
        max_score = max(scores.values())
        final_signal = max(scores, key=scores.get)
        
        # Calculate confidence
        confidence = min(max_score * 100, 100)
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'scores': scores,
            'reasoning': f"Weighted analysis across multiple timeframes and indicators"
        }
    
    def _assess_risk(self, data: List[Dict], final_signal: Dict) -> Dict[str, Any]:
        """Assess risk for the trade setup"""
        current_price = data[-1]['close']
        
        # Calculate ATR for volatility
        atr = self._calculate_atr(data[-20:])
        
        # Risk management based on signal strength
        confidence = final_signal.get('confidence', 0)
        
        if confidence > 75:
            position_size = 2.0  # 2% of portfolio
            stop_loss_atr = 1.5
        elif confidence > 50:
            position_size = 1.5  # 1.5% of portfolio
            stop_loss_atr = 2.0
        else:
            position_size = 1.0  # 1% of portfolio
            stop_loss_atr = 2.5
        
        return {
            'position_size_percentage': position_size,
            'stop_loss_atr_multiplier': stop_loss_atr,
            'risk_level': 'high' if confidence < 50 else 'medium' if confidence < 75 else 'low',
            'atr': atr,
            'volatility': 'high' if atr > current_price * 0.03 else 'medium' if atr > current_price * 0.015 else 'low'
        }
    
    def _generate_trade_setup(self, final_signal: Dict, risk_assessment: Dict, data: List[Dict]) -> Dict[str, Any]:
        """Generate complete trade setup"""
        current_price = data[-1]['close']
        signal = final_signal.get('signal', 'neutral')
        
        if signal == 'neutral':
            return {
                'action': 'HOLD',
                'reason': 'No clear signal detected'
            }
        
        atr = risk_assessment.get('atr', current_price * 0.02)
        stop_loss_multiplier = risk_assessment.get('stop_loss_atr_multiplier', 2.0)
        
        if signal == 'buy':
            stop_loss = current_price - (atr * stop_loss_multiplier)
            take_profit_1 = current_price + (atr * 1.5)
            take_profit_2 = current_price + (atr * 3.0)
            take_profit_3 = current_price + (atr * 4.5)
        else:  # sell
            stop_loss = current_price + (atr * stop_loss_multiplier)
            take_profit_1 = current_price - (atr * 1.5)
            take_profit_2 = current_price - (atr * 3.0)
            take_profit_3 = current_price - (atr * 4.5)
        
        return {
            'action': signal.upper(),
            'entry_price': current_price,
            'stop_loss': stop_loss,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'take_profit_3': take_profit_3,
            'position_size': risk_assessment.get('position_size_percentage', 1.0),
            'risk_reward_ratio': abs(take_profit_1 - current_price) / abs(stop_loss - current_price)
        }
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate EMA"""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_atr(self, data: List[Dict], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(data) < 2:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(data)):
            high = data[i]['high']
            low = data[i]['low']
            prev_close = data[i-1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        if len(true_ranges) < period:
            return np.mean(true_ranges)
        
        return np.mean(true_ranges[-period:])