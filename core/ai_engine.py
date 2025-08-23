"""
AI Engine - Production Ready for VPS Hostinger
Simplified but powerful AI analysis for deployment
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AIEngine:
    """AI Engine optimized for VPS deployment with fallback support"""
    
    def __init__(self):
        self.openai_client = None
        
        # Initialize OpenAI client if available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(
                    api_key=openai_api_key,
                    timeout=15.0,  # Shorter timeout for VPS
                    max_retries=1   # Reduced retries for faster response
                )
                logger.info("AI Engine initialized with OpenAI GPT-5")
            except ImportError:
                logger.warning("OpenAI library not available - using fallback narratives")
            except Exception as e:
                logger.error(f"OpenAI initialization failed: {e}")
        else:
            logger.info("No OpenAI API key - using fallback narratives")
    
    def is_available(self) -> bool:
        """Check if AI engine is available"""
        return self.openai_client is not None
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """Test AI engine connection"""
        return {
            "available": self.is_available(),
            "status": "connected" if self.is_available() else "fallback",
            "client": "OpenAI GPT-5" if self.is_available() else "Basic fallback"
        }
    
    def generate_ai_snapshot(self, symbol: str, timeframe: str, analysis_data: Dict[str, Any]) -> str:
        """Generate AI snapshot/narrative"""
        if self.openai_client:
            try:
                signal_result = analysis_data.get('signal_result', {})
                smc_analysis = analysis_data.get('smc_analysis', {})
                
                prompt = f"""Generate a professional trading analysis for {symbol} {timeframe}:
                
Signal: {signal_result.get('bias', 'NEUTRAL')}
Confidence: {signal_result.get('confidence', 0)}%
Market Structure: {smc_analysis.get('market_bias', 'neutral')}

Provide concise Indonesian analysis focusing on key trading insights."""

                response = self.openai_client.chat.completions.create(
                    model="gpt-5",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                return content.strip() if content else ""
                
            except Exception as e:
                logger.error(f"AI snapshot generation error: {e}")
                fallback_signal = analysis_data.get('signal_result', {})
                bias = fallback_signal.get('bias', 'neutral') if fallback_signal else 'neutral'
                confidence = fallback_signal.get('confidence', 0) if fallback_signal else 0
                return f"Analisis {symbol} menunjukkan kondisi market {bias} dengan confidence {confidence}%."
        
        # Fallback narrative
        signal_result = analysis_data.get('signal_result', {})
        bias = signal_result.get('bias', 'neutral') if signal_result else 'neutral'
        confidence = signal_result.get('confidence', 0) if signal_result else 0
        return f"Analisis {symbol} menunjukkan kondisi market {bias} dengan confidence {confidence}%."
    
    def generate_trading_narrative(self, symbol: str, timeframe: str, 
                                 market_data: Dict[str, Any], 
                                 smc_analysis: Optional[Dict[str, Any]] = None,
                                 signal: Optional[Dict[str, Any]] = None) -> str:
        """Generate trading narrative for the signal"""
        
        try:
            if self.openai_client and signal:
                return self._generate_ai_narrative(symbol, timeframe, market_data, smc_analysis, signal)
            else:
                return self._generate_fallback_narrative(symbol, timeframe, market_data, smc_analysis, signal)
                
        except Exception as e:
            logger.error(f"Narrative generation error: {e}")
            return self._generate_fallback_narrative(symbol, timeframe, market_data, smc_analysis, signal)
    
    def _generate_ai_narrative(self, symbol: str, timeframe: str, 
                             market_data: Dict[str, Any],
                             smc_analysis: Optional[Dict[str, Any]],
                             signal: Dict[str, Any]) -> str:
        """Generate AI-powered narrative using OpenAI"""
        
        try:
            # Build prompt for GPT
            current_price = signal.get('entry_price', 0)
            direction = signal.get('direction', 'HOLD')
            confidence = signal.get('confidence', 0)
            
            smc_bias = smc_analysis.get('market_bias', 'neutral') if smc_analysis else 'neutral'
            structure_break = smc_analysis.get('structure_analysis', {}).get('structure_break', 'none') if smc_analysis else 'none'
            
            prompt = f"""Analyze this cryptocurrency trading setup in Indonesian:

Symbol: {symbol}
Timeframe: {timeframe}
Current Price: {current_price}
Signal Direction: {direction}
Confidence: {confidence:.2f}

SMC Analysis:
- Market Bias: {smc_bias}
- Structure Break: {structure_break}

