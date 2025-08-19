"""
🚨 SMC Alert System - Automatic Telegram alerts untuk significant SMC events
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import threading

logger = logging.getLogger(__name__)

class SMCAlertSystem:
    """Automatic alert system untuk significant SMC events"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_threshold = 0.7  # Minimum strength untuk trigger alert
        self.last_alerts = {}  # Prevent spam alerts
        self.telegram_enabled = False
        
        try:
            # Try to import telegram bot
            from .telegram_bot import TelegramBot
            self.telegram = TelegramBot()
            self.telegram_enabled = True
            self.logger.info("🚨 SMC Alert System initialized with Telegram")
        except ImportError:
            self.logger.warning("Telegram bot not available for SMC alerts")
            self.telegram = None
    
    def check_and_alert(self, smc_data: Dict[str, Any], symbol: str, timeframe: str):
        """
        Check untuk significant SMC events dan kirim alert jika perlu
        
        Args:
            smc_data: SMC analysis data
            symbol: Trading symbol
            timeframe: Timeframe
        """
        try:
            # Check BOS events
            self._check_bos_alerts(smc_data, symbol, timeframe)
            
            # Check liquidity sweep events
            self._check_liquidity_alerts(smc_data, symbol, timeframe)
            
            # Check high-strength Order Block formations
            self._check_order_block_alerts(smc_data, symbol, timeframe)
            
            # Check significant FVG formations
            self._check_fvg_alerts(smc_data, symbol, timeframe)
            
        except Exception as e:
            self.logger.error(f"SMC alert check error: {e}")
    
    def _check_bos_alerts(self, smc_data: Dict, symbol: str, timeframe: str):
        """Check dan alert untuk Break of Structure events"""
        try:
            bos_data = smc_data.get('break_of_structure')
            if not bos_data:
                return
            
            # Handle list format
            if isinstance(bos_data, list):
                for bos in bos_data:
                    self._process_bos_alert(bos, symbol, timeframe)
            else:
                self._process_bos_alert(bos_data, symbol, timeframe)
                
        except Exception as e:
            self.logger.error(f"BOS alert check error: {e}")
    
    def _process_bos_alert(self, bos: Dict, symbol: str, timeframe: str):
        """Process individual BOS alert"""
        try:
            confidence = bos.get('confidence', 0)
            volume_confirmation = bos.get('volume_confirmation', False)
            
            if confidence > self.alert_threshold and volume_confirmation:
                alert_key = f"bos_{symbol}_{timeframe}_{bos.get('price', 0)}"
                
                if not self._is_duplicate_alert(alert_key):
                    direction = bos.get('direction', 'unknown')
                    price = bos.get('price', 'N/A')
                    
                    message = f"🚨 *BOS ALERT* 🚨\n\n"
                    message += f"📊 *Symbol*: {symbol}\n"
                    message += f"⏰ *Timeframe*: {timeframe}\n"
                    message += f"📈 *Direction*: {direction.upper()}\n"
                    message += f"💰 *Price*: {price}\n"
                    message += f"🎯 *Confidence*: {confidence:.1%}\n"
                    message += f"📊 *Volume Confirmed*: {'✅' if volume_confirmation else '❌'}\n"
                    message += f"⏰ *Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    self._send_telegram_alert(message)
                    self._mark_alert_sent(alert_key)
                    
        except Exception as e:
            self.logger.error(f"BOS alert processing error: {e}")
    
    def _check_liquidity_alerts(self, smc_data: Dict, symbol: str, timeframe: str):
        """Check dan alert untuk Liquidity Sweep events"""
        try:
            liquidity_data = smc_data.get('liquidity_sweep')
            if not liquidity_data:
                return
            
            # Handle list format
            if isinstance(liquidity_data, list):
                for liq in liquidity_data:
                    self._process_liquidity_alert(liq, symbol, timeframe)
            else:
                self._process_liquidity_alert(liquidity_data, symbol, timeframe)
                
        except Exception as e:
            self.logger.error(f"Liquidity alert check error: {e}")
    
    def _process_liquidity_alert(self, liquidity: Dict, symbol: str, timeframe: str):
        """Process individual liquidity sweep alert"""
        try:
            strength = liquidity.get('strength', 0)
            volume_spike = liquidity.get('volume_spike', False)
            
            if strength > self.alert_threshold:
                alert_key = f"liquidity_{symbol}_{timeframe}_{liquidity.get('sweep_price', 0)}"
                
                if not self._is_duplicate_alert(alert_key):
                    direction = liquidity.get('direction', 'unknown')
                    sweep_price = liquidity.get('sweep_price', 'N/A')
                    sweep_type = liquidity.get('sweep_type', 'liquidity_sweep')
                    
                    message = f"💧 *LIQUIDITY SWEEP ALERT* 💧\n\n"
                    message += f"📊 *Symbol*: {symbol}\n"
                    message += f"⏰ *Timeframe*: {timeframe}\n"
                    message += f"📈 *Direction*: {direction.upper()}\n"
                    message += f"💰 *Sweep Price*: {sweep_price}\n"
                    message += f"🎯 *Strength*: {strength:.1%}\n"
                    message += f"📊 *Type*: {sweep_type}\n"
                    message += f"📈 *Volume Spike*: {'✅' if volume_spike else '❌'}\n"
                    message += f"⏰ *Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    
                    self._send_telegram_alert(message)
                    self._mark_alert_sent(alert_key)
                    
        except Exception as e:
            self.logger.error(f"Liquidity alert processing error: {e}")
    
    def _check_order_block_alerts(self, smc_data: Dict, symbol: str, timeframe: str):
        """Check dan alert untuk high-strength Order Block formations"""
        try:
            order_blocks = smc_data.get('order_blocks', {})
            
            # Check bullish OBs
            bullish_obs = order_blocks.get('bullish', [])
            for ob in bullish_obs:
                if ob.get('strength', 0) > 0.8:  # Higher threshold for OB alerts
                    self._process_ob_alert(ob, symbol, timeframe, 'BULLISH')
            
            # Check bearish OBs
            bearish_obs = order_blocks.get('bearish', [])
            for ob in bearish_obs:
                if ob.get('strength', 0) > 0.8:
                    self._process_ob_alert(ob, symbol, timeframe, 'BEARISH')
                    
        except Exception as e:
            self.logger.error(f"Order Block alert check error: {e}")
    
    def _process_ob_alert(self, ob: Dict, symbol: str, timeframe: str, direction: str):
        """Process Order Block alert"""
        try:
            alert_key = f"ob_{direction}_{symbol}_{timeframe}_{ob.get('price_level', 0)}"
            
            if not self._is_duplicate_alert(alert_key):
                strength = ob.get('strength', 0)
                price_level = ob.get('price_level', 'N/A')
                volume = ob.get('volume', 0)
                
                message = f"🧱 *{direction} ORDER BLOCK ALERT* 🧱\n\n"
                message += f"📊 *Symbol*: {symbol}\n"
                message += f"⏰ *Timeframe*: {timeframe}\n"
                message += f"💰 *Price Level*: {price_level}\n"
                message += f"🎯 *Strength*: {strength:.1%}\n"
                message += f"📊 *Volume*: {volume:,.0f}\n"
                message += f"📈 *Status*: {ob.get('mitigation_status', 'unknown')}\n"
                message += f"⏰ *Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                self._send_telegram_alert(message)
                self._mark_alert_sent(alert_key)
                
        except Exception as e:
            self.logger.error(f"OB alert processing error: {e}")
    
    def _check_fvg_alerts(self, smc_data: Dict, symbol: str, timeframe: str):
        """Check dan alert untuk significant FVG formations"""
        try:
            fvgs = smc_data.get('fair_value_gaps', [])
            
            for fvg in fvgs:
                strength = fvg.get('strength', 0)
                gap_size = fvg.get('gap_size', 0)
                
                # Alert untuk large FVGs dengan good strength
                if strength > self.alert_threshold and gap_size > 100:  # Adjust gap_size threshold as needed
                    alert_key = f"fvg_{symbol}_{timeframe}_{fvg.get('upper_level', 0)}"
                    
                    if not self._is_duplicate_alert(alert_key):
                        direction = fvg.get('direction', 'unknown')
                        upper_level = fvg.get('upper_level', 'N/A')
                        lower_level = fvg.get('lower_level', 'N/A')
                        
                        message = f"📊 *FVG ALERT* 📊\n\n"
                        message += f"📊 *Symbol*: {symbol}\n"
                        message += f"⏰ *Timeframe*: {timeframe}\n"
                        message += f"📈 *Direction*: {direction.upper()}\n"
                        message += f"📊 *Upper Level*: {upper_level}\n"
                        message += f"📊 *Lower Level*: {lower_level}\n"
                        message += f"📏 *Gap Size*: {gap_size}\n"
                        message += f"🎯 *Strength*: {strength:.1%}\n"
                        message += f"📈 *Fill Status*: {fvg.get('fill_status', 'unknown')}\n"
                        message += f"⏰ *Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        
                        self._send_telegram_alert(message)
                        self._mark_alert_sent(alert_key)
                        
        except Exception as e:
            self.logger.error(f"FVG alert check error: {e}")
    
    def _is_duplicate_alert(self, alert_key: str) -> bool:
        """Check apakah alert sudah dikirim recently"""
        try:
            last_sent = self.last_alerts.get(alert_key)
            if last_sent:
                time_diff = (datetime.now() - last_sent).total_seconds()
                return time_diff < 3600  # 1 hour cooldown
            return False
        except:
            return False
    
    def _mark_alert_sent(self, alert_key: str):
        """Mark alert sebagai sudah dikirim"""
        self.last_alerts[alert_key] = datetime.now()
    
    def _send_telegram_alert(self, message: str):
        """Send alert ke Telegram"""
        try:
            if self.telegram_enabled and self.telegram:
                # Use threading untuk non-blocking alert
                threading.Thread(target=self._send_async_alert, args=(message,)).start()
                self.logger.info("📱 SMC alert sent to Telegram")
            else:
                self.logger.info(f"📱 SMC Alert (Telegram disabled): {message[:100]}...")
        except Exception as e:
            self.logger.error(f"Telegram alert send error: {e}")
    
    def _send_async_alert(self, message: str):
        """Send telegram alert asynchronously"""
        try:
            if hasattr(self.telegram, 'send_signal_alert'):
                self.telegram.send_signal_alert(message)
            else:
                self.logger.warning("Telegram send_signal_alert method not available")
        except Exception as e:
            self.logger.error(f"Async telegram alert error: {e}")

# Global instance
smc_alert_system = SMCAlertSystem()