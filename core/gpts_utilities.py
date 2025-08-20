#!/usr/bin/env python3
"""
GPTs Utility Functions - Extracted from multiple GPTs API files
Contains enhanced utility functions for symbol normalization, data validation,
service initialization, and Telegram messaging without blueprint conflicts.
"""

import os
import re
import logging
import urllib.parse
import pandas as pd
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

# =============================================================================
# ENHANCED SYMBOL & TIMEFRAME NORMALIZATION
# =============================================================================

def normalize_symbol_enhanced(symbol: str) -> str:
    """
    Enhanced symbol normalization handling multiple formats
    
    Handles:
    - BTCUSDT -> BTC-USDT  
    - BTC/USDT -> BTC-USDT
    - btc-usdt -> BTC-USDT
    - URL-encoded slashes: BTC%2FUSDT -> BTC-USDT
    """
    if not symbol:
        return "BTC-USDT"  # Default fallback
    
    # Handle URL-encoded slashes first
    symbol = urllib.parse.unquote(str(symbol))
    
    # Convert to uppercase and remove spaces
    symbol = symbol.upper().strip()
    
    # If already in correct format, return as-is
    if re.match(r'^[A-Z]{2,10}-[A-Z]{2,10}$', symbol):
        return symbol
    
    # Handle slash format (BTC/USDT -> BTC-USDT)
    if '/' in symbol:
        parts = symbol.split('/')
        if len(parts) == 2 and all(len(part) >= 2 for part in parts):
            return '-'.join(parts)
        else:
            logger.warning(f"Invalid slash format: {symbol}")
            return symbol.replace('/', '-')
    
    # Handle concatenated format (BTCUSDT -> BTC-USDT)
    common_quotes = ['USDT', 'USDC', 'BTC', 'ETH', 'USD', 'EUR', 'DAI', 'BUSD']
    
    for quote in common_quotes:
        if symbol.endswith(quote) and len(symbol) > len(quote):
            base = symbol[:-len(quote)]
            if len(base) >= 2:  # Valid base currency
                return f"{base}-{quote}"
    
    # If no pattern matches, return as-is
    logger.warning(f"Could not normalize symbol: {symbol}, returning as-is")
    return symbol

def normalize_timeframe_enhanced(tf: str) -> str:
    """Enhanced timeframe normalization with extended mappings"""
    if not tf:
        return '1H'
    
    # Extended timeframe mapping
    tf_map = {
        '1m': '1m', '1M': '1m', '1min': '1m',
        '3m': '3m', '3M': '3m', '3min': '3m',
        '5m': '5m', '5M': '5m', '5min': '5m',
        '15m': '15m', '15M': '15m', '15min': '15m',
        '30m': '30m', '30M': '30m', '30min': '30m',
        '1h': '1H', '1H': '1H', '1hour': '1H',
        '2h': '2H', '2H': '2H', '2hour': '2H', 
        '4h': '4H', '4H': '4H', '4hour': '4H',
        '6h': '6H', '6H': '6H', '6hour': '6H',
        '12h': '12H', '12H': '12H', '12hour': '12H',
        '1d': '1D', '1D': '1D', '1day': '1D', 'daily': '1D',
        '2d': '2D', '2D': '2D', '2day': '2D',
        '3d': '3D', '3D': '3D', '3day': '3D',
        '1w': '1W', '1W': '1W', '1week': '1W', 'weekly': '1W',
        '1mo': '1M', '1month': '1M', 'monthly': '1M'
    }
    
    normalized = tf_map.get(tf.lower() if isinstance(tf, str) else tf)
    return normalized if normalized else tf.upper()

# =============================================================================
# ENHANCED DATA VALIDATION
# =============================================================================

