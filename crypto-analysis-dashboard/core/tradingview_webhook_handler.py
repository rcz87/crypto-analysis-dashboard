#!/usr/bin/env python3
"""
TradingView Webhook Handler
Secure webhook system untuk menerima sinyal dari TradingView LuxAlgo Premium
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os

from flask import request

@dataclass
class TradingViewSignal:
    """TradingView signal data structure"""
    symbol: str
    action: str  # 'BUY', 'SELL', 'CLOSE'
    price: float
    strategy: str
    timeframe: str
    timestamp: datetime
    
    # LuxAlgo specific
    luxalgo_indicator: Optional[str] = None
    confidence: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Risk management
    position_size: Optional[float] = None
    risk_percentage: Optional[float] = None
    
    # Metadata
    exchange: str = "BINANCE"
    alert_name: Optional[str] = None
    raw_message: Optional[str] = None

class TradingViewWebhookHandler:
    """
    Secure TradingView webhook handler with authentication and validation
    
    Features:
    - HMAC signature verification
    - IP whitelist validation
    - Rate limiting protection
    - Signal parsing and validation
    - Integration with existing signal system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Security configuration
        self.webhook_secret = os.getenv('TRADINGVIEW_WEBHOOK_SECRET')
        self.allowed_ips = self._get_tradingview_ips()
        
        # Rate limiting (max 10 signals per minute)
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max = 10
        self.request_history = []
        
        # Signal validation
        self.valid_actions = ['BUY', 'SELL', 'CLOSE', 'LONG', 'SHORT']
        self.valid_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT']
        
    def _get_tradingview_ips(self) -> List[str]:
        """Get official TradingView webhook IP addresses"""
        return [
            '52.89.214.238',
            '34.212.75.30', 
            '54.218.53.128',
            '52.32.178.7'
        ]
    
    def validate_request_ip(self, client_ip: str) -> bool:
        """Validate request comes from TradingView servers"""
        if not self.allowed_ips:
            self.logger.warning("No IP whitelist configured - skipping IP validation")
            return True
            
        return client_ip in self.allowed_ips
    
    def validate_signature(self, payload: bytes, signature: str) -> bool:
        """Validate HMAC signature from TradingView"""
        if not self.webhook_secret:
            self.logger.warning("No webhook secret configured - skipping signature validation")
            return True
        
        try:
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures (constant time comparison)
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            self.logger.error(f"Signature validation error: {e}")
            return False
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if request exceeds rate limit"""
        now = datetime.now()
        
        # Clean old requests
        self.request_history = [
            req_time for req_time in self.request_history
            if (now - req_time).total_seconds() < self.rate_limit_window
        ]
        
        # Check rate limit
        if len(self.request_history) >= self.rate_limit_max:
            self.logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        # Add current request
        self.request_history.append(now)
        return True
    
    def parse_tradingview_message(self, message: str) -> Optional[TradingViewSignal]:
        """
        Parse TradingView alert message into structured signal
        
        Supports multiple formats:
        1. JSON format: {"symbol": "BTCUSDT", "action": "BUY", ...}
        2. LuxAlgo format: "LuxAlgo BUY BTCUSDT at 50000"
        3. Custom format: "{{strategy.order.action}} {{ticker}} {{close}}"
        """
        try:
            # Try JSON format first
            if message.strip().startswith('{'):
                return self._parse_json_message(message)
            
            # Try LuxAlgo specific format
            if 'LuxAlgo' in message.upper():
                return self._parse_luxalgo_message(message)
            
            # Try generic TradingView format
            return self._parse_generic_message(message)
            
        except Exception as e:
            self.logger.error(f"Message parsing error: {e}")
            return None
    
    def _parse_json_message(self, message: str) -> Optional[TradingViewSignal]:
        """Parse JSON formatted message"""
        try:
            data = json.loads(message)
            
            return TradingViewSignal(
                symbol=data.get('symbol', '').upper(),
                action=data.get('action', '').upper(),
                price=float(data.get('price', 0)),
                strategy=data.get('strategy', 'TradingView'),
                timeframe=data.get('timeframe', '1h'),
                timestamp=datetime.now(),
                luxalgo_indicator=data.get('indicator'),
                confidence=data.get('confidence'),
                stop_loss=data.get('stop_loss'),
                take_profit=data.get('take_profit'),
                position_size=data.get('position_size'),
                risk_percentage=data.get('risk_percentage'),
                exchange=data.get('exchange', 'BINANCE'),
                alert_name=data.get('alert_name'),
                raw_message=message
            )
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.error(f"JSON parsing error: {e}")
            return None
    
    def _parse_luxalgo_message(self, message: str) -> Optional[TradingViewSignal]:
        """Parse LuxAlgo specific message format"""
        try:
            # Example: "LuxAlgo BUY BTCUSDT at 50000 - Confluence Signal"
            parts = message.upper().split()
            
            if len(parts) < 4:
                return None
            
            # Extract components
            action = None
            symbol = None
            price = None
            
            for i, part in enumerate(parts):
                if part in self.valid_actions:
                    action = part
                elif any(sym in part for sym in self.valid_symbols):
                    symbol = part
                elif part.replace('.', '').isdigit() and i > 0 and parts[i-1] == 'AT':
                    price = float(part)
            
            if not all([action, symbol]):
                return None
                
            return TradingViewSignal(
                symbol=symbol,
                action=action,
                price=price or 0.0,
                strategy='LuxAlgo Premium',
                timeframe='1h',  # Default
                timestamp=datetime.now(),
                luxalgo_indicator='LuxAlgo',
                raw_message=message
            )
            
        except (ValueError, IndexError) as e:
            self.logger.error(f"LuxAlgo parsing error: {e}")
            return None
    
    def _parse_generic_message(self, message: str) -> Optional[TradingViewSignal]:
        """Parse generic TradingView alert format"""
        try:
            # Common patterns: "BUY BTCUSDT 50000" or "SELL ETHUSDT"
            parts = message.upper().split()
            
            action = parts[0] if parts and parts[0] in self.valid_actions else None
            symbol = None
            price = None
            
            for part in parts[1:]:
                if any(sym in part for sym in self.valid_symbols):
                    symbol = part
                elif part.replace('.', '').isdigit():
                    price = float(part)
                    
            if not all([action, symbol]):
                return None
                
            return TradingViewSignal(
                symbol=symbol,
                action=action,
                price=price or 0.0,
                strategy='TradingView',
                timeframe='1h',
                timestamp=datetime.now(),
                raw_message=message
            )
            
        except (ValueError, IndexError) as e:
            self.logger.error(f"Generic parsing error: {e}")
            return None
    
    def validate_signal(self, signal: TradingViewSignal) -> tuple[bool, str]:
        """Validate parsed signal for safety"""
        if not signal:
            return False, "Invalid signal data"
        
        # Check required fields
        if not signal.symbol:
            return False, "Missing symbol"
        
        if not signal.action:
            return False, "Missing action"
        
        # Validate action
        if signal.action not in self.valid_actions:
            return False, f"Invalid action: {signal.action}"
        
        # Validate symbol
        if signal.symbol not in self.valid_symbols:
            return False, f"Unsupported symbol: {signal.symbol}"
        
        # Validate price (if provided)
        if signal.price and (signal.price <= 0 or signal.price > 1000000):
            return False, f"Invalid price: {signal.price}"
        
        # Validate risk management
        if signal.risk_percentage and (signal.risk_percentage <= 0 or signal.risk_percentage > 10):
            return False, f"Risk percentage too high: {signal.risk_percentage}%"
        
        return True, "Valid signal"
    
    def process_webhook(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main webhook processing function
        
        Returns response for TradingView
        """
        try:
            # Extract request info
            client_ip = request_data.get('remote_addr', 'unknown')
            payload = request_data.get('data', b'')
            signature = request_data.get('signature', '')
            message = request_data.get('message', '')
            
            # Security validations
            if not self.validate_request_ip(client_ip):
                return {
                    'success': False,
                    'error': 'Unauthorized IP address',
                    'code': 403
                }
            
            if not self.check_rate_limit(client_ip):
                return {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'code': 429
                }
            
            if not self.validate_signature(payload, signature):
                return {
                    'success': False,
                    'error': 'Invalid signature',
                    'code': 401
                }
            
            # Parse signal
            signal = self.parse_tradingview_message(message)
            if not signal:
                return {
                    'success': False,
                    'error': 'Unable to parse signal',
                    'code': 400
                }
            
            # Validate signal
            is_valid, validation_message = self.validate_signal(signal)
            if not is_valid:
                return {
                    'success': False,
                    'error': f'Signal validation failed: {validation_message}',
                    'code': 400
                }
            
            # Process signal (integrate with existing system)
            processing_result = self._integrate_with_trading_system(signal)
            
            # Log successful processing
            self.logger.info(f"TradingView signal processed: {signal.action} {signal.symbol} @ {signal.price}")
            
            return {
                'success': True,
                'message': 'Signal processed successfully',
                'signal_id': processing_result.get('signal_id'),
                'timestamp': datetime.now().isoformat(),
                'processing_time_ms': processing_result.get('processing_time_ms', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Webhook processing error: {e}")
            return {
                'success': False,
                'error': 'Internal processing error',
                'code': 500
            }
    
    def _integrate_with_trading_system(self, signal: TradingViewSignal) -> Dict[str, Any]:
        """Integrate TradingView signal with our existing trading system"""
        try:
            # Import our existing signal system
            from core.enhanced_sharp_signal_engine import get_enhanced_signal_engine
            from core.telegram_notifier import get_telegram_notifier
            
            signal_engine = get_enhanced_signal_engine()
            telegram = get_telegram_notifier()
            
            # Convert TradingView signal to our system format
            trading_signal = {
                'symbol': signal.symbol,
                'action': signal.action.lower(),
                'entry_price': signal.price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'confidence': signal.confidence or 75,
                'strategy': signal.strategy,
                'source': 'TradingView-LuxAlgo',
                'timeframe': signal.timeframe,
                'timestamp': signal.timestamp.isoformat(),
                'risk_percentage': signal.risk_percentage or 2.0
            }
            
            # Process through our signal engine for validation
            enhanced_signal = signal_engine.enhance_signal_with_context(trading_signal)
            
            # Send Telegram notification
            if telegram:
                notification_message = self._format_telegram_message(signal, enhanced_signal)
                telegram.send_trading_signal(notification_message, priority='high')
            
            # Store signal for tracking
            signal_id = self._store_signal_record(signal, enhanced_signal)
            
            return {
                'signal_id': signal_id,
                'processing_time_ms': 50,  # Placeholder
                'enhanced': True,
                'telegram_sent': telegram is not None
            }
            
        except Exception as e:
            self.logger.error(f"Trading system integration error: {e}")
            return {
                'signal_id': None,
                'processing_time_ms': 0,
                'enhanced': False,
                'error': str(e)
            }
    
    def _format_telegram_message(self, tv_signal: TradingViewSignal, enhanced_signal: Dict) -> str:
        """Format signal for Telegram notification"""
        direction_emoji = "🟢" if tv_signal.action in ['BUY', 'LONG'] else "🔴"
        
        message = f"""
{direction_emoji} <b>TradingView LuxAlgo Signal</b>

📊 <b>Symbol:</b> {tv_signal.symbol}
⚡ <b>Action:</b> {tv_signal.action}
💰 <b>Price:</b> ${tv_signal.price:,.2f}
📈 <b>Strategy:</b> {tv_signal.strategy}
⏰ <b>Time:</b> {tv_signal.timeframe}

🎯 <b>LuxAlgo Indicator:</b> {tv_signal.luxalgo_indicator or 'Premium Signal'}
🔍 <b>Confidence:</b> {tv_signal.confidence or 'High'}%

💡 <b>Enhanced Analysis:</b>
{enhanced_signal.get('reasoning', 'Processing complete')}

⚠️ <b>Risk Management:</b>
Stop Loss: ${tv_signal.stop_loss or 'Manual'}
Take Profit: ${tv_signal.take_profit or 'Manual'}
Risk: {tv_signal.risk_percentage or 2}%

🤖 <i>Automated from TradingView LuxAlgo Premium</i>
        """.strip()
        
        return message
    
    def _store_signal_record(self, signal: TradingViewSignal, enhanced_signal: Dict) -> str:
        """Store signal record for tracking and analysis"""
        try:
            signal_id = f"TV_{signal.symbol}_{int(signal.timestamp.timestamp())}"
            
            # In production, store to database
            # For now, log the signal
            self.logger.info(f"Signal stored: {signal_id} - {signal.action} {signal.symbol}")
            
            return signal_id
            
        except Exception as e:
            self.logger.error(f"Signal storage error: {e}")
            return f"ERROR_{int(datetime.now().timestamp())}"
    
    def get_webhook_setup_guide(self) -> Dict[str, Any]:
        """Generate setup guide for TradingView webhook configuration"""
        webhook_url = f"https://{os.getenv('REPLIT_DOMAINS', 'your-app.replit.app')}/api/webhooks/tradingview"
        
        return {
            'webhook_url': webhook_url,
            'setup_instructions': {
                'step_1': 'Go to TradingView > Alerts > Create Alert',
                'step_2': 'Configure your LuxAlgo indicator alert',
                'step_3': 'In Notifications tab, select Webhook URL',
                'step_4': f'Enter webhook URL: {webhook_url}',
                'step_5': 'Use one of the message formats below'
            },
            'recommended_message_formats': {
                'json_format': {
                    'description': 'Most comprehensive format',
                    'template': '''
{
    "symbol": "{{ticker}}",
                    "action": "{{strategy.order.action}}",
                    "price": {{close}},
                    "strategy": "LuxAlgo Premium",
                    "timeframe": "{{interval}}",
                    "indicator": "{{plot_title}}",
                    "confidence": 85
}
                    '''.strip()
                },
                'simple_format': {
                    'description': 'Basic format for quick setup',
                    'template': 'LuxAlgo {{strategy.order.action}} {{ticker}} at {{close}}'
                },
                'custom_format': {
                    'description': 'Custom with risk management',
                    'template': '{{strategy.order.action}} {{ticker}} {{close}} SL={{strategy.order.contracts}} TP={{high}}'
                }
            },
            'security_setup': {
                'webhook_secret': 'Add TRADINGVIEW_WEBHOOK_SECRET to Replit Secrets',
                'ip_whitelist': 'TradingView IPs automatically whitelisted',
                'rate_limiting': '10 requests per minute maximum'
            }
        }

# Global webhook handler instance
tradingview_handler = TradingViewWebhookHandler()

def get_tradingview_webhook_handler():
    """Get the global TradingView webhook handler"""
    return tradingview_handler

if __name__ == "__main__":
    # Test webhook handler
    handler = TradingViewWebhookHandler()
    
    # Test message parsing
    test_messages = [
        '{"symbol": "BTCUSDT", "action": "BUY", "price": 50000}',
        'LuxAlgo BUY BTCUSDT at 50000',
        'BUY ETHUSDT 2500'
    ]
    
    print("TradingView Webhook Handler Test")
    print("=" * 40)
    
    for i, message in enumerate(test_messages, 1):
        signal = handler.parse_tradingview_message(message)
        print(f"\nTest {i}: {message}")
        if signal:
            print(f"  ✅ Parsed: {signal.action} {signal.symbol} @ ${signal.price}")
            is_valid, msg = handler.validate_signal(signal)
            print(f"  {'✅' if is_valid else '❌'} Validation: {msg}")
        else:
            print(f"  ❌ Failed to parse")