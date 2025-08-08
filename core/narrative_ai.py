"""
AI-powered narrative generation for trading analysis
"""

import os
import openai
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class NarrativeAI:
    """AI-powered narrative generation for trading signals"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("OpenAI API key not found. Narrative AI will use fallback responses.")
    
    def generate_analysis_narrative(self, 
                                  symbol: str, 
                                  analysis_data: Dict[str, Any],
                                  language: str = "indonesian") -> str:
        """Generate detailed analysis narrative"""
        
        if not self.openai_api_key:
            return self._generate_fallback_narrative(symbol, analysis_data, language)
        
        try:
            # Create a comprehensive prompt for analysis
            prompt = self._create_analysis_prompt(symbol, analysis_data, language)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional cryptocurrency trading analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI narrative: {e}")
            return self._generate_fallback_narrative(symbol, analysis_data, language)
    
    def _create_analysis_prompt(self, symbol: str, data: Dict[str, Any], language: str) -> str:
        """Create analysis prompt for OpenAI"""
        
        lang_instruction = "in Indonesian" if language == "indonesian" else "in English"
        
        prompt = f"""
        Create a detailed cryptocurrency trading analysis {lang_instruction} for {symbol}:
        
        Current Data:
        - Price: ${data.get('current_price', 'N/A')}
        - Signal: {data.get('signal_action', 'NEUTRAL')}
        - Confidence: {data.get('confidence', 0)}%
        - Pattern: {data.get('pattern_type', 'None')}
        - RSI: {data.get('rsi', 'N/A')}
        - Trend: {data.get('trend', 'NEUTRAL')}
        - Volume: {data.get('volume_status', 'Normal')}
        
        Please provide:
        1. Market structure analysis
        2. Technical indicator interpretation
        3. Trading recommendation
        4. Risk assessment
        5. Price targets if applicable
        
        Keep it professional and actionable.
        """
        
        return prompt
    
    def _generate_fallback_narrative(self, symbol: str, data: Dict[str, Any], language: str) -> str:
        """Generate fallback narrative when OpenAI is unavailable"""
        
        if language == "indonesian":
            return f"""
            Analisis {symbol} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            
            📊 STRUKTUR PASAR
            Harga saat ini: ${data.get('current_price', 'N/A')}
            Signal: {data.get('signal_action', 'NEUTRAL')}
            Confidence: {data.get('confidence', 0)}%
            
            🔍 ANALISIS TEKNIKAL
            RSI: {data.get('rsi', 'N/A')}
            Trend: {data.get('trend', 'NEUTRAL')}
            Volume: {data.get('volume_status', 'Normal')}
            
            ⚠️ MANAJEMEN RISIKO
            Selalu gunakan stop loss dan take profit sesuai analisis.
            Position sizing maksimal 2% dari portfolio.
            
            📈 REKOMENDASI
            Tunggu konfirmasi lebih lanjut sebelum entry.
            Monitor pergerakan harga dan volume.
            """
        else:
            return f"""
            {symbol} Analysis ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            
            📊 MARKET STRUCTURE
            Current Price: ${data.get('current_price', 'N/A')}
            Signal: {data.get('signal_action', 'NEUTRAL')}
            Confidence: {data.get('confidence', 0)}%
            
            🔍 TECHNICAL ANALYSIS
            RSI: {data.get('rsi', 'N/A')}
            Trend: {data.get('trend', 'NEUTRAL')}
            Volume: {data.get('volume_status', 'Normal')}
            
            ⚠️ RISK MANAGEMENT
            Always use stop loss and take profit levels.
            Maximum position size: 2% of portfolio.
            
            📈 RECOMMENDATION
            Wait for further confirmation before entry.
            Monitor price movement and volume closely.
            """
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            'api_key_configured': bool(self.openai_api_key),
            'last_request': datetime.now().isoformat(),
            'status': 'active' if self.openai_api_key else 'fallback_mode'
        }