def validate_ohlcv_data_enhanced(df: pd.DataFrame) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Enhanced OHLCV data validation with detailed error reporting
    
    Returns:
        tuple: (is_valid, error_message, cleaned_df)
    """
    if df is None or df.empty:
        return False, "Empty dataframe provided", None
    
    # Required OHLCV columns
    required_cols = ["open", "high", "low", "close", "volume"]
    
    # Check if required columns exist
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return False, f"Missing required columns: {missing_cols}", None
    
    # Create a copy to avoid modifying original
    df_clean = df.copy()
    
    try:
        # Coerce to numeric, invalid parsing will become NaN
        df_clean[required_cols] = df_clean[required_cols].apply(pd.to_numeric, errors="coerce")
        
        # Check for any NaN values after coercion
        nan_counts = df_clean[required_cols].isna().sum()
        if nan_counts.any():
            nan_details = {col: count for col, count in nan_counts.items() if count > 0}
            return False, f"Invalid numeric data detected: {nan_details}", None
        
        # Enhanced validation: ensure OHLC relationships are logical
        invalid_conditions = [
            (df_clean['high'] < df_clean['low'], 'High < Low'),
            (df_clean['high'] < df_clean['open'], 'High < Open'),
            (df_clean['high'] < df_clean['close'], 'High < Close'),
            (df_clean['low'] > df_clean['open'], 'Low > Open'),
            (df_clean['low'] > df_clean['close'], 'Low > Close'),
            (df_clean['open'] <= 0, 'Open <= 0'),
            (df_clean['volume'] < 0, 'Volume < 0')
        ]
        
        for condition, description in invalid_conditions:
            if condition.any():
                invalid_count = condition.sum()
                return False, f"Invalid OHLC data: {description} in {invalid_count} rows", None
        
        # Check for minimum data requirements
        if len(df_clean) < 60:
            return False, f"Insufficient data: {len(df_clean)} rows (minimum 60 required for indicators)", None
        
        return True, "Enhanced data validation passed", df_clean
        
    except Exception as e:
        return False, f"Data validation error: {str(e)}", None

# =============================================================================
# FEATURE FLAGS SYSTEM
# =============================================================================

class FeatureFlags:
    """Enhanced feature flags system for production deployment"""
    
    @staticmethod
    def is_telegram_enabled() -> bool:
        """Check if Telegram features are enabled"""
        return os.environ.get('TELEGRAM_ENABLED', 'true').lower() == 'true'
    
    @staticmethod
    def is_redis_enabled() -> bool:
        """Check if Redis caching is enabled"""
        return os.environ.get('REDIS_ENABLED', 'true').lower() == 'true'
    
    @staticmethod
    def is_debug_mode() -> bool:
        """Check if debug mode is enabled"""
        return os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    
    @staticmethod
    def is_ai_reasoning_enabled() -> bool:
        """Check if AI reasoning logging is enabled"""
        return os.environ.get('AI_REASONING_ENABLED', 'true').lower() == 'true'
    
    @staticmethod
    def get_max_concurrent_requests() -> int:
        """Get maximum concurrent requests limit"""
        try:
            return int(os.environ.get('MAX_CONCURRENT_REQUESTS', '10'))
        except ValueError:
            return 10
    
    @staticmethod
    def get_feature_status() -> Dict[str, Any]:
        """Get complete feature flags status"""
        return {
            'telegram_enabled': FeatureFlags.is_telegram_enabled(),
            'redis_enabled': FeatureFlags.is_redis_enabled(),
            'debug_mode': FeatureFlags.is_debug_mode(),
            'ai_reasoning_enabled': FeatureFlags.is_ai_reasoning_enabled(),
            'max_concurrent_requests': FeatureFlags.get_max_concurrent_requests(),
            'environment': os.environ.get('ENVIRONMENT', 'development')
        }

# =============================================================================
# CORE SERVICES INITIALIZATION  
# =============================================================================

class CoreServicesManager:
    """Enhanced on-demand core services initialization"""
    
    def __init__(self):
        self.services = {}
        self.initialization_log = []
    
    def get_service(self, service_name: str):
        """Get service with lazy initialization"""
        if service_name in self.services:
            return self.services[service_name]
        
        return self._initialize_service(service_name)
    
    def _initialize_service(self, service_name: str):
        """Initialize specific service on demand"""
        try:
            if service_name == 'okx_fetcher':
                from core.okx_fetcher_enhanced import OKXFetcherEnhanced
                service = OKXFetcherEnhanced()
                self.services[service_name] = service
                self.initialization_log.append(f"✅ {service_name} initialized")
                logger.info(f"✅ {service_name} initialized successfully")
                return service
                
            elif service_name == 'ai_engine':
                from core.enhanced_ai_engine import EnhancedAIEngine
                service = EnhancedAIEngine()
                self.services[service_name] = service
                self.initialization_log.append(f"✅ {service_name} initialized")
                logger.info(f"✅ {service_name} initialized successfully")
                return service
                
            elif service_name == 'telegram_notifier' and FeatureFlags.is_telegram_enabled():
                from core.telegram_notifier import TelegramNotifier
                service = TelegramNotifier()
                self.services[service_name] = service
                self.initialization_log.append(f"✅ {service_name} initialized")
                logger.info(f"✅ {service_name} initialized successfully")
                return service
                
            elif service_name == 'redis_manager' and FeatureFlags.is_redis_enabled():
                from core.redis_manager import RedisManager
                service = RedisManager()
                self.services[service_name] = service
                self.initialization_log.append(f"✅ {service_name} initialized")
                logger.info(f"✅ {service_name} initialized successfully")
                return service
                
            else:
                logger.warning(f"⚠️ Service {service_name} not available or disabled by feature flags")
                return None
                
        except ImportError as e:
            logger.warning(f"⚠️ {service_name} not available: {e}")
            self.initialization_log.append(f"⚠️ {service_name} failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ {service_name} initialization error: {e}")
            self.initialization_log.append(f"❌ {service_name} error: {str(e)}")
            return None
    
    def get_initialization_status(self) -> Dict[str, Any]:
        """Get complete initialization status"""
        return {
            'initialized_services': list(self.services.keys()),
            'service_count': len(self.services),
            'initialization_log': self.initialization_log,
            'feature_flags': FeatureFlags.get_feature_status()
        }

# Global services manager instance
services_manager = CoreServicesManager()

# =============================================================================
# ENHANCED TELEGRAM MESSAGING FUNCTIONS
# =============================================================================

def generate_telegram_message_enhanced(signal_result: Dict, symbol: str, timeframe: str, current_price: float) -> str:
    """
    Generate enhanced Telegram message with rich formatting
    """
    try:
        action = signal_result.get('action', 'HOLD')
        confidence = signal_result.get('confidence', 0)
        entry_price = signal_result.get('entry_price', current_price)
        stop_loss = signal_result.get('stop_loss', 0)
        take_profit = signal_result.get('take_profit', 0)
        reasoning = signal_result.get('reasoning', 'Analysis completed')
        
        # Enhanced emoji mapping
        action_emojis = {
            'BUY': '🟢📈',
            'SELL': '🔴📉', 
            'STRONG_BUY': '🚀💚',
            'STRONG_SELL': '⚡🔴',
            'HOLD': '⏸️💛'
        }
        
        confidence_emoji = '🔥' if confidence > 80 else '⭐' if confidence > 60 else '⚠️'
        
        message = f"""
{action_emojis.get(action, '📊')} **TRADING SIGNAL** {confidence_emoji}