Please provide a concise professional trading analysis in Indonesian covering:
1. Market structure assessment
2. Entry rationale
3. Risk management
4. Expected outcome

Keep response under 200 words, professional tone."""

            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-5",  # Use GPT-5 for enhanced response
                    messages=[
                        {"role": "system", "content": "You are a professional cryptocurrency trader providing concise market analysis in Indonesian."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                content = response.choices[0].message.content
                return content.strip() if content else "Unable to generate narrative"
            else:
                return self._generate_fallback_narrative(symbol, timeframe, market_data, smc_analysis, signal)
            
        except Exception as e:
            logger.error(f"AI narrative generation failed: {e}")
            return self._generate_fallback_narrative(symbol, timeframe, market_data, smc_analysis, signal)
    
    def _generate_fallback_narrative(self, symbol: str, timeframe: str,
                                   market_data: Dict[str, Any],
                                   smc_analysis: Optional[Dict[str, Any]] = None,
                                   signal: Optional[Dict[str, Any]] = None) -> str:
        """Generate fallback narrative when AI is not available"""
        
        try:
            if not signal:
                return f"Analisis teknikal untuk {symbol} pada timeframe {timeframe} sedang diproses. Silakan coba lagi dalam beberapa saat."
            
            direction = signal.get('direction', 'HOLD')
            confidence = signal.get('confidence', 0)
            entry_price = signal.get('entry_price', 0)
            take_profit = signal.get('take_profit', 0)
            stop_loss = signal.get('stop_loss', 0)
            
            # Build narrative based on direction
            if direction == 'BUY':
                bias_text = "Sinyal BELI teridentifikasi"
                action_text = f"Pertimbangkan entry di level {entry_price:.2f}"
                risk_text = f"Target profit {take_profit:.2f}, stop loss {stop_loss:.2f}"
            elif direction == 'SELL':
                bias_text = "Sinyal JUAL teridentifikasi" 
                action_text = f"Pertimbangkan short di level {entry_price:.2f}"
                risk_text = f"Target profit {take_profit:.2f}, stop loss {stop_loss:.2f}"
            else:
                bias_text = "Sinyal HOLD - tunggu konfirmasi lebih lanjut"
                action_text = "Tidak ada entry point yang jelas saat ini"
                risk_text = "Tunggu breakout atau breakdown yang jelas"
            
            # Add SMC context if available
            smc_text = ""
            if smc_analysis:
                market_bias = smc_analysis.get('market_bias', 'neutral')
                if market_bias == 'bullish':
                    smc_text = "Market structure menunjukkan bias bullish. "
                elif market_bias == 'bearish':
                    smc_text = "Market structure menunjukkan bias bearish. "
                else:
                    smc_text = "Market structure dalam kondisi sideways. "
            
            # Confidence assessment
            if confidence > 0.7:
                conf_text = "Confidence tinggi pada setup ini."
            elif confidence > 0.5:
                conf_text = "Confidence sedang, gunakan position sizing yang hati-hati."
            else:
                conf_text = "Confidence rendah, sebaiknya tunggu konfirmasi tambahan."
            
            narrative = f"""
📊 Analisis {symbol} ({timeframe})

{bias_text} dengan confidence {confidence:.2f}.

🎯 Setup Trading:
{action_text}
{risk_text}

📈 Market Structure:
{smc_text}{conf_text}

⚠️ Risk Management:
Gunakan position sizing yang sesuai dengan risk tolerance Anda. Selalu gunakan stop loss dan jangan over-leverage.
            """.strip()
            
            return narrative
            
        except Exception as e:
            logger.error(f"Fallback narrative generation failed: {e}")
            return f"Analisis untuk {symbol} sedang diproses. Error: {str(e)[:50]}"
    
    def test_connection(self) -> Dict[str, Any]:
        """Test AI engine connection"""
        try:
            if self.openai_client:
                # Simple test
                response = self.openai_client.chat.completions.create(
                    model="gpt-5",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                return {
                    "available": True,
                    "model": "gpt-5",
                    "status": "connected"
                }
            else:
                return {
                    "available": False,
                    "model": "fallback",
                    "status": "using_fallback"
                }
                
        except Exception as e:
            logger.error(f"AI connection test failed: {e}")
            return {
                "available": False,
                "model": "fallback", 
                "status": f"error: {str(e)}"
            }

# Factory function for backward compatibility
def get_ai_engine():
    """Factory function to get AI engine instance"""
    return AIEngine()