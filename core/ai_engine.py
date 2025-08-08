"""
AI Engine - Advanced Trading Analysis Narrative Generator
Menggunakan OpenAI GPT-4o untuk menghasilkan narasi analitis berkualitas tinggi
Integrated from OkxCandleTracker for Phase 1 Core Integration
"""

import os
import logging
from typing import Dict, Any, Optional
from .ai_prompt_builder import AIPromptBuilder

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEngine:
    """
    AI Engine untuk menghasilkan narasi analitis profesional dari data teknikal
    Menggunakan OpenAI GPT-4o dengan prompt engineering yang optimal
    """
    
    def __init__(self):
        """Initialize AI Engine with OpenAI client and prompt builder"""
        self.openai_client = None
        self.ai_prompt_builder = AIPromptBuilder()
        
        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                # Import here to avoid dependency issues
                from openai import OpenAI
                self.openai_client = OpenAI(
                    api_key=openai_api_key,
                    timeout=30.0,  # 30 second timeout
                    max_retries=2   # Maximum 2 retries
                )
                logger.info("AI Engine initialized successfully with OpenAI GPT-4o")
            except ImportError:
                logger.warning("OpenAI library not installed - AI Engine will use fallback narratives")
                self.openai_client = None
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            logger.warning("OPENAI_API_KEY not found - AI Engine will use fallback narratives")
    
    def generate_ai_snapshot(self, symbol: str, timeframe: str, analysis_result: Dict[str, Any], 
                           quick_mode: bool = False) -> str:
        """
        Kirim analisa teknikal ke OpenAI GPT dan terima narasi analitis yang realistis.
        GPT tetap menjelaskan arah pasar dan konfluensi meski belum ada sinyal kuat.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC-USDT')
            timeframe: Timeframe (e.g., '1h', '5m')
            analysis_result: Dictionary berisi hasil analisis 7-layer
            quick_mode: Enable quick mode for faster response
            
        Returns:
            String berisi narasi analitis profesional
        """
        
        if not self.openai_client:
            logger.warning("OpenAI client not available. Using fallback narrative.")
            return self._generate_fallback_narrative(symbol, timeframe, analysis_result)
        
        try:
            # Build prompt berdasarkan mode
            if quick_mode:
                confluence_data = analysis_result.get('confluence_summary', {})
                confluence_data['current_price'] = self._get_current_price(analysis_result)
                prompt = self.ai_prompt_builder.build_ultra_quick_prompt(symbol, timeframe, confluence_data)
                max_tokens = 800
            else:
                prompt = self.ai_prompt_builder.build_ai_analysis_prompt(symbol, timeframe, analysis_result)
                max_tokens = 2000
            
            # System prompt yang optimal untuk narasi berkualitas
            system_prompt = self._get_optimized_system_prompt()
            
            # Log the prompt for debugging (optional)
            logger.debug(f"=== GPT PROMPT for {symbol} {timeframe} ===")
            logger.debug(prompt[:200] + "..." if len(prompt) > 200 else prompt)
            
            # Generate analysis menggunakan OpenAI GPT-4o with better error handling
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.4,        # Agak fleksibel biar jawabannya hidup
                    top_p=0.95,
                    frequency_penalty=0.1,
                    presence_penalty=0.0
                )
                
                narrative = response.choices[0].message.content.strip()
                
                # Log the response for debugging (optional)
                logger.debug(f"=== GPT RESPONSE for {symbol} {timeframe} ===")
                logger.debug(narrative[:200] + "..." if len(narrative) > 200 else narrative)
                
                # Validate the response
                if not narrative or len(narrative) < 10:
                    logger.warning(f"Empty or too short AI response for {symbol} {timeframe}")
                    return self._generate_fallback_narrative(symbol, timeframe, analysis_result)
                
                mode = "quick" if quick_mode else "comprehensive"
                logger.info(f"AI narrative generated successfully for {symbol} {timeframe} ({mode} mode)")
                
                return narrative
                
            except Exception as openai_error:
                error_msg = str(openai_error)
                logger.error(f"OpenAI API error for {symbol} {timeframe}: {error_msg}")
                
                # Check if it's a timeout error
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    logger.warning(f"OpenAI API timeout for {symbol} {timeframe}")
                    fallback_msg = f"⏱️ OpenAI API timeout untuk {symbol} {timeframe}. Sistem akan menggunakan analisis fallback."
                    return self._generate_fallback_narrative(symbol, timeframe, analysis_result, fallback_msg)
                else:
                    # Other OpenAI errors
                    return self._generate_fallback_narrative(symbol, timeframe, analysis_result)
            
        except Exception as e:
            logger.error(f"General error generating AI narrative for {symbol} {timeframe}: {str(e)}")
            return self._generate_fallback_narrative(symbol, timeframe, analysis_result)
    
    def _get_optimized_system_prompt(self) -> str:
        """
        System prompt yang dioptimalkan untuk menghasilkan narasi berkualitas tinggi
        """
        return """
Kamu adalah analis teknikal crypto profesional dan objektif dengan pengalaman 10+ tahun di pasar finansial.

TUGAS UTAMA:
- Menjelaskan kondisi pasar berdasarkan analisa teknikal multi-layer (SMC, volume delta, orderbook, RSI, EMA, Fibonacci, open interest, funding rate)
- Memberikan narasi yang informatif, analitis, dan berkualitas tinggi
- Tetap menjelaskan arah pasar dan potensi pergerakan meski sinyal belum terbentuk
- Fokus pada observasi mendalam dan persiapan trader profesional

PRINSIP ANALISIS:
✅ LAKUKAN:
• Jelaskan arah pasar berdasarkan konfluensi teknikal
• Analisis zona-zona penting dan level kritis
• Berikan perspektif berbagai skenario (bullish/bearish/neutral)
• Fokus pada risk management dan probabilitas
• Gunakan terminologi teknikal yang tepat
• Berikan insight mendalam tentang kondisi pasar

❌ JANGAN:
• Memaksakan sinyal BUY/SELL palsu
• Memberikan rekomendasi trading langsung
• Menggunakan bahasa yang terlalu yakin tanpa basis
• Mengabaikan risiko atau uncertainty

GAYA KOMUNIKASI:
- Bahasa Indonesia profesional dan mudah dipahami
- Struktur yang logis dan sistematis
- Gunakan bullet points dan formatting yang rapi
- Berikan reasoning yang jelas untuk setiap analisis
- Fokus pada actionable insights

STRUKTUR NARASI:
1. Executive Summary (bias utama dan confidence level)
2. Analisis Multi-Layer (SMC, Volume, Orderbook, RSI/EMA, Fibonacci, OI/Funding)
3. Skenario Trading (kondisi, entry zones, risk management)
4. Key Levels dan Zona Penting
5. Risk Assessment dan Market Context

Berikan analisis yang komprehensif namun concise, dengan fokus pada kualitas insight daripada kuantitas kata.
"""
    
    def _generate_fallback_narrative(self, symbol: str, timeframe: str, analysis_result: Dict[str, Any], custom_msg: str = None) -> str:
        """
        Generate fallback narrative ketika OpenAI tidak tersedia
        """
        confluence = analysis_result.get('confluence_summary', {})
        consensus = confluence.get('consensus_level', 0)
        overall_signal = confluence.get('overall_signal', 'neutral')
        current_price = self._get_current_price(analysis_result)
        
        # Determine market bias
        if consensus >= 0.7:
            confidence_desc = "High Conviction"
            confluence_desc = "multiple confluences yang align dengan kuat"
        elif consensus >= 0.5:
            confidence_desc = "Moderate Conviction"
            confluence_desc = "beberapa confluences yang supportive"
        else:
            confidence_desc = "Low Conviction"
            confluence_desc = "confluences yang mixed dan belum jelas"
        
        # Add custom message if provided (for timeout situations)
        timeout_notice = ""
        if custom_msg:
            timeout_notice = f"\n⚠️ **NOTICE:** {custom_msg}\n"
        
        narrative = f"""
## 📊 ANALISIS TEKNIKAL {symbol.upper()} ({timeframe})
**Current Price:** ${current_price} | **Bias:** {overall_signal.upper()} | **Confidence:** {confidence_desc}
{timeout_notice}
### 🎯 Executive Summary
Market berada dalam kondisi **{overall_signal}** dengan {confluence_desc}. Tingkat konsensus teknikal menunjukkan {consensus:.1f} yang mengindikasikan {confidence_desc.lower()}.

### 📈 Multi-Layer Analysis
Berdasarkan analisis 7-layer confluence:
• **SMC Analysis:** Struktur pasar menunjukkan {overall_signal} bias
• **Volume Profile:** Volume dan CVD dalam kondisi yang mendukung analisis
• **Orderbook Depth:** Imbalance menunjukkan tekanan {overall_signal}
• **RSI/EMA Confluence:** Indikator momentum aligned dengan bias utama
• **Fibonacci Levels:** Level retracement/extension memberikan zona kunci
• **Open Interest:** Sentiment futures mendukung analisis teknikal
• **Funding Rate:** Kondisi funding menunjukkan sentiment yang sesuai

### 🎯 Trading Scenarios
**Skenario Utama ({overall_signal.upper()}):**
• Entry berdasarkan konfirmasi dari multiple timeframe
• Risk management dengan stop loss yang ketat
• Take profit bertahap di level-level kunci
• Position sizing sesuai dengan conviction level

### ⚠️ Risk Assessment
• Market volatility dalam range normal untuk {timeframe}
• Selalu gunakan risk management yang ketat
• Jangan risk lebih dari 1-2% per trade
• Monitor perubahan sentiment dan kondisi makro

### 📝 Key Observations
Market saat ini memerlukan pendekatan yang hati-hati. Meski bias teknikal menunjukkan {overall_signal}, trader disarankan untuk:
1. Menunggu konfirmasi yang lebih kuat
2. Menggunakan multiple timeframe analysis
3. Fokus pada risk management
4. Siap untuk adaptasi jika kondisi berubah

*Analisis ini berdasarkan data teknikal saat ini dan dapat berubah sesuai perkembangan pasar.*
"""
        
        logger.info(f"Fallback narrative generated for {symbol} {timeframe}")
        return narrative.strip()
    
    def _get_current_price(self, analysis_result: Dict[str, Any]) -> str:
        """Extract current price from analysis result"""
        # Try different possible locations for current price
        if 'current_price' in analysis_result:
            return f"{analysis_result['current_price']:.4f}"
        
        candlestick_data = analysis_result.get('candlestick', [])
        if candlestick_data:
            return f"{candlestick_data[-1].get('close', 0):.4f}"
        
        # Try to get from SMC analysis
        smc_data = analysis_result.get('smc_analysis', {})
        if smc_data and 'current_price' in smc_data:
            return f"{smc_data['current_price']:.4f}"
        
        return "N/A"
    
    def is_available(self) -> bool:
        """Check if AI Engine is available"""
        return self.openai_client is not None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test OpenAI connection"""
        if not self.openai_client:
            return {
                'status': 'error',
                'message': 'OpenAI client not initialized',
                'available': False
            }
        
        try:
            # Simple test with minimal tokens
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'OK' if you can hear me."}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            return {
                'status': 'success',
                'message': 'OpenAI connection successful',
                'available': True,
                'response': response.choices[0].message.content.strip()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'OpenAI connection failed: {str(e)}',
                'available': False
            }

# Convenience functions for backward compatibility
def generate_ai_snapshot(symbol: str, timeframe: str, analysis_result: Dict[str, Any], 
                        quick_mode: bool = False) -> str:
    """
    Convenience function untuk generate AI snapshot
    """
    engine = AIEngine()
    return engine.generate_ai_snapshot(symbol, timeframe, analysis_result, quick_mode)

# Global instance for reuse
_ai_engine_instance = None

def get_ai_engine() -> AIEngine:
    """
    Get singleton instance of AI Engine
    """
    global _ai_engine_instance
    if _ai_engine_instance is None:
        _ai_engine_instance = AIEngine()
    return _ai_engine_instance