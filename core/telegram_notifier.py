# core/telegram_notifier.py
import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Telegram notification service"""
    
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
    def send_message(self, message: str, override_chat_id: Optional[str] = None) -> Dict[str, Any]:
        """Send message to Telegram"""
        return send_telegram_message(message, override_chat_id)

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