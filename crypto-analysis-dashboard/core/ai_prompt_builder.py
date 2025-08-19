"""
AI Prompt Builder - Professional Trading Analysis Prompt Generator
Mengubah hasil analisa internal menjadi prompt teks siap kirim ke OpenAI GPT
Integrated from OkxCandleTracker for Phase 1 Core Integration
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime


class AIPromptBuilder:
    """
    Kelas untuk membentuk prompt AI yang komprehensif dari hasil analisis teknikal 7 layer
    """
    
    def __init__(self):
        self.system_prompt = """
Anda adalah analis trading profesional dengan keahlian dalam:
- Smart Money Concepts (SMC)
- Volume Profile Analysis
- Orderbook & Market Microstructure
- Technical Indicators (RSI, EMA, MACD)
- Fibonacci Analysis
- Open Interest & Funding Rate Analysis
- Risk Management & Position Sizing

Berikan analisis yang:
✅ Faktual dan berdasarkan data
✅ Menggunakan terminologi trading yang tepat
✅ Memberikan level-level konkret
✅ Menyertakan skenario utama dan alternatif
✅ Professional dan actionable
"""
    
    def build_ai_analysis_prompt(self, symbol: str, timeframe: str, analysis_result: Dict[str, Any]) -> str:
        """
        Menerima hasil analisa (dict) dan membentuk prompt teks untuk GPT.
        
        Args:
            symbol: Trading pair (e.g., "BTC-USDT")
            timeframe: Time frame (e.g., "5m", "1h")
            analysis_result: Dictionary berisi hasil analisis 7 layer
            
        Returns:
            String prompt yang siap dikirim ke OpenAI
        """
        
        # Extract analysis data with fallbacks
        smc = self._extract_smc_data(analysis_result.get("smc_analysis", {}))
        volume = self._extract_volume_data(analysis_result.get("volume_analysis", {}))
        indicators = self._extract_indicators_data(analysis_result.get("indicators", {}))
        signals = self._extract_signals_data(analysis_result.get("signals", {}))
        
        # Get current price for context
        current_price = self._get_current_price(analysis_result)
        
        # Build comprehensive prompt
        prompt = f"""
=== TRADING SNAPSHOT ANALYSIS REQUEST ===

**ANALISIS MENDALAM {symbol.upper()} (Timeframe: {timeframe})**
**Current Price: ${current_price}**
**Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC**

Berdasarkan data teknikal berikut, berikan analisis trading profesional:

## 1. 📘 Smart Money Concept (SMC)
{smc}

## 2. 📊 Volume Analysis
{volume}

## 3. 📏 Technical Indicators
{indicators}

## 4. 🎯 Signal Analysis
{signals}

---

## 🎯 INSTRUKSI ANALISIS:

Berikan analisis profesional dalam bahasa Indonesia yang mencakup:

### A. Executive Summary
- Bias utama (bullish/bearish/neutral) dengan reasoning
- Confidence level (1-5 🔵) berdasarkan confluence

### B. Key Levels & Zones
- Support dan resistance utama
- FVG (Fair Value Gap) penting
- SMC zones (Order Blocks, Breaker Blocks)

### C. Market Structure Analysis
- Trend saat ini (Higher High/Lower Low pattern)
- Market phase (accumulation/distribution/markup/markdown)
- Volume confirmation atau divergence

### D. Trading Scenarios

**Skenario Utama:**
- Kondisi yang harus dipenuhi
- Entry strategy dan timing
- Stop Loss placement
- Take Profit targets (TP1, TP2)
- Risk/Reward ratio

**Skenario Alternatif:**
- Kondisi invalidasi skenario utama
- Backup plan dan levels
- Risk management adjustments

### E. Risk Assessment
- Faktor risiko utama
- Market sentiment risks
- Technical risks
- Recommended position size

### F. Execution Notes
- Best entry approach (market/limit order)
- Monitoring points
- Exit strategy refinements
- Time-based considerations

