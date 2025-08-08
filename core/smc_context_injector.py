"""
🧠 SMC Context Injector - Auto-Inject SMC context ke trading signals
Mengintegrasikan historical SMC structures ke dalam response utama
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SMCContextInjector:
    """Auto-inject SMC context untuk enhanced GPT reasoning"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            from .structure_memory import smc_memory
            self.smc_memory = smc_memory
            self.enabled = True
            self.logger.info("🧠 SMC Context Injector initialized")
        except ImportError:
            self.logger.warning("SMC Memory not available for context injection")
            self.smc_memory = None
            self.enabled = False
    
    def inject_context(self, signal_response: Dict[str, Any], symbol: str = None, timeframe: str = None) -> Dict[str, Any]:
        """
        Auto-inject SMC context ke dalam response trading signal
        
        Args:
            signal_response: Original signal response
            symbol: Trading symbol untuk filter context
            timeframe: Timeframe untuk filter context
            
        Returns:
            Enhanced response dengan SMC context
        """
        if not self.enabled or not self.smc_memory:
            return signal_response
        
        try:
            # Get SMC context
            context = self.smc_memory.get_context()
            summary = self.smc_memory.get_structure_summary()
            
            # Generate heatmap status
            heatmap_status = self._generate_heatmap_status(context, summary)
            
            # Generate contextual reasoning
            contextual_reasoning = self._generate_contextual_reasoning(context, summary, signal_response)
            
            # Inject context ke response
            enhanced_response = {
                **signal_response,
                'smc_context': {
                    'historical_structures': {
                        'last_bos': context.get('last_bos'),
                        'last_choch': context.get('last_choch'),
                        'active_ob_count': len(context.get('last_bullish_ob', [])) + len(context.get('last_bearish_ob', [])),
                        'active_fvg_count': len(context.get('last_fvg', [])),
                        'liquidity_sweep_active': context.get('last_liquidity') is not None
                    },
                    'market_bias': summary.get('market_bias', 'NEUTRAL'),
                    'heatmap_status': heatmap_status,
                    'key_levels': summary.get('key_levels', {}),
                    'contextual_reasoning': contextual_reasoning,
                    'context_confidence': self._calculate_context_confidence(context),
                    'last_updated': context.get('memory_stats', {}).get('last_updated')
                }
            }
            
            self.logger.info(f"✅ SMC context injected for {symbol or 'unknown'} signal")
            return enhanced_response
            
        except Exception as e:
            self.logger.error(f"Failed to inject SMC context: {e}")
            return signal_response
    
    def _generate_heatmap_status(self, context: Dict, summary: Dict) -> str:
        """Generate heatmap status warning/info"""
        try:
            status_parts = []
            
            # Check liquidity levels
            last_liquidity = context.get('last_liquidity')
            if last_liquidity and last_liquidity.get('strength', 0) > 0.7:
                price = last_liquidity.get('sweep_price', 'Unknown')
                direction = last_liquidity.get('direction', 'unknown')
                status_parts.append(f"⚠️ Likuiditas {direction} di {price}")
            
            # Check BOS confirmation
            last_bos = context.get('last_bos')
            if last_bos:
                bos_time = last_bos.get('timestamp')
                if bos_time:
                    try:
                        bos_datetime = datetime.fromisoformat(bos_time.replace('Z', '+00:00'))
                        time_diff = datetime.now() - bos_datetime.replace(tzinfo=None)
                        if time_diff < timedelta(hours=2):
                            status_parts.append(f"📈 BOS {last_bos.get('direction', '')} {int(time_diff.seconds/60)}m ago")
                        else:
                            status_parts.append("⚠️ BOS belum dikonfirmasi ulang")
                    except:
                        status_parts.append("📈 BOS aktif")
            
            # Check Order Block status
            bullish_obs = context.get('last_bullish_ob', [])
            bearish_obs = context.get('last_bearish_ob', [])
            
            untested_obs = []
            for obs in bullish_obs + bearish_obs:
                if obs.get('mitigation_status') == 'untested':
                    untested_obs.append(f"{obs.get('direction', 'OB')} {obs.get('price_level', '')}")
            
            if untested_obs:
                status_parts.append(f"🎯 {len(untested_obs)} OB belum ditest")
            
            # Check FVG status
            fvgs = context.get('last_fvg', [])
            unfilled_fvgs = [fvg for fvg in fvgs if fvg.get('fill_status') == 'unfilled']
            if unfilled_fvgs:
                status_parts.append(f"📊 {len(unfilled_fvgs)} FVG belum terisi")
            
            return ". ".join(status_parts) if status_parts else "✅ Struktur SMC stabil"
            
        except Exception as e:
            self.logger.error(f"Heatmap status generation error: {e}")
            return "⚠️ Status SMC belum tersedia"
    
    def _generate_contextual_reasoning(self, context: Dict, summary: Dict, signal: Dict) -> str:
        """Generate contextual reasoning untuk GPT"""
        try:
            reasoning_parts = []
            
            # Market bias reasoning
            market_bias = summary.get('market_bias', 'NEUTRAL')
            signal_direction = signal.get('signal', '').upper()
            
            if market_bias == signal_direction:
                reasoning_parts.append(f"✅ Signal {signal_direction} sejalan dengan bias SMC {market_bias}")
            elif market_bias != 'NEUTRAL':
                reasoning_parts.append(f"⚠️ Signal {signal_direction} berlawanan dengan bias SMC {market_bias}")
            
            # BOS/CHoCH reasoning
            last_bos = context.get('last_bos')
            if last_bos:
                bos_direction = last_bos.get('direction', '').upper()
                if 'BULL' in bos_direction and signal_direction == 'BUY':
                    reasoning_parts.append("📈 BOS bullish mendukung signal BUY")
                elif 'BEAR' in bos_direction and signal_direction == 'SELL':
                    reasoning_parts.append("📉 BOS bearish mendukung signal SELL")
            
            # Order Block reasoning
            bullish_obs = context.get('last_bullish_ob', [])
            bearish_obs = context.get('last_bearish_ob', [])
            
            if signal_direction == 'BUY' and bullish_obs:
                active_obs = [ob for ob in bullish_obs if ob.get('mitigation_status') == 'active']
                if active_obs:
                    reasoning_parts.append(f"🎯 {len(active_obs)} Bullish OB tersedia untuk support")
            
            if signal_direction == 'SELL' and bearish_obs:
                active_obs = [ob for ob in bearish_obs if ob.get('mitigation_status') == 'active']
                if active_obs:
                    reasoning_parts.append(f"🎯 {len(active_obs)} Bearish OB tersedia untuk resistance")
            
            # Liquidity reasoning
            last_liquidity = context.get('last_liquidity')
            if last_liquidity:
                liq_direction = last_liquidity.get('direction', '').upper()
                liq_strength = last_liquidity.get('strength', 0)
                if liq_strength > 0.8:
                    reasoning_parts.append(f"💧 Strong liquidity sweep {liq_direction} (strength: {liq_strength:.2f})")
            
            return ". ".join(reasoning_parts) if reasoning_parts else "Analisis berdasarkan indikator teknis standar"
            
        except Exception as e:
            self.logger.error(f"Contextual reasoning generation error: {e}")
            return "Context reasoning tidak tersedia"
    
    def _calculate_context_confidence(self, context: Dict) -> float:
        """Calculate confidence score berdasarkan available context"""
        try:
            confidence_factors = []
            
            # BOS/CHoCH availability
            if context.get('last_bos'):
                confidence_factors.append(0.2)
            if context.get('last_choch'):
                confidence_factors.append(0.15)
            
            # Order Blocks availability
            ob_count = len(context.get('last_bullish_ob', [])) + len(context.get('last_bearish_ob', []))
            if ob_count > 0:
                confidence_factors.append(min(0.3, ob_count * 0.1))
            
            # FVG availability
            fvg_count = len(context.get('last_fvg', []))
            if fvg_count > 0:
                confidence_factors.append(min(0.2, fvg_count * 0.05))
            
            # Liquidity availability
            if context.get('last_liquidity'):
                liq_strength = context['last_liquidity'].get('strength', 0)
                confidence_factors.append(liq_strength * 0.15)
            
            # Base confidence
            base_confidence = 0.5
            
            return min(1.0, base_confidence + sum(confidence_factors))
            
        except Exception as e:
            self.logger.error(f"Context confidence calculation error: {e}")
            return 0.5

# Global instance
smc_context_injector = SMCContextInjector()