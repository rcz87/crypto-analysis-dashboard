# core/signal_generator.py
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SignalGenerator:
    """
    Signal Generator untuk menghasilkan sinyal trading dari data teknikal
    """
    
    def __init__(self):
        logger.info("Signal Generator initialized")
    
    def generate_signal(self, market_data: Dict[str, Any], smc_result: Dict[str, Any], is_concise: bool = True) -> Dict[str, Any]:
        """
        Generate signal dari market data dan hasil analisis SMC
        
        Args:
            market_data: Dictionary berisi data pasar (candles)
            smc_result: Dictionary berisi hasil analisis SMC
            is_concise: Jika True, hanya berikan informasi inti (untuk sinyal tajam)
            
        Returns:
            Dictionary berisi sinyal trading
        """
        try:
            # Extract data from market_data
            candles = market_data.get('candles', [])
            if not candles:
                return {"error": "No candle data available"}
            
            # Ekstrak data dari hasil SMC
            market_structure = smc_result.get('market_structure', 'NEUTRAL')
            trend_bias = smc_result.get('trend_bias', 'NEUTRAL')
            
            # Current price dari candle terakhir
            current_price = float(candles[-1]['close'])
            
            # Penentuan bias utama (dari kombinasi market structure dan trend bias)
            # Dalam implementasi nyata, ini bisa lebih kompleks dengan perhitungan indikator, dsb.
            bias = 'NEUTRAL'
            if market_structure == 'BULLISH' and trend_bias == 'BULLISH':
                bias = 'BULLISH'
            elif market_structure == 'BEARISH' and trend_bias == 'BEARISH':
                bias = 'BEARISH'
            elif market_structure == 'BULLISH' and trend_bias != 'BEARISH':
                bias = 'MODERATELY_BULLISH'
            elif market_structure == 'BEARISH' and trend_bias != 'BULLISH':
                bias = 'MODERATELY_BEARISH'
            
            # Strength: nilai 0-1 yang menunjukkan kekuatan sinyal
            # Seharusnya dihitung dari berbagai indikator dan konfluensi
            strength = 0.0
            if bias in ['BULLISH', 'BEARISH']:
                strength = 0.8
            elif bias in ['MODERATELY_BULLISH', 'MODERATELY_BEARISH']:
                strength = 0.6
            else:
                strength = 0.3
            
            # Action yang direkomendasikan
            action = 'WAIT'
            if bias == 'BULLISH' and strength >= 0.7:
                action = 'BUY'
            elif bias == 'BEARISH' and strength >= 0.7:
                action = 'SELL'
            elif bias == 'MODERATELY_BULLISH' and strength >= 0.6:
                action = 'CONSIDER_BUY'
            elif bias == 'MODERATELY_BEARISH' and strength >= 0.6:
                action = 'CONSIDER_SELL'
            
            # Confidence: seberapa yakin dengan sinyal ini
            confidence = strength * 0.9  # Slightly lower than strength
            
            # Entry zone
            # Dalam implementasi nyata, ini bisa dihitung dari support/resistance, OB, dsb.
            entry_low = current_price * 0.98
            entry_high = current_price * 1.02
            
            # Stop loss dan take profit
            # Dalam implementasi nyata, ini juga dihitung dari level kunci, volatilitas, dsb.
            stop_loss = current_price * 0.95 if bias in ['BULLISH', 'MODERATELY_BULLISH'] else current_price * 1.05
            take_profit = current_price * 1.1 if bias in ['BULLISH', 'MODERATELY_BULLISH'] else current_price * 0.9
            
            # Key drivers (alasan utama untuk sinyal)
            key_drivers = []
            if market_structure == 'BULLISH':
                key_drivers.append("Bullish market structure")
            if trend_bias == 'BULLISH':
                key_drivers.append("Bullish trend bias")
            if market_structure == 'BEARISH':
                key_drivers.append("Bearish market structure")
            if trend_bias == 'BEARISH':
                key_drivers.append("Bearish trend bias")
            
            # Add default driver if empty
            if not key_drivers:
                key_drivers.append("Mixed signals, no clear bias")
            
            # Buat signal result
            signal_result = {
                "bias": bias,
                "strength": strength,
                "action": action,
                "confidence": confidence,
                "entry_low": entry_low,
                "entry_high": entry_high,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "key_drivers": key_drivers,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Tambahkan data lebih lengkap jika tidak concise
            if not is_concise:
                # Tambahan untuk sinyal yang lebih lengkap
                signal_result.update({
                    "market_structure": market_structure,
                    "trend_bias": trend_bias,
                    "risk_reward": (take_profit - current_price) / (current_price - stop_loss) if bias in ['BULLISH', 'MODERATELY_BULLISH'] else (current_price - take_profit) / (stop_loss - current_price),
                    "volatility": "NORMAL",  # Bisa dihitung dari ATR atau stdev
                    "trend_strength": 0.7,  # Bisa dihitung dari ADX atau slope
                    "indicators": {
                        "rsi": 55,  # Mock values
                        "macd": "BULLISH",
                        "ema_alignment": "BULLISH",
                        "atr": 120
                    },
                    "confluence": {
                        "overall_score": 7,
                        "technical_alignment": 0.7,
                        "overall_signal": bias
                    }
                })
            
            return signal_result
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return {
                "error": f"Failed to generate signal: {str(e)}",
                "bias": "NEUTRAL",
                "action": "WAIT",
                "strength": 0,
                "confidence": 0
            }
    
    def generate_enhanced_signal(self, market_data: Dict[str, Any], smc_result: Dict[str, Any], 
                               additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate enhanced signal dengan data tambahan (news, multi-timeframe)
        
        Args:
            market_data: Dictionary berisi data pasar (candles)
            smc_result: Dictionary berisi hasil analisis SMC
            additional_data: Dictionary berisi data tambahan (news, multi-timeframe)
            
        Returns:
            Dictionary berisi sinyal trading yang lebih lengkap
        """
        try:
            # Get basic signal first
            base_signal = self.generate_signal(market_data, smc_result, is_concise=False)
            
            if 'error' in base_signal:
                return base_signal
            
            # Extract data tambahan jika ada
            news_data = additional_data.get('news', {}) if additional_data else {}
            mtf_data = additional_data.get('multi_timeframe', {}) if additional_data else {}
            
            # Extract bias dari base signal
            base_bias = base_signal['bias']
            base_strength = base_signal['strength']
            
            # Adjustment berdasarkan news sentiment
            adjusted_strength = base_strength
            news_impact = 0
            
            if news_data:
                sentiment = news_data.get('sentiment', 'NEUTRAL')
                confidence = news_data.get('confidence', 0.5)
                
                if sentiment == 'BULLISH' and base_bias in ['BULLISH', 'MODERATELY_BULLISH']:
                    # Bullish news + bullish technical = stronger signal
                    news_impact = 0.1 * confidence
                    adjusted_strength += news_impact
                elif sentiment == 'BEARISH' and base_bias in ['BEARISH', 'MODERATELY_BEARISH']:
                    # Bearish news + bearish technical = stronger signal
                    news_impact = 0.1 * confidence
                    adjusted_strength += news_impact
                elif sentiment == 'BULLISH' and base_bias in ['BEARISH', 'MODERATELY_BEARISH']:
                    # Bullish news + bearish technical = weaker signal
                    news_impact = -0.1 * confidence
                    adjusted_strength += news_impact
                elif sentiment == 'BEARISH' and base_bias in ['BULLISH', 'MODERATELY_BULLISH']:
                    # Bearish news + bullish technical = weaker signal
                    news_impact = -0.1 * confidence
                    adjusted_strength += news_impact
            
            # Ensure strength is within valid range
            adjusted_strength = max(0, min(1, adjusted_strength))
            
            # Adjustment berdasarkan multi-timeframe alignment
            mtf_alignment = 'NEUTRAL'
            mtf_impact = 0
            
            if mtf_data:
                # Count bias tendencies across timeframes
                bullish_count = 0
                bearish_count = 0
                total_count = len(mtf_data)
                
                for tf, tf_data in mtf_data.items():
                    tf_bias = tf_data.get('trend_bias', 'NEUTRAL')
                    if tf_bias == 'BULLISH':
                        bullish_count += 1
                    elif tf_bias == 'BEARISH':
                        bearish_count += 1
                
                # Determine alignment
                if bullish_count > bearish_count and bullish_count > total_count / 2:
                    mtf_alignment = 'BULLISH'
                    if base_bias in ['BULLISH', 'MODERATELY_BULLISH']:
                        mtf_impact = 0.15  # Strong positive impact
                    else:
                        mtf_impact = -0.1  # Negative impact (conflicting bias)
                elif bearish_count > bullish_count and bearish_count > total_count / 2:
                    mtf_alignment = 'BEARISH'
                    if base_bias in ['BEARISH', 'MODERATELY_BEARISH']:
                        mtf_impact = 0.15  # Strong positive impact
                    else:
                        mtf_impact = -0.1  # Negative impact (conflicting bias)
                else:
                    mtf_alignment = 'MIXED'
                    mtf_impact = -0.05  # Slight negative impact (unclear direction)
            
            # Final adjusted strength
            final_strength = max(0, min(1, adjusted_strength + mtf_impact))
            
            # Update confidence based on adjusted strength
            final_confidence = final_strength * 0.9
            
            # Update action based on final strength
            final_action = 'WAIT'
            if base_bias == 'BULLISH' and final_strength >= 0.7:
                final_action = 'BUY'
            elif base_bias == 'BEARISH' and final_strength >= 0.7:
                final_action = 'SELL'
            elif base_bias == 'MODERATELY_BULLISH' and final_strength >= 0.6:
                final_action = 'CONSIDER_BUY'
            elif base_bias == 'MODERATELY_BEARISH' and final_strength >= 0.6:
                final_action = 'CONSIDER_SELL'
            
            # Risk assessment
            risk_level = 'MEDIUM'
            market_conditions = 'NORMAL'
            position_size_adjustment = 1.0
            
            # High impact news increases risk
            if news_data.get('high_impact_count', 0) >= 2:
                risk_level = 'HIGH'
                market_conditions = 'VOLATILE'
                position_size_adjustment = 0.7
            
            # Conflicting MTF reduces position size
            if mtf_alignment == 'MIXED' or (mtf_alignment != 'NEUTRAL' and mtf_alignment != base_bias):
                position_size_adjustment *= 0.8
            
            # Confluence factors
            confluence_factors = base_signal.get('key_drivers', []).copy()
            
            if news_impact > 0:
                confluence_factors.append(f"{news_data.get('sentiment', 'NEUTRAL')} news sentiment supporting bias")
            elif news_impact < 0:
                confluence_factors.append(f"Conflicting news sentiment")
            
            if mtf_impact > 0:
                confluence_factors.append(f"Multi-timeframe alignment: {mtf_alignment}")
            elif mtf_impact < 0:
                confluence_factors.append(f"Conflicting higher timeframe bias")
            
            # Update take profit levels to multiple targets
            current_price = float(market_data['candles'][-1]['close'])
            is_bullish = base_bias in ['BULLISH', 'MODERATELY_BULLISH']
            base_tp = base_signal['take_profit']
            
            take_profit_levels = [
                base_tp,  # Original TP
                current_price * 1.15 if is_bullish else current_price * 0.85,  # Extended TP
                current_price * 1.25 if is_bullish else current_price * 0.75   # Stretch target
            ]
            
            # Create enhanced signal result
            enhanced_signal = base_signal.copy()
            enhanced_signal.update({
                "strength": final_strength,
                "confidence": final_confidence,
                "action": final_action,
                "take_profit": take_profit_levels,
                "mtf_alignment": mtf_alignment,
                "news_impact": news_impact,
                "mtf_impact": mtf_impact,
                "risk_level": risk_level,
                "market_conditions": market_conditions,
                "position_size_adjustment": position_size_adjustment,
                "risk_comments": f"Adjust position size to {position_size_adjustment:.1f}x normal due to current conditions",
                "confluence_factors": confluence_factors
            })
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"Error generating enhanced signal: {e}")
            return {
                "error": f"Failed to generate enhanced signal: {str(e)}",
                "bias": "NEUTRAL",
                "action": "WAIT",
                "strength": 0,
                "confidence": 0
            }