**Format:** Gunakan markdown formatting yang rapi dengan bullet points dan emoji yang sesuai.
**Tone:** Professional trading analyst, factual, actionable.
**Length:** Komprehensif namun concise, fokus pada actionable insights.

=== END ANALYSIS REQUEST ===
"""
        
        return prompt.strip()
    
    def _extract_smc_data(self, smc_analysis: Dict[str, Any]) -> str:
        """Extract SMC analysis data"""
        if not smc_analysis:
            return "Data SMC tidak tersedia untuk analisis."
        
        confidence_score = smc_analysis.get('confidence_score', 0)
        current_price = smc_analysis.get('current_price', 0)
        choch_bos = smc_analysis.get('choch_bos_signals', [])
        order_blocks = smc_analysis.get('order_blocks', [])
        fvg_signals = smc_analysis.get('fvg_signals', [])
        
        smc_text = f"""
📊 Confidence Score: {confidence_score:.1f}%
📈 Current Price: ${current_price:,.2f}
🔄 CHoCH/BOS Signals: {len(choch_bos)} detected
📋 Order Blocks: {len(order_blocks)} identified
💎 FVG Signals: {len(fvg_signals)} detected
"""
        
        if choch_bos:
            smc_text += "\n🔍 Recent CHoCH/BOS:\n"
            for signal in choch_bos[-2:]:  # Last 2 signals
                smc_text += f"   - {signal.get('type', 'Unknown')} {signal.get('direction', 'neutral')} at ${signal.get('price', 0):,.2f}\n"
        
        if order_blocks:
            smc_text += "\n📋 Key Order Blocks:\n"
            for block in order_blocks[-2:]:  # Last 2 blocks
                smc_text += f"   - {block.get('type', 'OB')} at ${block.get('price', 0):,.2f}\n"
        
        return smc_text.strip()
    
    def _extract_volume_data(self, volume_analysis: Dict[str, Any]) -> str:
        """Extract volume analysis data"""
        if not volume_analysis:
            return "Data volume tidak tersedia untuk analisis."
        
        signal = volume_analysis.get('signal', 'neutral')
        strength = volume_analysis.get('strength', 0)
        current_volume = volume_analysis.get('current_volume', 0)
        avg_volume = volume_analysis.get('avg_volume', 0)
        volume_ratio = volume_analysis.get('volume_ratio', 1)
        
        volume_text = f"""
📊 Volume Signal: {signal.upper()} (Strength: {strength:.1f}%)
📈 Current Volume: {current_volume:,.0f}
📊 Average Volume: {avg_volume:,.0f}
📏 Volume Ratio: {volume_ratio:.2f}x
"""
        
        if volume_ratio > 2:
            volume_text += f"🔥 Volume Spike: {volume_ratio:.1f}x above average\n"
        elif volume_ratio > 1.5:
            volume_text += f"📈 Above Average Volume: {volume_ratio:.1f}x\n"
        else:
            volume_text += f"📊 Normal Volume: {volume_ratio:.1f}x\n"
        
        return volume_text.strip()
    
    def _extract_indicators_data(self, indicators: Dict[str, Any]) -> str:
        """Extract technical indicators data"""
        if not indicators:
            return "Data indikator teknis tidak tersedia."
        
        rsi_value = indicators.get('rsi_value', 50)
        ema_trend = indicators.get('ema_trend', 'neutral')
        volume_trend = indicators.get('volume_trend', 'neutral')
        
        indicators_text = f"""
📏 RSI: {rsi_value:.1f}
📈 EMA Trend: {ema_trend.upper()}
📊 Volume Trend: {volume_trend.upper()}
"""
        
        # Add RSI interpretation
        if rsi_value > 70:
            indicators_text += "⚠️ RSI Overbought (>70)\n"
        elif rsi_value < 30:
            indicators_text += "✅ RSI Oversold (<30)\n"
        else:
            indicators_text += "🔄 RSI Normal Range\n"
        
        return indicators_text.strip()
    
    def _extract_signals_data(self, signals: Dict[str, Any]) -> str:
        """Extract trading signals data"""
        if not signals:
            return "Data sinyal trading tidak tersedia."
        
        signal_action = signals.get('signal_action', 'HOLD')
        signal_confidence = signals.get('signal_confidence', 0)
        entry_price = signals.get('entry_price', 0)
        stop_loss = signals.get('stop_loss', 0)
        take_profit_1 = signals.get('take_profit_1', 0)
        
        signals_text = f"""
