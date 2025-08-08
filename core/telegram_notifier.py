import os
import logging
import json
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        """Initialize Telegram Notifier"""
        # Read token from environment secrets
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment")
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
            
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.chat_ids = self._load_chat_ids()
        
        logger.info("📱 Telegram Notifier initialized")
    
    def _load_chat_ids(self) -> List[str]:
        """Load saved chat IDs from database or file"""
        # TODO: Load from database
        # For now, return empty list - will be populated when users start the bot
        return []
    
    def _save_chat_id(self, chat_id: str):
        """Save chat ID for future notifications"""
        if chat_id not in self.chat_ids:
            self.chat_ids.append(chat_id)
            # TODO: Save to database
            logger.info(f"New chat ID registered: {chat_id}")
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = 'HTML', max_retries: int = 2) -> bool:
        """Send message to specific chat with retry mechanism"""
        for attempt in range(max_retries + 1):
            try:
                url = f"{self.api_url}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': text,
                    'parse_mode': parse_mode
                }
                
                response = requests.post(url, json=data, timeout=10)
                if response.status_code == 200:
                    if attempt > 0:
                        logger.info(f"✅ Message sent successfully on attempt {attempt + 1}")
                    return True
                else:
                    logger.warning(f"❌ Attempt {attempt + 1} failed: {response.text}")
                    if attempt < max_retries:
                        time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                        continue
                    else:
                        logger.error(f"💥 All {max_retries + 1} attempts failed to send message")
                        return False
                        
            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} error: {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(f"💥 All {max_retries + 1} attempts failed: {str(e)}")
                    return False
        
        return False
    
    def send_signal(self, signal_data: Dict):
        """Send trading signal to all registered chats"""
        try:
            # Format signal using professional formatter
            message = self.format_sharp_signal(signal_data)
            
            # Send to all registered chats
            success_count = 0
            for chat_id in self.chat_ids:
                if self.send_message(chat_id, message, parse_mode='HTML'):
                    success_count += 1
            
            logger.info(f"📊 Sharp signal sent to {success_count}/{len(self.chat_ids)} chats")
            
        except Exception as e:
            logger.error(f"💥 Error sending signal: {e}")
    
    def format_sharp_signal(self, signal_data: Dict) -> str:
        """
        Format sharp signal untuk Telegram dengan gaya profesional
        """
        try:
            # Extract signal data
            symbol = signal_data.get('symbol', 'Unknown')
            signal = signal_data.get('signal', {})
            direction = signal.get('direction', 'NEUTRAL') if isinstance(signal, dict) else signal_data.get('direction', 'NEUTRAL')
            confidence = signal.get('confidence', 0) if isinstance(signal, dict) else signal_data.get('confidence', 0)
            confidence_emoji = signal.get('confidence_emoji', '') if isinstance(signal, dict) else signal_data.get('confidence_emoji', '')
            confidence_level = signal.get('confidence_level', '') if isinstance(signal, dict) else signal_data.get('confidence_level', '')
            entry_price = signal.get('entry_price', 0) if isinstance(signal, dict) else signal_data.get('entry_price', 0)
            stop_loss = signal.get('stop_loss', 0) if isinstance(signal, dict) else signal_data.get('stop_loss', 0)
            take_profit = signal.get('take_profit', 0) if isinstance(signal, dict) else signal_data.get('take_profit', 0)
            
            # Get indicators and narrative with HTML escaping
            indicators = signal_data.get('indicators', {})
            narrative_raw = signal_data.get('ai_narrative', signal_data.get('narrative', 'Market analysis indicates potential trading opportunity based on current technical conditions.'))
            # Escape HTML characters to prevent parsing errors
            narrative = self._escape_html(narrative_raw)
            
            # Format numbers properly
            entry_formatted = f"${entry_price:,.2f}" if entry_price > 0 else "TBD"
            tp_formatted = f"${take_profit:,.2f}" if take_profit > 0 else "TBD"
            sl_formatted = f"${stop_loss:,.2f}" if stop_loss > 0 else "TBD"
            confidence_formatted = f"{confidence:.2f}%" if isinstance(confidence, (int, float)) else f"{confidence}%"
            
            # Add confidence emoji if not present
            if not confidence_emoji:
                if confidence >= 90:
                    confidence_emoji = "🔥"
                    confidence_level = "ULTRA HIGH"
                elif confidence >= 80:
                    confidence_emoji = "💎"
                    confidence_level = "HIGH"
                elif confidence >= 75:
                    confidence_emoji = "✅"
                    confidence_level = "STANDARD"
                else:
                    confidence_emoji = "⚠️"
                    confidence_level = "LOW"
            
            # Signal emoji based on direction
            signal_emoji = "🟢" if direction in ["BUY", "LONG"] else "🔴" if direction in ["SELL", "SHORT"] else "⚪"
            
            # Format indicators as bullet list
            indicators_text = self._format_indicators_professional(indicators)
            
            # UTC timestamp
            utc_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Safe message format - HTML instead of Markdown for reliability
            message = f"""⚪ <b>SHARP SIGNAL ALERT</b> ⚪

📊 <b>Pair:</b> {symbol}
📈 <b>Signal:</b> {direction}
💰 <b>Entry:</b> {entry_formatted}
🎯 <b>Take Profit:</b> {tp_formatted}
🛡 <b>Stop Loss:</b> {sl_formatted}
💯 <b>Confidence:</b> {confidence_emoji} {confidence_formatted} ({confidence_level})

📈 <b>Technical Indicators:</b>
{indicators_text}

🤖 <b>AI Market Analysis:</b>
{narrative}

⏰ <i>{utc_time}</i>
"""
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Error formatting sharp signal: {e}")
            return f"⚪ *SIGNAL ERROR* ⚪\n\nUnable to format signal data. Please check system status.\n\n⏰ _{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}_"
    
    def _format_indicators_professional(self, indicators) -> str:
        """Format indicators sebagai bullet list profesional"""
        if not indicators:
            return "• Market conditions analyzed with standard technical indicators"
        
        formatted_indicators = []
        
        # Format different types of indicators
        if isinstance(indicators, dict):
            for key, value in indicators.items():
                if key == 'trend' and value:
                    formatted_indicators.append(f"• Trend Analysis: {value}")
                elif key == 'momentum' and value:
                    formatted_indicators.append(f"• Momentum: {value}")
                elif key == 'support_resistance' and value:
                    formatted_indicators.append(f"• Support/Resistance: Active levels detected")
                elif key == 'volume' and value:
                    formatted_indicators.append(f"• Volume Analysis: {value}")
                elif key == 'rsi' and value:
                    formatted_indicators.append(f"• RSI: {value}")
                elif key == 'macd' and value:
                    formatted_indicators.append(f"• MACD: {value}")
                elif isinstance(value, (str, int, float)) and value:
                    escaped_value = self._escape_html(str(value))
                    formatted_indicators.append(f"• {key.replace('_', ' ').title()}: {escaped_value}")
        elif isinstance(indicators, list):
            for indicator in indicators[:8]:  # Limit to 8 indicators
                formatted_indicators.append(f"• {indicator}")
        
        if not formatted_indicators:
            formatted_indicators.append("• Technical analysis completed with multiple indicators")
        
        return "\n".join(formatted_indicators[:8])  # Max 8 lines
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters untuk Telegram"""
        if not text:
            return text
        
        # Basic HTML escaping
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text
    
    def _format_indicators(self, indicators: List[str]) -> str:
        """Legacy format untuk kompatibilitas"""
        return self._format_indicators_professional(indicators)
    
    def send_alert(self, alert_type: str, message: str, data: Optional[Dict] = None):
        """Send general alert to all registered chats"""
        try:
            alert_emoji = {
                'funding_rate': '💸',
                'volume_spike': '📊',
                'pattern_detected': '🎯',
                'risk_alert': '⚠️',
                'system': '🔧'
            }.get(alert_type, '📢')
            
            alert_message = f"{alert_emoji} <b>{alert_type.upper().replace('_', ' ')}</b>\n\n{message}"
            
            if data:
                # Add key data points, not full JSON
                if 'symbol' in data:
                    alert_message += f"\n\n📊 Symbol: {data['symbol']}"
                if 'value' in data:
                    alert_message += f"\n💰 Value: {data['value']}"
            
            # Send to all registered chats
            for chat_id in self.chat_ids:
                self.send_message(chat_id, alert_message)
                    
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def get_updates(self):
        """Get updates from Telegram to process commands"""
        try:
            url = f"{self.api_url}/getUpdates"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json().get('result', [])
            return []
            
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    def set_webhook(self, webhook_url: str):
        """Set webhook for bot updates"""
        try:
            url = f"{self.api_url}/setWebhook"
            data = {'url': webhook_url}
            
            response = requests.post(url, json=data)
            if response.status_code == 200:
                logger.info(f"Webhook set: {webhook_url}")
                return True
            else:
                logger.error(f"Failed to set webhook: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False

# Global notifier instance
telegram_notifier = None

def initialize_telegram_notifier():
    """Initialize global telegram notifier instance"""
    global telegram_notifier
    if not telegram_notifier:
        telegram_notifier = TelegramNotifier()
    return telegram_notifier

def get_telegram_notifier() -> Optional[TelegramNotifier]:
    """Get telegram notifier instance"""
    return telegram_notifier