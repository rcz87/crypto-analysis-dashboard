"""
Enhanced AI Engine - Professional Trading Analysis Narrative Generator
Integrated from OkxCandleTracker with existing system compatibility
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from openai import OpenAI

# Setup logging
logger = logging.getLogger(__name__)

class EnhancedAIEngine:
    """
    Enhanced AI Engine untuk menghasilkan narasi analitis profesional
    Menggunakan OpenAI GPT-4o dengan prompt engineering yang optimal
    Compatible dengan existing system architecture
    """
    
    def __init__(self):
        """Initialize Enhanced AI Engine with OpenAI client"""
        self.openai_client = None
        self.usage_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens': 0,
            'last_request_time': None
        }
        
        # Initialize OpenAI client
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                self.openai_client = OpenAI(
                    api_key=openai_api_key,
                    timeout=30.0,
                    max_retries=2
                )
                logger.info("Enhanced AI Engine initialized with OpenAI GPT-4o")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        else:
            logger.warning("OPENAI_API_KEY not found - Enhanced AI Engine will use fallback narratives")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to OpenAI API"""
        try:
            if self.openai_client:
                # Simple test request
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "Test connection"}],
                    max_tokens=10
                )
                return {
                    'status': 'connected',
                    'service': 'OpenAI GPT-4o',
                    'test_successful': True
                }
            else:
                return {
                    'status': 'fallback_mode',
                    'service': 'Enhanced Fallback Engine',
                    'test_successful': True
                }
        except Exception as e:
            return {
                'status': 'error',
                'service': 'OpenAI GPT-4o',
                'test_successful': False,
                'error': str(e)
            }
    
    def generate_enhanced_analysis(self, symbol: str, analysis_data: Dict[str, Any], 
                                  language: str = "indonesian", quick_mode: bool = False) -> str:
        """
        Generate comprehensive analysis narrative using enhanced AI engine
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC-USDT')
            analysis_data: Dictionary containing comprehensive analysis results
            language: Language for narrative ('indonesian' or 'english')
            quick_mode: Enable quick mode for faster response
            
        Returns:
            String containing professional analysis narrative
        """
        
        self.usage_stats['total_requests'] += 1
        self.usage_stats['last_request_time'] = datetime.now()
        
        if not self.openai_client:
            logger.warning("OpenAI client not available. Using enhanced fallback narrative.")
            return self._generate_enhanced_fallback(symbol, analysis_data, language)
        
        try:
            # Build enhanced prompt from analysis data
            prompt = self._build_enhanced_prompt(symbol, analysis_data, language, quick_mode)
            
            # Configure parameters based on mode
            max_tokens = 1000 if quick_mode else 2000
            system_prompt = self._get_enhanced_system_prompt(language)
            
            # Generate analysis using OpenAI GPT-4o
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.4,
                top_p=0.95,
                frequency_penalty=0.1,
                presence_penalty=0.0
            )
            
            narrative = response.choices[0].message.content
            if narrative:
                narrative = narrative.strip()
            else:
                narrative = ""
            
            # Update usage statistics
            self.usage_stats['successful_requests'] += 1
            if response.usage and response.usage.total_tokens:
                self.usage_stats['total_tokens'] += response.usage.total_tokens
            
            # Validate response
            if not narrative or len(narrative) < 10:
                logger.warning(f"Empty or too short AI response for {symbol}")
                return self._generate_enhanced_fallback(symbol, analysis_data, language)
            
            logger.info(f"Enhanced AI narrative generated successfully for {symbol}")
            return narrative
            
        except Exception as e:
            logger.error(f"Enhanced AI engine error for {symbol}: {str(e)}")
            self.usage_stats['failed_requests'] += 1
            return self._generate_enhanced_fallback(symbol, analysis_data, language)
    
    def generate_ai_snapshot(self, symbol: str, analysis_data: Dict[str, Any], 
                            language: str = "indonesian", quick_mode: bool = False) -> str:
        """Alias for generate_enhanced_analysis - for backward compatibility"""
        return self.generate_enhanced_analysis(symbol, analysis_data, language, quick_mode)
    
    def _build_enhanced_prompt(self, symbol: str, analysis_data: Dict[str, Any], 
                              language: str, quick_mode: bool) -> str:
        """Build enhanced prompt from real analysis data"""
        
        # Extract real market data
        current_price = analysis_data.get('current_price', 0)
        price_change = analysis_data.get('price_change_24h', 0)
        volume_ratio = analysis_data.get('volume_ratio', 1.0)
        timeframe = analysis_data.get('timeframe', '1H')
        
        # Extract SMC signals
        smc_signals = analysis_data.get('smc_signals', {})
        confluence_score = analysis_data.get('confluence_score', 0)
        market_structure = analysis_data.get('market_structure', {})
        
        # Extract technical data  
        smc_analysis = analysis_data.get('smc_analysis', {})
        technical_indicators = analysis_data.get('technical_indicators', {})
        
        # Build comprehensive prompt
        mode_instruction = "singkat dan fokus" if quick_mode else "mendalam dan komprehensif"
        
        prompt = f"""
=== ANALISIS PROFESIONAL {symbol} ===

**DATA PASAR REAL-TIME:**
- Harga Saat Ini: ${current_price:,.2f}
- Perubahan 24H: {price_change:+.2f}%
- Volume Ratio: {volume_ratio:.2f}x (vs rata-rata)
- Timeframe: {timeframe}

**SINYAL SMART MONEY CONCEPT:**
- Break of Structure (BOS): {'✅ TERDETEKSI' if smc_signals.get('bos_detected') else '❌ TIDAK TERDETEKSI'}
- Change of Character (CHoCH): {'✅ TERDETEKSI' if smc_signals.get('choch_detected') else '❌ TIDAK TERDETEKSI'}
- Fair Value Gap: {'✅ Ada di zona ' + str(smc_signals.get('fvg_zone')) if smc_signals.get('fvg_zone') else '❌ TIDAK ADA'}
- Order Block: {'✅ Teridentifikasi di $' + str(smc_signals.get('order_block')) if smc_signals.get('order_block') else '❌ TIDAK TERDETEKSI'}
- Liquidity Sweep: {'✅ TERJADI' if smc_signals.get('liquidity_sweep') else '❌ TIDAK TERJADI'}

**STRUKTUR PASAR:**
- Tipe Struktur: {market_structure.get('structure_type', 'tidak jelas').upper()}
- Konsistensi Trend: {'KUAT' if market_structure.get('trend_consistency') else 'LEMAH'}
- Recent High: ${market_structure.get('recent_high', 0):,.2f}
- Recent Low: ${market_structure.get('recent_low', 0):,.2f}

**SKOR KONFLUENSI: {confluence_score}/100**

Berikan analisis {mode_instruction} dalam bahasa Indonesian yang mencakup:

1. **EXECUTIVE SUMMARY** (Bias utama dan confidence level berdasarkan data real)
2. **ANALISIS STRUKTUR PASAR** (Berdasarkan SMC signals yang terdeteksi)
3. **KONDISI VOLUME & MOMENTUM** (Interpretasi volume ratio dan price change)
4. **LEVEL KRITIS & ZONA PENTING** (Support/resistance berdasarkan data)
5. **BIAS TRADING & SKENARIO** (Setup potensial berdasarkan konfluensi)
6. **RISK MANAGEMENT** (Berdasarkan kondisi pasar saat ini)

CATATAN PENTING:
- Gunakan data REAL yang disediakan, jangan buat asumsi
- Fokus pada analisis FAKTUAL berdasarkan SMC signals
- Berikan confidence level yang realistis
- Jelaskan WHY analysis ini valid atau tidak valid
- Gunakan terminologi SMC yang tepat dan profesional
"""
        
        return prompt.strip()
        
        # Get current price
        current_price = analysis_data.get('current_price', 0)
        
        # Build comprehensive prompt
        if quick_mode:
            prompt = f"""
=== QUICK ANALYSIS REQUEST ===

**{symbol.upper()} Analysis**
**Price: ${current_price:,.2f}**
**Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**

Market Structure: {smc_analysis.get('market_structure', {}).get('trend', 'neutral')}
RSI: {technical_indicators.get('rsi', {}).get('value', 'N/A')}
EMA Trend: {technical_indicators.get('ema', {}).get('trend', 'N/A')}
Volume: {technical_indicators.get('volume', {}).get('current', 'N/A')}
Signal: {signals.get('action', 'HOLD')}
Confidence: {signals.get('confidence', 0):.1f}%

Berikan analisis singkat dalam bahasa {language} yang mencakup:
1. Kondisi pasar saat ini
2. Level-level penting
3. Bias trading
4. Risk management
"""
        else:
            prompt = f"""
=== COMPREHENSIVE ANALYSIS REQUEST ===

**{symbol.upper()} Professional Analysis**
**Current Price: ${current_price:,.2f}**
**Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**

## Smart Money Concepts Analysis
Market Structure: {smc_analysis.get('market_structure', {}).get('trend', 'neutral')}
Swing Points: {len(smc_analysis.get('swing_points', {}).get('swing_highs', []))} highs, {len(smc_analysis.get('swing_points', {}).get('swing_lows', []))} lows
SMC Patterns: {smc_analysis.get('smc_summary', {})}

## Technical Indicators
RSI: {technical_indicators.get('rsi', {}).get('value', 'N/A')} ({"Overbought" if technical_indicators.get('rsi', {}).get('overbought') else "Oversold" if technical_indicators.get('rsi', {}).get('oversold') else "Normal"})
EMA Trend: {technical_indicators.get('ema', {}).get('trend', 'N/A')}
MACD: {technical_indicators.get('macd', {}).get('macd', 'N/A')} ({"Bullish" if technical_indicators.get('macd', {}).get('bullish') else "Bearish"})
Volume: {technical_indicators.get('volume', {}).get('current', 'N/A')} ({"Above Average" if technical_indicators.get('volume', {}).get('above_average') else "Below Average"})

## Trading Signals
Action: {signals.get('action', 'HOLD')}
Confidence: {signals.get('confidence', 0):.1f}%
Entry Price: {signals.get('entry_price', 'N/A')}
Stop Loss: {signals.get('stop_loss', 'N/A')}
Take Profit: {signals.get('take_profit', 'N/A')}

## Confluence Analysis
Level: {confluence.get('confluence_level', 'N/A')}
Score: {confluence.get('confluence_score', 0):.2f}
Supporting Indicators: {confluence.get('supporting_indicators', [])}

Berikan analisis komprehensif dalam bahasa {language} yang mencakup:
1. Executive Summary & Market Bias
2. Smart Money Concepts Analysis
3. Technical Indicators Breakdown
4. Trading Strategy & Levels
5. Risk Management & Scenarios
6. Key Levels & Zones
"""
        
        return prompt
    
    def _get_enhanced_system_prompt(self, language: str) -> str:
        """Get enhanced system prompt for professional analysis"""
        
        if language == "english":
            return """
You are a professional cryptocurrency technical analyst with 15+ years of experience in institutional trading.

CORE EXPERTISE:
- Smart Money Concepts (SMC) analysis
- Multi-timeframe technical analysis  
- Risk management and position sizing
- Market structure interpretation
- Volume and momentum analysis

ANALYSIS APPROACH:
✅ ALWAYS:
• Base analysis ONLY on provided real market data
• Use factual SMC concepts (BOS, CHoCH, FVG, Order Blocks, Liquidity Sweeps)
• Explain WHY each conclusion is valid based on data
• Provide realistic confidence levels
• Focus on risk management
• Use professional terminology correctly

❌ NEVER:
• Make up data or assume information not provided
• Give direct buy/sell recommendations
• Use overly confident language without supporting data
• Ignore risk factors or market uncertainty

OUTPUT FORMAT:
1. Executive Summary (2-3 sentences, main bias)
2. Market Structure Analysis (based on SMC signals)
3. Volume & Momentum Assessment  
4. Key Levels & Zones
5. Trading Bias & Scenarios
6. Risk Management Notes

Keep analysis factual, professional, and actionable.
"""
        else:
            return """
Anda adalah analis teknikal crypto profesional dengan pengalaman 15+ tahun di trading institusional.

KEAHLIAN INTI:
- Analisis Smart Money Concepts (SMC)
- Analisis teknikal multi-timeframe
- Risk management dan position sizing
- Interpretasi struktur pasar
- Analisis volume dan momentum

PENDEKATAN ANALISIS:
✅ SELALU:
• Dasarkan analisis HANYA pada data pasar real yang diberikan
• Gunakan konsep SMC yang faktual (BOS, CHoCH, FVG, Order Blocks, Liquidity Sweeps)
• Jelaskan MENGAPA setiap kesimpulan valid berdasarkan data
• Berikan confidence level yang realistis
• Fokus pada risk management
• Gunakan terminologi profesional dengan benar

❌ JANGAN PERNAH:
• Membuat data atau asumsi informasi yang tidak disediakan
• Memberikan rekomendasi buy/sell langsung
• Gunakan bahasa terlalu yakin tanpa data pendukung
• Abaikan faktor risiko atau ketidakpastian pasar

FORMAT OUTPUT:
1. Executive Summary (2-3 kalimat, bias utama)
2. Analisis Struktur Pasar (berdasarkan sinyal SMC)
3. Penilaian Volume & Momentum
4. Level & Zona Kunci
5. Bias Trading & Skenario
6. Catatan Risk Management

Tetap faktual, profesional, dan actionable dalam analisis.
"""
    
    def _generate_enhanced_fallback(self, symbol: str, analysis_data: Dict[str, Any], 
                                   language: str) -> str:
        """Generate enhanced fallback narrative when AI is unavailable"""
        
        current_price = analysis_data.get('current_price', 0)
        price_change = analysis_data.get('price_change_24h', 0)
        volume_ratio = analysis_data.get('volume_ratio', 1.0)
        confluence_score = analysis_data.get('confluence_score', 0)
        smc_signals = analysis_data.get('smc_signals', {})
        
        if language == "english":
            return f"""
## TECHNICAL ANALYSIS - {symbol.upper()}

**MARKET DATA:**
Current Price: ${current_price:,.2f} ({price_change:+.2f}% 24h)
Volume: {volume_ratio:.1f}x average
Confluence Score: {confluence_score}/100

**SMC SIGNALS:**
- BOS: {'Detected' if smc_signals.get('bos_detected') else 'Not Detected'}
- CHoCH: {'Detected' if smc_signals.get('choch_detected') else 'Not Detected'}
- FVG: {'Present' if smc_signals.get('fvg_zone') else 'None'}
- Order Block: {'Active' if smc_signals.get('order_block') else 'None'}
- Liquidity Sweep: {'Occurred' if smc_signals.get('liquidity_sweep') else 'None'}

**ANALYSIS:**
Market shows {confluence_score}% confluence based on SMC signals. 
{'Strong setup with multiple confirmations.' if confluence_score >= 70 else 'Moderate setup, wait for more confirmation.' if confluence_score >= 50 else 'Weak setup, avoid entry.'}

**RISK MANAGEMENT:**
Use proper position sizing and stop losses based on market structure.

Note: Enhanced AI analysis temporarily unavailable.
"""
        else:
            return f"""
## ANALISIS TEKNIKAL - {symbol.upper()}

**DATA PASAR:**
Harga Saat Ini: ${current_price:,.2f} ({price_change:+.2f}% 24j)
Volume: {volume_ratio:.1f}x rata-rata  
Skor Konfluensi: {confluence_score}/100

**SINYAL SMC:**
- BOS: {'Terdeteksi' if smc_signals.get('bos_detected') else 'Tidak Terdeteksi'}
- CHoCH: {'Terdeteksi' if smc_signals.get('choch_detected') else 'Tidak Terdeteksi'}
- FVG: {'Ada' if smc_signals.get('fvg_zone') else 'Tidak Ada'}
- Order Block: {'Aktif' if smc_signals.get('order_block') else 'Tidak Ada'}
- Liquidity Sweep: {'Terjadi' if smc_signals.get('liquidity_sweep') else 'Tidak Terjadi'}

**ANALISIS:**
Pasar menunjukkan konfluensi {confluence_score}% berdasarkan sinyal SMC.
{'Setup kuat dengan beberapa konfirmasi.' if confluence_score >= 70 else 'Setup sedang, tunggu konfirmasi lebih.' if confluence_score >= 50 else 'Setup lemah, hindari entry.'}

**RISK MANAGEMENT:**
Gunakan position sizing yang tepat dan stop loss berdasarkan struktur pasar.

Catatan: Analisis AI enhanced sementara tidak tersedia.
"""
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get AI engine usage statistics"""
        return {
            'total_requests': self.usage_stats['total_requests'],
            'successful_requests': self.usage_stats['successful_requests'],
            'failed_requests': self.usage_stats['failed_requests'],
            'success_rate': (self.usage_stats['successful_requests'] / max(1, self.usage_stats['total_requests'])) * 100,
            'total_tokens': self.usage_stats['total_tokens'],
            'last_request_time': self.usage_stats['last_request_time'],
            'ai_available': self.openai_client is not None
        }
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """Test AI connection and return status"""
        if not self.openai_client:
            return {
                'status': 'unavailable',
                'message': 'OpenAI client not initialized',
                'ai_available': False
            }
        
        try:
            # Test with simple request
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'AI connection test successful'"}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            return {
                'status': 'connected',
                'message': 'AI connection test successful',
                'ai_available': True,
                'response': response.choices[0].message.content.strip() if response.choices[0].message.content else ""
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'AI connection test failed: {str(e)}',
                'ai_available': False
            }