🎯 Signal Action: {signal_action}
📊 Confidence: {signal_confidence:.1f}%
"""
        
        if signal_action != 'HOLD' and entry_price > 0:
            signals_text += f"""💰 Entry Price: ${entry_price:,.2f}
🛡️ Stop Loss: ${stop_loss:,.2f}
🎯 Take Profit: ${take_profit_1:,.2f}
"""
        
        return signals_text.strip()
    
    def _get_current_price(self, analysis_result: Dict[str, Any]) -> str:
        """Extract current price from analysis result"""
        # Try different possible locations for current price
        if 'current_price' in analysis_result:
            return f"{analysis_result['current_price']:.4f}"
        
        smc_data = analysis_result.get('smc_analysis', {})
        if smc_data and 'current_price' in smc_data:
            return f"{smc_data['current_price']:.4f}"
        
        indicators = analysis_result.get('indicators', {})
        if indicators and 'current_price' in indicators:
            return f"{indicators['current_price']:.4f}"
        
        return "N/A"
    
    def build_quick_prompt(self, symbol: str, timeframe: str, key_data: Dict[str, Any]) -> str:
        """
        Build a quick prompt for faster analysis with essential data only
        """
        prompt = f"""
Quick Analysis Request for {symbol.upper()} ({timeframe}):

Current Price: ${key_data.get('current_price', 'N/A')}
SMC Bias: {key_data.get('smc_signal', 'neutral')}
Volume: {key_data.get('volume_signal', 'neutral')}
RSI: {key_data.get('rsi_value', 50)}
EMA Trend: {key_data.get('ema_trend', 'sideways')}

Berikan analisis singkat dalam bahasa Indonesia:
1. Bias utama (bullish/bearish/neutral) dengan reasoning
2. Entry level yang optimal 
3. Stop loss dan take profit
4. Risk/reward ratio
5. Confidence level (1-5)

Format: Bullet points, maksimal 200 kata, professional tone.
"""
        return prompt.strip()
    
    def build_ultra_quick_prompt(self, symbol: str, timeframe: str, confluence_data: Dict[str, Any]) -> str:
        """
        Build ultra-quick prompt for fastest response (under 10 seconds)
        """
        signal = confluence_data.get('overall_signal', 'neutral')
        consensus = confluence_data.get('consensus_level', 0)
        current_price = confluence_data.get('current_price', 'N/A')
        
        prompt = f"""
Ultra-Quick Analysis untuk {symbol.upper()} ({timeframe}):

Signal: {signal.upper()}
Consensus Level: {consensus:.1f}
Current Price: ${current_price}

Berikan analisis singkat dalam bahasa Indonesia (maksimal 100 kata):
• Bias utama dan reasoning
• Entry point optimal
• Stop loss dan take profit
• Confidence level (1-5 🔵)

Format: Bullet points, actionable insights only.
"""
        return prompt.strip()


# Convenience functions for easy integration
def build_ai_analysis_prompt(symbol: str, timeframe: str, analysis_result: Dict[str, Any]) -> str:
    """
    Convenience function for building AI analysis prompt
    """
    builder = AIPromptBuilder()
    return builder.build_ai_analysis_prompt(symbol, timeframe, analysis_result)


def build_quick_prompt(symbol: str, timeframe: str, key_data: Dict[str, Any]) -> str:
    """
    Convenience function for building quick analysis prompt
    """
    builder = AIPromptBuilder()
    return builder.build_quick_prompt(symbol, timeframe, key_data)