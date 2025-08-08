import os
import logging
import asyncio
from typing import Optional, List, Dict
try:
    from telegram import Bot, Update
    from telegram.constants import ParseMode
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
    TELEGRAM_AVAILABLE = True
except ImportError:
    # Fallback if telegram package not available
    Bot = None
    Update = None
    ParseMode = None
    Application = None
    CommandHandler = None
    MessageHandler = None
    ContextTypes = None
    filters = None
    TELEGRAM_AVAILABLE = False
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        """Initialize Telegram Bot"""
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot library not installed")
            
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        self.bot = Bot(token=self.token)
        self.application = None
        self.chat_ids = self._load_chat_ids()
        
        logger.info("🤖 Telegram Bot initialized")
    
    def _load_chat_ids(self) -> List[str]:
        """Load saved chat IDs from database or file"""
        # TODO: Load from database
        # For now, return empty list
        return []
    
    def _save_chat_id(self, chat_id: str):
        """Save chat ID for future notifications"""
        if chat_id not in self.chat_ids:
            self.chat_ids.append(chat_id)
            # TODO: Save to database
            logger.info(f"New chat ID registered: {chat_id}")
    
    async def send_signal(self, signal_data: Dict):
        """Send trading signal to all registered chats"""
        try:
            # Format signal message
            symbol = signal_data.get('symbol', 'Unknown')
            signal = signal_data.get('signal', 'NEUTRAL')
            confidence = signal_data.get('confidence', 0)
            entry_price = signal_data.get('entry_price', 0)
            stop_loss = signal_data.get('stop_loss', 0) 
            take_profit = signal_data.get('take_profit', 0)
            indicators = signal_data.get('indicators_triggered', [])
            narrative = signal_data.get('narrative', '')
            
            # Create emoji based on signal
            signal_emoji = "🟢" if signal == "LONG" else "🔴" if signal == "SHORT" else "⚪"
            
            # Format message
            message = f"""
{signal_emoji} <b>SHARP SIGNAL ALERT</b> {signal_emoji}

📊 <b>Pair:</b> {symbol}
📈 <b>Signal:</b> {signal}
💯 <b>Confidence:</b> {confidence:.1%}

💰 <b>Entry Price:</b> ${entry_price:,.2f}
🎯 <b>Take Profit:</b> ${take_profit:,.2f}  
🛡 <b>Stop Loss:</b> ${stop_loss:,.2f}

📌 <b>Indicators Triggered:</b>
{self._format_indicators(indicators)}

🤖 <b>AI Analysis:</b>
{narrative}

⏰ <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
            
            # Send to all registered chats
            for chat_id in self.chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=ParseMode.HTML
                    )
                except Exception as e:
                    logger.error(f"Failed to send to chat {chat_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
    
    def _format_indicators(self, indicators: List[str]) -> str:
        """Format indicators list for telegram message"""
        if not indicators:
            return "• No strong indicators detected"
        
        formatted = []
        for indicator in indicators:
            formatted.append(f"• {indicator}")
        
        return "\n".join(formatted)
    
    async def send_alert(self, alert_type: str, message: str, data: Optional[Dict] = None):
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
                alert_message += f"\n\n<pre>{json.dumps(data, indent=2)}</pre>"
            
            for chat_id in self.chat_ids:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=alert_message,
                        parse_mode=ParseMode.HTML
                    )
                except Exception as e:
                    logger.error(f"Failed to send alert to {chat_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def start_bot(self):
        """Start the telegram bot with handlers"""
        try:
            self.updater = Updater(token=self.token, use_context=True)
            dispatcher = self.updater.dispatcher
            
            # Add command handlers
            dispatcher.add_handler(CommandHandler("start", self._start_command))
            dispatcher.add_handler(CommandHandler("help", self._help_command))
            dispatcher.add_handler(CommandHandler("signal", self._signal_command))
            dispatcher.add_handler(CommandHandler("status", self._status_command))
            dispatcher.add_handler(CommandHandler("subscribe", self._subscribe_command))
            dispatcher.add_handler(CommandHandler("unsubscribe", self._unsubscribe_command))
            
            # Start the bot
            self.updater.start_polling()
            logger.info("🚀 Telegram bot started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start telegram bot: {e}")
    
    def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = str(update.effective_chat.id)
        self._save_chat_id(chat_id)
        
        welcome_message = """
🤖 <b>Welcome to RZC GPS Trading Bot!</b>

I'll send you sharp trading signals and market alerts.

<b>Available Commands:</b>
/help - Show all commands
/signal SYMBOL - Get latest signal for a symbol
/status - Check system status
/subscribe - Subscribe to automatic signals
/unsubscribe - Unsubscribe from signals

<b>Example:</b>
/signal BTCUSDT

You're now subscribed to receive trading signals! 🚀
"""
        
        update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)
    
    def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 <b>RZC GPS Trading Bot Commands</b>

<b>Signal Commands:</b>
• /signal SYMBOL - Get latest signal (e.g., /signal BTCUSDT)
• /analyze SYMBOL - Get detailed analysis

<b>Subscription:</b>
• /subscribe - Receive automatic signals
• /unsubscribe - Stop receiving signals

<b>Information:</b>
• /status - System status
• /help - This message

<b>Signal Types:</b>
🟢 LONG - Buy signal
🔴 SHORT - Sell signal
⚪ NEUTRAL - No clear signal

<b>Confidence Levels:</b>
• 90%+ : Very Strong Signal
• 80-90% : Strong Signal
• 70-80% : Moderate Signal
• <70% : Weak Signal
"""
        
        update.message.reply_text(help_message, parse_mode=ParseMode.HTML)
    
    def _signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signal command"""
        if not context.args:
            update.message.reply_text("Please provide a symbol. Example: /signal BTCUSDT")
            return
        
        symbol = context.args[0].upper()
        if not symbol.endswith('USDT'):
            symbol += 'USDT'
        
        # TODO: Fetch latest signal from database or API
        update.message.reply_text(f"Fetching latest signal for {symbol}... 🔍")
    
    def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_message = """
🟢 <b>System Status: ONLINE</b>

📊 Active Signals: Loading...
📈 Win Rate: Loading...
🤖 AI Engine: Active
📡 Data Feed: Connected

Last Update: {timestamp}
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))
        
        update.message.reply_text(status_message, parse_mode=ParseMode.HTML)
    
    def _subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        chat_id = str(update.effective_chat.id)
        self._save_chat_id(chat_id)
        update.message.reply_text("✅ You're subscribed to trading signals!")
    
    def _unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command"""
        chat_id = str(update.effective_chat.id)
        if chat_id in self.chat_ids:
            self.chat_ids.remove(chat_id)
            # TODO: Remove from database
        update.message.reply_text("❌ You've been unsubscribed from trading signals.")
    
    def stop_bot(self):
        """Stop the telegram bot"""
        if self.updater:
            self.updater.stop()
            logger.info("Telegram bot stopped")

# Global bot instance
telegram_bot = None

def initialize_telegram_bot():
    """Initialize global telegram bot instance"""
    global telegram_bot
    if not telegram_bot:
        telegram_bot = TelegramBot()
        telegram_bot.start_bot()
    return telegram_bot

def get_telegram_bot() -> Optional[TelegramBot]:
    """Get telegram bot instance"""
    return telegram_bot