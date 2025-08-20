# core/telegram_notifier.py
import os
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import enhanced utilities
try:
    from core.gpts_utilities import (
        generate_telegram_message_enhanced,
        generate_natural_language_narrative_enhanced,
        FeatureFlags
    )
    ENHANCED_UTILITIES_AVAILABLE = True
except ImportError:
    # Fallback definitions for LSP compatibility
    ENHANCED_UTILITIES_AVAILABLE = False
    
    class FeatureFlags:
        @staticmethod
        def is_telegram_enabled():
            return True
    
    def generate_telegram_message_enhanced(signal_result, symbol, timeframe, current_price):
        return f"Trading signal for {symbol}: {signal_result.get('action', 'HOLD')}"
    
    def generate_natural_language_narrative_enhanced(signal_result, symbol, timeframe, current_price):
        return f"Analysis for {symbol} completed with {signal_result.get('confidence', 0)}% confidence."

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Enhanced Telegram notification service with rich formatting"""
    
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        self.enhanced_mode = ENHANCED_UTILITIES_AVAILABLE and FeatureFlags.is_telegram_enabled() if ENHANCED_UTILITIES_AVAILABLE else True
        
    def send_message(self, message: str, override_chat_id: Optional[str] = None) -> Dict[str, Any]:
        """Send message to Telegram"""
        return send_telegram_message(message, override_chat_id)
    
    def send_trading_signal(self, signal_result: Dict, symbol: str, timeframe: str, current_price: float, 
                           override_chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send enhanced trading signal with rich formatting
        """
        if self.enhanced_mode and ENHANCED_UTILITIES_AVAILABLE:
            # Use enhanced message generation
            message = generate_telegram_message_enhanced(signal_result, symbol, timeframe, current_price)
        else:
            # Fallback to basic message
            action = signal_result.get('action', 'HOLD')
            confidence = signal_result.get('confidence', 0)
            message = f"""
🚨 TRADING SIGNAL

💱 Pair: {symbol}
⏰ Timeframe: {timeframe}
💰 Price: ${current_price:,.4f}

🎯 Action: {action}
📊 Confidence: {confidence}%

⚡ Generated at {datetime.now().strftime('%H:%M:%S UTC')}
            """.strip()
        
        return self.send_message(message, override_chat_id)
    
    def send_market_analysis(self, analysis_result: Dict, symbol: str, timeframe: str, 
                           current_price: float, override_chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send market analysis with natural language narrative
        """
        if self.enhanced_mode and ENHANCED_UTILITIES_AVAILABLE:
            # Use enhanced narrative generation
            narrative = generate_natural_language_narrative_enhanced(analysis_result, symbol, timeframe, current_price)
            message = f"""
📊 MARKET ANALYSIS

{narrative}

⚡ Generated at {datetime.now().strftime('%H:%M:%S UTC')}
🤖 AI-Powered Analysis
            """.strip()
        else:
            # Fallback to basic analysis
            message = f"""
📊 MARKET ANALYSIS

💱 Symbol: {symbol}
⏰ Timeframe: {timeframe}
💰 Current Price: ${current_price:,.4f}

Analysis completed successfully.

⚡ Generated at {datetime.now().strftime('%H:%M:%S UTC')}
            """.strip()
        
        return self.send_message(message, override_chat_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get enhanced Telegram notifier status"""
        return {
            'bot_configured': bool(self.bot_token and self.chat_id),
            'enhanced_mode': self.enhanced_mode,
            'utilities_available': ENHANCED_UTILITIES_AVAILABLE,
            'feature_flags_enabled': FeatureFlags.is_telegram_enabled() if ENHANCED_UTILITIES_AVAILABLE else True,
            'last_check': datetime.now().isoformat()
        }

def send_telegram_message(message: str, override_chat_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Send message to Telegram
    
    Args:
        message: Text message to send
        override_chat_id: Optional chat ID to override default
        
    Returns:
        Dictionary dengan status pengiriman
    """
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = override_chat_id or os.environ.get('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            return {
                'success': False,
                'error': 'Telegram credentials not configured (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)'
            }
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        
        return {
            'success': True,
            'message_id': response.json().get('result', {}).get('message_id')
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram API request failed: {e}")
        return {
            'success': False,
            'error': f"Telegram API request failed: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return {
            'success': False,
            'error': f"Error sending Telegram message: {str(e)}"
        }