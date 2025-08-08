"""
Enhanced Alert System with Customizable Filters
Provides advanced alerting capabilities with user-defined rules and priorities
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import os

logger = logging.getLogger(__name__)

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    enabled: bool = True
    conditions: Dict[str, Any] = None
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    notification_channels: List[str] = None
    cooldown_minutes: int = 60
    created_at: datetime = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}
        if self.notification_channels is None:
            self.notification_channels = ["telegram"]
        if self.created_at is None:
            self.created_at = datetime.now()

class AlertManager:
    """
    Advanced alert management system with customizable filters
    - Create custom alert rules based on conditions
    - Filter signals by confidence, symbol, timeframe, indicators
    - Priority-based alerting
    - Alert history and deduplication
    """
    
    def __init__(self, telegram_notifier=None, redis_manager=None):
        self.telegram_notifier = telegram_notifier
        self.redis_manager = redis_manager
        
        # Alert rules storage (in-memory or Redis)
        self.alert_rules = {}
        self.alert_history = []
        
        # Default alert rules
        self._initialize_default_rules()
        
        logger.info("🔔 Enhanced Alert Manager initialized")
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        # High confidence signals rule
        self.add_alert_rule(AlertRule(
            rule_id="high_confidence",
            name="High Confidence Signals",
            conditions={
                "confidence_min": 80,
                "action": ["BUY", "SELL", "STRONG_BUY", "STRONG_SELL"]
            },
            priority="HIGH",
            cooldown_minutes=30
        ))
        
        # SMC breakout rule
        self.add_alert_rule(AlertRule(
            rule_id="smc_breakout",
            name="SMC Structure Break",
            conditions={
                "indicators_contains": ["CHoCH", "BOS"],
                "confidence_min": 75
            },
            priority="HIGH",
            cooldown_minutes=60
        ))
        
        # Volume spike rule
        self.add_alert_rule(AlertRule(
            rule_id="volume_spike",
            name="High Volume Alert",
            conditions={
                "volume_spike": True,
                "price_change_percent_min": 2
            },
            priority="MEDIUM",
            cooldown_minutes=120
        ))
        
        # Funding rate alert
        self.add_alert_rule(AlertRule(
            rule_id="funding_overheat",
            name="Funding Rate Overheat",
            conditions={
                "funding_rate_max": -3,  # Negative for shorts
                "funding_rate_min": 3    # Positive for longs
            },
            priority="CRITICAL",
            cooldown_minutes=240
        ))
    
    def add_alert_rule(self, rule: AlertRule) -> bool:
        """Add or update an alert rule"""
        try:
            self.alert_rules[rule.rule_id] = rule
            logger.info(f"✅ Alert rule added/updated: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Error adding alert rule: {e}")
            return False
    
    def remove_alert_rule(self, rule_id: str) -> bool:
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"🗑️ Alert rule removed: {rule_id}")
            return True
        return False
    
    def toggle_alert_rule(self, rule_id: str, enabled: bool) -> bool:
        """Enable or disable an alert rule"""
        if rule_id in self.alert_rules:
            self.alert_rules[rule_id].enabled = enabled
            logger.info(f"{'✅' if enabled else '❌'} Alert rule {rule_id} {'enabled' if enabled else 'disabled'}")
            return True
        return False
    
    def evaluate_signal(self, signal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate a signal against all active alert rules
        Returns list of triggered alerts with priorities
        """
        triggered_alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
                
            # Check if rule conditions are met
            if self._check_conditions(signal_data, rule.conditions):
                # Check cooldown
                if not self._is_in_cooldown(rule_id, signal_data.get('symbol')):
                    triggered_alerts.append({
                        'rule': rule,
                        'signal': signal_data,
                        'triggered_at': datetime.now()
                    })
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        triggered_alerts.sort(key=lambda x: priority_order.get(x['rule'].priority, 999))
        
        return triggered_alerts
    
    def _check_conditions(self, signal_data: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Check if signal meets rule conditions"""
        if not conditions:
            return True
            
        # Check confidence threshold
        if 'confidence_min' in conditions:
            if signal_data.get('confidence', 0) < conditions['confidence_min']:
                return False
        
        # Check action type
        if 'action' in conditions:
            if signal_data.get('action') not in conditions['action']:
                return False
        
        # Check symbol filter
        if 'symbols' in conditions:
            if signal_data.get('symbol') not in conditions['symbols']:
                return False
        
        # Check timeframe filter
        if 'timeframes' in conditions:
            if signal_data.get('timeframe') not in conditions['timeframes']:
                return False
        
        # Check indicator presence
        if 'indicators_contains' in conditions:
            signal_indicators = signal_data.get('smc_indicators', [])
            required_indicators = conditions['indicators_contains']
            if not any(ind in str(signal_indicators) for ind in required_indicators):
                return False
        
        # Check volume spike
        if 'volume_spike' in conditions and conditions['volume_spike']:
            volume_data = signal_data.get('volume_analysis', {})
            if not volume_data.get('is_spike', False):
                return False
        
        # Check price change
        if 'price_change_percent_min' in conditions:
            price_change = abs(signal_data.get('price_change_percent', 0))
            if price_change < conditions['price_change_percent_min']:
                return False
        
        # Check funding rate
        if 'funding_rate_max' in conditions or 'funding_rate_min' in conditions:
            funding_rate = signal_data.get('derivatives_data', {}).get('funding_rate', 0)
            if 'funding_rate_max' in conditions and funding_rate > conditions['funding_rate_max']:
                return False
            if 'funding_rate_min' in conditions and funding_rate < conditions['funding_rate_min']:
                return False
        
        # Check risk level
        if 'risk_levels' in conditions:
            if signal_data.get('risk_level') not in conditions['risk_levels']:
                return False
        
        return True
    
    def _is_in_cooldown(self, rule_id: str, symbol: str) -> bool:
        """Check if alert is in cooldown period"""
        if not self.redis_manager:
            # Check in-memory history
            cooldown_key = f"{rule_id}:{symbol}"
            for alert in self.alert_history[-50:]:  # Check last 50 alerts
                if alert.get('cooldown_key') == cooldown_key:
                    alert_time = alert.get('timestamp')
                    if isinstance(alert_time, str):
                        alert_time = datetime.fromisoformat(alert_time)
                    
                    rule = self.alert_rules.get(rule_id)
                    if rule and (datetime.now() - alert_time).total_seconds() < (rule.cooldown_minutes * 60):
                        return True
            return False
        else:
            # Use Redis for cooldown check
            cooldown_key = f"alert_cooldown:{rule_id}:{symbol}"
            return self.redis_manager.get(cooldown_key) is not None
    
    def send_alerts(self, triggered_alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send alerts through configured channels"""
        results = {
            'sent': 0,
            'failed': 0,
            'alerts': []
        }
        
        for alert_data in triggered_alerts:
            rule = alert_data['rule']
            signal = alert_data['signal']
            
            # Format alert message
            message = self._format_alert_message(rule, signal)
            
            # Send through configured channels
            for channel in rule.notification_channels:
                if channel == 'telegram' and self.telegram_notifier:
                    success = self._send_telegram_alert(message, rule.priority)
                    
                    if success:
                        results['sent'] += 1
                        # Record alert in history
                        self._record_alert(rule, signal)
                    else:
                        results['failed'] += 1
                    
                    results['alerts'].append({
                        'rule_name': rule.name,
                        'priority': rule.priority,
                        'channel': channel,
                        'success': success
                    })
        
        return results
    
    def _format_alert_message(self, rule: AlertRule, signal: Dict[str, Any]) -> str:
        """Format alert message based on rule and signal"""
        priority_emoji = {
            'CRITICAL': '🚨🚨🚨',
            'HIGH': '🚨🚨',
            'MEDIUM': '🚨',
            'LOW': '📢'
        }
        
        emoji = priority_emoji.get(rule.priority, '📢')
        
        # Build message
        message = f"{emoji} <b>{rule.name}</b>\n\n"
        message += f"📊 <b>{signal.get('symbol', 'N/A')}</b> ({signal.get('timeframe', '1H')})\n"
        message += f"🎯 <b>Signal:</b> {signal.get('action', 'N/A')}\n"
        message += f"💰 <b>Price:</b> ${signal.get('current_price', 0):,.6f}\n"
        message += f"📈 <b>Confidence:</b> {signal.get('confidence', 0):.1f}%\n"
        
        # Add specific alert reason
        if 'smc_indicators' in signal and signal['smc_indicators']:
            message += f"\n<b>SMC Indicators:</b>\n"
            for ind in signal['smc_indicators'][:3]:  # Show top 3
                message += f"• {ind}\n"
        
        # Add risk info if available
        if 'risk_management' in signal:
            risk = signal['risk_management']
            message += f"\n<b>Risk Management:</b>\n"
            message += f"• Position Size: {risk.get('position_size', 0):.6f}\n"
            message += f"• Leverage: {risk.get('recommended_leverage', 1)}x\n"
            message += f"• Max Loss: ${risk.get('max_loss_usd', 0):.2f}\n"
        
        # Add alert metadata
        message += f"\n<i>Alert: {rule.name} | Priority: {rule.priority}</i>"
        
        return message
    
    def _send_telegram_alert(self, message: str, priority: str) -> bool:
        """Send Telegram alert with priority handling"""
        try:
            # Get appropriate chat ID based on priority
            if priority == 'CRITICAL':
                # Send to admin immediately
                chat_id = os.environ.get('ADMIN_CHAT_ID', '5899681906')
            else:
                # Send to regular channel
                chat_id = os.environ.get('TELEGRAM_CHAT_ID', os.environ.get('ADMIN_CHAT_ID', '5899681906'))
            
            return self.telegram_notifier.send_message(chat_id, message)
            
        except Exception as e:
            logger.error(f"Telegram alert error: {e}")
            return False
    
    def _record_alert(self, rule: AlertRule, signal: Dict[str, Any]):
        """Record alert in history"""
        alert_record = {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'symbol': signal.get('symbol'),
            'action': signal.get('action'),
            'confidence': signal.get('confidence'),
            'priority': rule.priority,
            'timestamp': datetime.now().isoformat(),
            'cooldown_key': f"{rule.rule_id}:{signal.get('symbol')}"
        }
        
        # Store in memory
        self.alert_history.append(alert_record)
        
        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        # Store cooldown in Redis if available
        if self.redis_manager:
            cooldown_key = f"alert_cooldown:{rule.rule_id}:{signal.get('symbol')}"
            self.redis_manager.setex(cooldown_key, rule.cooldown_minutes * 60, "1")
    
    def get_alert_rules(self) -> List[Dict[str, Any]]:
        """Get all alert rules"""
        return [
            {
                **asdict(rule),
                'created_at': rule.created_at.isoformat() if rule.created_at else None
            }
            for rule in self.alert_rules.values()
        ]
    
    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def create_custom_rule(self, rule_config: Dict[str, Any]) -> AlertRule:
        """Create custom alert rule from configuration"""
        try:
            # Validate required fields
            if 'name' not in rule_config:
                raise ValueError("Rule name is required")
            
            # Generate rule ID
            rule_id = rule_config.get('rule_id', f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            # Create rule
            rule = AlertRule(
                rule_id=rule_id,
                name=rule_config['name'],
                enabled=rule_config.get('enabled', True),
                conditions=rule_config.get('conditions', {}),
                priority=rule_config.get('priority', 'MEDIUM'),
                notification_channels=rule_config.get('notification_channels', ['telegram']),
                cooldown_minutes=rule_config.get('cooldown_minutes', 60)
            )
            
            # Add to rules
            self.add_alert_rule(rule)
            
            return rule
            
        except Exception as e:
            logger.error(f"Error creating custom rule: {e}")
            raise