💱 **Pair**: {symbol}
⏰ **Timeframe**: {timeframe}
💰 **Current Price**: ${current_price:,.4f}

🎯 **Action**: {action}
📊 **Confidence**: {confidence}%

📍 **Levels**:
• Entry: ${entry_price:,.4f}
• Stop Loss: ${stop_loss:,.4f}
• Take Profit: ${take_profit:,.4f}

🧠 **Analysis**: {reasoning[:200]}...

⚡ Generated at {datetime.now().strftime('%H:%M:%S UTC')}
🤖 AI-Powered Trading Assistant
        """.strip()
        
        return message
        
    except Exception as e:
        logger.error(f"Error generating enhanced Telegram message: {e}")
        return f"📊 Trading signal for {symbol} | Action: {signal_result.get('action', 'HOLD')} | Generated at {datetime.now().strftime('%H:%M:%S')}"

def generate_natural_language_narrative_enhanced(signal_result: Dict, symbol: str, timeframe: str, current_price: float) -> str:
    """
    Generate enhanced natural language narrative for trading signals
    """
    try:
        action = signal_result.get('action', 'HOLD')
        confidence = signal_result.get('confidence', 0)
        reasoning = signal_result.get('reasoning', '')
        technical_indicators = signal_result.get('technical_indicators', {})
        
        # Enhanced narrative templates
        confidence_phrases = {
            (90, 100): "dengan keyakinan sangat tinggi",
            (80, 89): "dengan keyakinan tinggi", 
            (70, 79): "dengan keyakinan sedang",
            (60, 69): "dengan keyakinan cukup",
            (0, 59): "dengan keyakinan rendah"
        }
        
        confidence_text = next((phrase for (low, high), phrase in confidence_phrases.items() 
                              if low <= confidence <= high), "dengan analisis mendalam")
        
        action_narratives = {
            'BUY': f"Sistem AI merekomendasikan posisi BELI untuk {symbol}",
            'SELL': f"Sistem AI merekomendasikan posisi JUAL untuk {symbol}",
            'STRONG_BUY': f"Sistem AI memberikan sinyal BELI KUAT untuk {symbol}",
            'STRONG_SELL': f"Sistem AI memberikan sinyal JUAL KUAT untuk {symbol}",
            'HOLD': f"Sistem AI merekomendasikan untuk MENAHAN posisi {symbol}"
        }
        
        base_narrative = action_narratives.get(action, f"Analisis untuk {symbol}")
        
        # Technical analysis summary
        tech_summary = ""
        if technical_indicators:
            sma_trend = technical_indicators.get('sma_trend', 'neutral')
            rsi_level = technical_indicators.get('rsi', 50)
            
            if sma_trend == 'bullish':
                tech_summary += " Tren SMA menunjukkan momentum bullish."
            elif sma_trend == 'bearish':
                tech_summary += " Tren SMA menunjukkan momentum bearish."
                
            if rsi_level > 70:
                tech_summary += " RSI menunjukkan kondisi overbought."
            elif rsi_level < 30:
                tech_summary += " RSI menunjukkan kondisi oversold."
        
        narrative = f"""
{base_narrative} {confidence_text} (confidence: {confidence}%) pada timeframe {timeframe}. 
Harga saat ini berada di level ${current_price:,.4f}.

{tech_summary}

Reasoning: {reasoning[:300]}...

Analisis ini dihasilkan menggunakan kombinasi indikator teknikal, analisis Smart Money Concept, 
dan machine learning algorithms untuk memberikan insight trading yang akurat.
        """.strip()
        
        return narrative
        
    except Exception as e:
        logger.error(f"Error generating enhanced narrative: {e}")
        return f"Analisis trading untuk {symbol} pada timeframe {timeframe} telah selesai dengan confidence {signal_result.get('confidence', 0)}%."

# =============================================================================
# UTILITY EXPORT
# =============================================================================

__all__ = [
    'normalize_symbol_enhanced',
    'normalize_timeframe_enhanced', 
    'validate_ohlcv_data_enhanced',
    'FeatureFlags',
    'CoreServicesManager',
    'services_manager',
    'generate_telegram_message_enhanced',
    'generate_natural_language_narrative_enhanced'
]

logger.info("🚀 GPTs Utility Functions loaded successfully")