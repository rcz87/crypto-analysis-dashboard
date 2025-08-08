#!/usr/bin/env python3
"""
📬 Failover Telegram Bot - Backup Notification System
Sistem backup bot untuk memastikan notifikasi tetap terkirim jika bot utama gagal
"""

import os
import logging
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import threading
from queue import Queue, Empty
import requests

logger = logging.getLogger(__name__)

class FailoverTelegramBot:
    """
    📬 Failover Telegram Bot untuk backup notification system
    
    Features:
    - Multiple bot tokens untuk redundancy
    - Automatic failover detection
    - Health monitoring untuk setiap bot
    - Message queue dengan retry mechanism
    - Fallback notification methods
    - Real-time status monitoring
    """
    
    def __init__(self, redis_manager=None):
        """Initialize Failover Telegram Bot"""
        self.redis_manager = redis_manager
        
        # Bot configurations
        self.bots = {
            'primary': {
                'token': os.environ.get('TELEGRAM_BOT_TOKEN'),
                'name': 'Primary Trading Bot',
                'status': 'unknown',
                'last_check': None,
                'error_count': 0,
                'priority': 1
            },
            'backup': {
                'token': os.environ.get('TELEGRAM_BOT_TOKEN_BACKUP'),
                'name': 'Backup Trading Bot',
                'status': 'unknown',
                'last_check': None,
                'error_count': 0,
                'priority': 2
            },
            'fallback': {
                'token': os.environ.get('TELEGRAM_BOT_TOKEN_FALLBACK'),
                'name': 'Fallback Notification Bot',
                'status': 'unknown',
                'last_check': None,
                'error_count': 0,
                'priority': 3
            }
        }
        
        # Message queue
        self.message_queue = Queue()
        self.processing_thread = None
        self.is_running = False
        
        # Health monitoring
        self.health_check_interval = 300  # 5 minutes
        self.health_thread = None
        
        # Failover settings
        self.max_errors_before_failover = 3
        self.health_check_timeout = 10  # seconds
        
        # Active bot tracking
        self.active_bot = None
        
        # Initialize
        self._initialize_bots()
        self._start_background_processing()
        
        logger.info("📬 Failover Telegram Bot system initialized")
    
    def send_signal_notification(self, signal_data: Dict[str, Any], 
                                chat_ids: List[str] = None, 
                                priority: str = 'normal') -> bool:
        """
        Send signal notification dengan failover support
        
        Args:
            signal_data: Signal information
            chat_ids: List of chat IDs (default: all registered)
            priority: Message priority (high, normal, low)
            
        Returns:
            success: Boolean indicating if message was queued successfully
        """
        try:
            # Format signal message
            message = self._format_signal_message(signal_data)
            
            # Get chat IDs
            if not chat_ids:
                chat_ids = self._get_registered_chat_ids()
            
            if not chat_ids:
                logger.warning("No chat IDs available for notification")
                return False
            
            # Queue message untuk setiap chat
            for chat_id in chat_ids:
                message_item = {
                    'type': 'SIGNAL_NOTIFICATION',
                    'chat_id': chat_id,
                    'message': message,
                    'priority': priority,
                    'signal_data': signal_data,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'retry_count': 0,
                    'max_retries': 3
                }
                
                self.message_queue.put(message_item)
            
            logger.info(f"📬 Signal notification queued for {len(chat_ids)} chats")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing signal notification: {e}")
            return False
    
    def send_alert_notification(self, alert_data: Dict[str, Any], 
                               chat_ids: List[str] = None) -> bool:
        """Send alert notification"""
        try:
            message = self._format_alert_message(alert_data)
            
            if not chat_ids:
                chat_ids = self._get_registered_chat_ids()
            
            if not chat_ids:
                return False
            
            for chat_id in chat_ids:
                message_item = {
                    'type': 'ALERT_NOTIFICATION',
                    'chat_id': chat_id,
                    'message': message,
                    'priority': 'high',
                    'alert_data': alert_data,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'retry_count': 0,
                    'max_retries': 2
                }
                
                self.message_queue.put(message_item)
            
            logger.info(f"📬 Alert notification queued for {len(chat_ids)} chats")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing alert notification: {e}")
            return False
    
    def send_system_notification(self, message: str, notification_type: str = 'info',
                                chat_ids: List[str] = None) -> bool:
        """Send system notification"""
        try:
            formatted_message = self._format_system_message(message, notification_type)
            
            if not chat_ids:
                chat_ids = self._get_admin_chat_ids()  # System messages go to admins only
            
            if not chat_ids:
                return False
            
            for chat_id in chat_ids:
                message_item = {
                    'type': 'SYSTEM_NOTIFICATION',
                    'chat_id': chat_id,
                    'message': formatted_message,
                    'priority': 'high' if notification_type == 'error' else 'normal',
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'retry_count': 0,
                    'max_retries': 2
                }
                
                self.message_queue.put(message_item)
            
            logger.info(f"📬 System notification queued: {notification_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing system notification: {e}")
            return False
    
    def get_bot_status(self) -> Dict[str, Any]:
        """Get comprehensive bot status"""
        try:
            status = {
                'active_bot': self.active_bot,
                'bots': {},
                'queue_status': {
                    'pending_messages': self.message_queue.qsize(),
                    'processing_active': self.is_running
                },
                'last_update': datetime.now(timezone.utc).isoformat()
            }
            
            for bot_id, bot_info in self.bots.items():
                status['bots'][bot_id] = {
                    'name': bot_info['name'],
                    'status': bot_info['status'],
                    'last_check': bot_info['last_check'],
                    'error_count': bot_info['error_count'],
                    'priority': bot_info['priority'],
                    'has_token': bool(bot_info['token'])
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {'error': str(e)}
    
    def force_failover(self, target_bot: str = None) -> bool:
        """
        Force failover to specific bot atau next available
        
        Args:
            target_bot: Target bot ID (primary, backup, fallback)
            
        Returns:
            success: Boolean indicating failover success
        """
        try:
            if target_bot and target_bot in self.bots:
                # Check if target bot is available
                if self._check_bot_health(target_bot):
                    old_bot = self.active_bot
                    self.active_bot = target_bot
                    
                    logger.info(f"📬 Manual failover: {old_bot} -> {target_bot}")
                    self.send_system_notification(
                        f"Bot failover completed: {old_bot} -> {target_bot}",
                        'info'
                    )
                    return True
                else:
                    logger.warning(f"Target bot {target_bot} is not healthy")
                    return False
            else:
                # Find next available bot
                return self._perform_automatic_failover()
                
        except Exception as e:
            logger.error(f"Error in manual failover: {e}")
            return False
    
    def _initialize_bots(self):
        """Initialize dan check health semua bots"""
        logger.info("📬 Initializing bot health checks...")
        
        for bot_id in self.bots.keys():
            self._check_bot_health(bot_id)
        
        # Set active bot (choose healthiest with highest priority)
        self._select_active_bot()
    
    def _select_active_bot(self):
        """Select active bot berdasarkan priority dan health"""
        available_bots = []
        
        for bot_id, bot_info in self.bots.items():
            if bot_info['status'] == 'healthy' and bot_info['token']:
                available_bots.append((bot_id, bot_info['priority']))
        
        if available_bots:
            # Sort by priority (lower number = higher priority)
            available_bots.sort(key=lambda x: x[1])
            self.active_bot = available_bots[0][0]
            logger.info(f"📬 Active bot selected: {self.active_bot}")
        else:
            self.active_bot = None
            logger.warning("📬 No healthy bots available!")
    
    def _check_bot_health(self, bot_id: str) -> bool:
        """Check health of specific bot"""
        try:
            bot_info = self.bots.get(bot_id)
            if not bot_info or not bot_info['token']:
                bot_info['status'] = 'no_token'
                return False
            
            # Test bot dengan getMe API call
            url = f"https://api.telegram.org/bot{bot_info['token']}/getMe"
            
            response = requests.get(url, timeout=self.health_check_timeout)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    bot_info['status'] = 'healthy'
                    bot_info['error_count'] = 0
                    bot_info['last_check'] = datetime.now(timezone.utc).isoformat()
                    
                    logger.debug(f"📬 Bot {bot_id} health check: OK")
                    return True
            
            # Health check failed
            bot_info['status'] = 'unhealthy'
            bot_info['error_count'] += 1
            bot_info['last_check'] = datetime.now(timezone.utc).isoformat()
            
            logger.warning(f"📬 Bot {bot_id} health check failed: {response.status_code}")
            return False
            
        except Exception as e:
            bot_info = self.bots.get(bot_id, {})
            bot_info['status'] = 'error'
            bot_info['error_count'] = bot_info.get('error_count', 0) + 1
            bot_info['last_check'] = datetime.now(timezone.utc).isoformat()
            
            logger.error(f"📬 Bot {bot_id} health check error: {e}")
            return False
    
    def _perform_automatic_failover(self) -> bool:
        """Perform automatic failover to next available bot"""
        try:
            current_bot = self.active_bot
            
            # Check if current bot needs failover
            if current_bot and self.bots[current_bot]['error_count'] < self.max_errors_before_failover:
                return False  # No failover needed
            
            # Find next available bot
            available_bots = []
            for bot_id, bot_info in self.bots.items():
                if bot_id != current_bot and bot_info['token']:
                    if self._check_bot_health(bot_id):
                        available_bots.append((bot_id, bot_info['priority']))
            
            if available_bots:
                # Select bot with highest priority
                available_bots.sort(key=lambda x: x[1])
                new_bot = available_bots[0][0]
                
                old_bot = self.active_bot
                self.active_bot = new_bot
                
                logger.info(f"📬 Automatic failover: {old_bot} -> {new_bot}")
                
                # Send notification about failover
                self.send_system_notification(
                    f"🔄 Bot Failover\n\nSwitched from {old_bot or 'None'} to {new_bot}\nReason: Health check failure",
                    'warning'
                )
                
                return True
            else:
                logger.error("📬 No healthy bots available for failover!")
                
                # Send critical alert
                self.send_system_notification(
                    "🚨 CRITICAL: All Telegram bots are down!\n\nImmediate attention required.",
                    'error'
                )
                
                return False
                
        except Exception as e:
            logger.error(f"Error in automatic failover: {e}")
            return False
    
    def _start_background_processing(self):
        """Start background processing threads"""
        # Message processing thread
        if not self.processing_thread or not self.processing_thread.is_alive():
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._process_message_queue, daemon=True)
            self.processing_thread.start()
        
        # Health monitoring thread
        if not self.health_thread or not self.health_thread.is_alive():
            self.health_thread = threading.Thread(target=self._health_monitoring_loop, daemon=True)
            self.health_thread.start()
        
        logger.info("📬 Background processing started")
    
    def _process_message_queue(self):
        """Process message queue dengan failover support"""
        while self.is_running:
            try:
                # Get message from queue dengan timeout
                message_item = self.message_queue.get(timeout=1.0)
                
                # Attempt to send message
                success = self._send_message_with_failover(message_item)
                
                if not success:
                    # Retry logic
                    message_item['retry_count'] += 1
                    
                    if message_item['retry_count'] <= message_item['max_retries']:
                        # Re-queue for retry
                        self.message_queue.put(message_item)
                        logger.warning(f"📬 Message retry {message_item['retry_count']}/{message_item['max_retries']}")
                    else:
                        logger.error(f"📬 Message failed after {message_item['max_retries']} retries")
                        self._handle_failed_message(message_item)
                
                self.message_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing message queue: {e}")
                time.sleep(1)
    
    def _send_message_with_failover(self, message_item: Dict[str, Any]) -> bool:
        """Send message dengan automatic failover"""
        try:
            # Try current active bot first
            if self.active_bot:
                if self._send_telegram_message(self.active_bot, message_item):
                    return True
                else:
                    # Active bot failed, try failover
                    self._perform_automatic_failover()
            
            # Try with new active bot after failover
            if self.active_bot:
                return self._send_telegram_message(self.active_bot, message_item)
            
            return False
            
        except Exception as e:
            logger.error(f"Error in message sending with failover: {e}")
            return False
    
    def _send_telegram_message(self, bot_id: str, message_item: Dict[str, Any]) -> bool:
        """Send message menggunakan specific bot"""
        try:
            bot_info = self.bots.get(bot_id)
            if not bot_info or not bot_info['token']:
                return False
            
            url = f"https://api.telegram.org/bot{bot_info['token']}/sendMessage"
            
            data = {
                'chat_id': message_item['chat_id'],
                'text': message_item['message'],
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    # Reset error count on success
                    bot_info['error_count'] = 0
                    return True
            
            # Message failed
            bot_info['error_count'] += 1
            logger.warning(f"📬 Message send failed via {bot_id}: {response.text}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending message via {bot_id}: {e}")
            if bot_id in self.bots:
                self.bots[bot_id]['error_count'] += 1
            return False
    
    def _health_monitoring_loop(self):
        """Background health monitoring loop"""
        while self.is_running:
            try:
                time.sleep(self.health_check_interval)
                
                # Check health of all bots
                for bot_id in self.bots.keys():
                    self._check_bot_health(bot_id)
                
                # Check if failover is needed
                if self.active_bot:
                    active_bot_info = self.bots[self.active_bot]
                    if active_bot_info['error_count'] >= self.max_errors_before_failover:
                        self._perform_automatic_failover()
                else:
                    # No active bot, try to select one
                    self._select_active_bot()
                
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                time.sleep(60)  # Wait before retry
    
    def _format_signal_message(self, signal_data: Dict[str, Any]) -> str:
        """Format signal data into Telegram message"""
        try:
            symbol = signal_data.get('symbol', 'Unknown')
            action = signal_data.get('action', 'HOLD')
            confidence = signal_data.get('confidence', 0)
            entry_price = signal_data.get('entry_price', 0)
            take_profit = signal_data.get('take_profit', 0)
            stop_loss = signal_data.get('stop_loss', 0)
            
            # Confidence emoji
            if confidence >= 85:
                conf_emoji = "🔥"
            elif confidence >= 70:
                conf_emoji = "✅"
            else:
                conf_emoji = "⚠️"
            
            # Action emoji
            action_emoji = "📈" if action == "BUY" else "📉" if action == "SELL" else "⏸️"
            
            message = f"""
{action_emoji} <b>TRADING SIGNAL</b> {conf_emoji}

<b>Symbol:</b> {symbol}
<b>Action:</b> {action}
<b>Confidence:</b> {confidence}%

<b>Entry Price:</b> ${entry_price:,.4f}
<b>Take Profit:</b> ${take_profit:,.4f}
<b>Stop Loss:</b> ${stop_loss:,.4f}

<i>Time:</i> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC

⚡ <i>Automated Signal by Crypto AI</i>
            """.strip()
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting signal message: {e}")
            return f"Signal Update: {signal_data.get('symbol', 'Unknown')} - {signal_data.get('action', 'Unknown')}"
    
    def _format_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Format alert data into Telegram message"""
        try:
            alert_type = alert_data.get('type', 'Unknown')
            message = alert_data.get('message', 'Alert triggered')
            
            alert_emoji = {
                'HIGH_VOLUME': '📊',
                'PRICE_ALERT': '💰',
                'RISK_WARNING': '⚠️',
                'SYSTEM_ALERT': '🔔'
            }.get(alert_type, '🚨')
            
            formatted_message = f"""
{alert_emoji} <b>MARKET ALERT</b>

<b>Type:</b> {alert_type}
<b>Message:</b> {message}

<i>Time:</i> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
            """.strip()
            
            return formatted_message
            
        except Exception as e:
            logger.error(f"Error formatting alert message: {e}")
            return f"Alert: {alert_data.get('message', 'Unknown alert')}"
    
    def _format_system_message(self, message: str, notification_type: str) -> str:
        """Format system message"""
        type_emojis = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '🚨',
            'success': '✅'
        }
        
        emoji = type_emojis.get(notification_type, 'ℹ️')
        
        return f"""
{emoji} <b>SYSTEM {notification_type.upper()}</b>

{message}

<i>Time:</i> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
        """.strip()
    
    def _get_registered_chat_ids(self) -> List[str]:
        """Get list of registered chat IDs"""
        try:
            if self.redis_manager:
                chat_ids = self.redis_manager.get_cache('telegram_chat_ids') or []
                return chat_ids
            
            # Fallback default chat IDs (should be configured via environment)
            default_chats = os.environ.get('TELEGRAM_DEFAULT_CHAT_IDS', '').split(',')
            return [chat.strip() for chat in default_chats if chat.strip()]
            
        except Exception as e:
            logger.error(f"Error getting registered chat IDs: {e}")
            return []
    
    def _get_admin_chat_ids(self) -> List[str]:
        """Get list of admin chat IDs"""
        try:
            if self.redis_manager:
                admin_chats = self.redis_manager.get_cache('telegram_admin_chat_ids') or []
                return admin_chats
            
            # Fallback default admin chat IDs
            admin_chats = os.environ.get('TELEGRAM_ADMIN_CHAT_IDS', '').split(',')
            return [chat.strip() for chat in admin_chats if chat.strip()]
            
        except Exception as e:
            logger.error(f"Error getting admin chat IDs: {e}")
            return []
    
    def _handle_failed_message(self, message_item: Dict[str, Any]):
        """Handle message yang gagal dikirim setelah semua retries"""
        try:
            logger.error(f"📬 Message permanently failed: {message_item['type']}")
            
            # Store failed message untuk manual review
            if self.redis_manager:
                failed_key = "failed_telegram_messages"
                failed_messages = self.redis_manager.get_cache(failed_key) or []
                
                failed_messages.append({
                    **message_item,
                    'failed_at': datetime.now(timezone.utc).isoformat()
                })
                
                # Keep only last 100 failed messages
                if len(failed_messages) > 100:
                    failed_messages = failed_messages[-100:]
                
                self.redis_manager.set_cache(failed_key, failed_messages)
                
        except Exception as e:
            logger.error(f"Error handling failed message: {e}")
    
    def shutdown(self):
        """Gracefully shutdown failover bot system"""
        self.is_running = False
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
        
        if self.health_thread and self.health_thread.is_alive():
            self.health_thread.join(timeout=5.0)
        
        logger.info("📬 Failover Telegram Bot system shutdown completed")

# Global failover bot instance
failover_bot = None

def get_failover_bot():
    """Get global failover bot instance"""
    global failover_bot
    if failover_bot is None:
        try:
            from core.redis_manager import RedisManager
            redis_manager = RedisManager()
            failover_bot = FailoverTelegramBot(redis_manager=redis_manager)
        except Exception as e:
            logger.error(f"Failed to initialize failover bot: {e}")
            failover_bot = FailoverTelegramBot()  # Fallback without Redis
    
    return failover_bot

def send_signal_notification(signal_data: Dict[str, Any], chat_ids: List[str] = None) -> bool:
    """Send signal notification via failover bot"""
    return get_failover_bot().send_signal_notification(signal_data, chat_ids)

def send_alert_notification(alert_data: Dict[str, Any], chat_ids: List[str] = None) -> bool:
    """Send alert notification via failover bot"""
    return get_failover_bot().send_alert_notification(alert_data, chat_ids)

def send_system_notification(message: str, notification_type: str = 'info', chat_ids: List[str] = None) -> bool:
    """Send system notification via failover bot"""
    return get_failover_bot().send_system_notification(message, notification_type, chat_ids)

# Export
__all__ = [
    'FailoverTelegramBot', 'get_failover_bot', 'send_signal_notification',
    'send_alert_notification', 'send_system_notification'
]