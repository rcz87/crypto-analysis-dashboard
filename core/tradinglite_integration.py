#!/usr/bin/env python3
"""
TradingLite Integration Module
Integrates TradingLite Gold features with our trading system:
- Liquidity Heatmaps data
- Order Flow analysis
- Real-time bid/ask spreads
- Custom LitScript indicators
"""

import asyncio
import websocket
import json
import struct
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import threading
from collections import deque
import requests

logger = logging.getLogger(__name__)

@dataclass
class TradingLiteConfig:
    """Configuration for TradingLite connection"""
    account_token: str  # User's account token from TradingLite
    workspace_id: str   # Workspace ID
    version: str = "v0.41.13"  # TradingLite version
    use_testnet: bool = False
    subscription_level: str = "gold"  # gold, silver, etc.

@dataclass
class LiquidityData:
    """Liquidity heatmap data structure"""
    timestamp: datetime
    price_level: float
    bid_liquidity: float
    ask_liquidity: float
    cumulative_bid: float
    cumulative_ask: float
    liquidity_score: float  # 0-100 score
    is_significant: bool

@dataclass
class OrderFlowData:
    """Order flow analysis data"""
    timestamp: datetime
    buy_volume: float
    sell_volume: float
    delta: float  # buy - sell
    cumulative_delta: float
    buy_pressure: float  # percentage
    sell_pressure: float
    flow_direction: str  # 'bullish', 'bearish', 'neutral'

class TradingLiteIntegration:
    """
    Main integration class for TradingLite Gold features
    """
    
    def __init__(self, config: TradingLiteConfig):
        self.config = config
        self.ws = None
        self.connected = False
        
        # Data storage
        self.liquidity_data: deque = deque(maxlen=1000)
        self.order_flow_data: deque = deque(maxlen=1000)
        self.bid_ask_spreads: deque = deque(maxlen=100)
        
        # Callbacks
        self.on_liquidity_update: Optional[Callable] = None
        self.on_order_flow_update: Optional[Callable] = None
        
        # Threading
        self.ws_thread = None
        self.processing_thread = None
        self.running = False
        
        # Metrics
        self.metrics = {
            'messages_received': 0,
            'liquidity_updates': 0,
            'order_flow_updates': 0,
            'errors': 0,
            'last_update': None
        }
        
        self.logger = logging.getLogger(f"{__name__}.TradingLiteIntegration")
        self.logger.info(f"🎯 TradingLite Integration initialized - {config.subscription_level.upper()} subscription")
    
    def connect(self):
        """Connect to TradingLite WebSocket"""
        try:
            # WebSocket URL for TradingLite (unofficial API)
            ws_url = f"wss://tradinglite.com/ws/{self.config.workspace_id}"
            
            # Headers with authentication
            headers = {
                "Authorization": f"Bearer {self.config.account_token}",
                "Version": self.config.version
            }
            
            self.ws = websocket.WebSocketApp(
                ws_url,
                header=headers,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start WebSocket in separate thread
            self.running = True
            self.ws_thread = threading.Thread(target=self._run_websocket, daemon=True)
            self.ws_thread.start()
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._process_data, daemon=True)
            self.processing_thread.start()
            
            self.logger.info("✅ Connected to TradingLite WebSocket")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to TradingLite: {e}")
            return False
    
    def _run_websocket(self):
        """Run WebSocket connection"""
        while self.running:
            try:
                self.ws.run_forever()
            except Exception as e:
                self.logger.error(f"WebSocket error: {e}")
                if self.running:
                    self.logger.info("Reconnecting in 5 seconds...")
                    asyncio.sleep(5)
    
    def _on_open(self, ws):
        """WebSocket opened callback"""
        self.connected = True
        self.logger.info("📡 TradingLite WebSocket connection opened")
        
        # Subscribe to data feeds
        self._subscribe_to_feeds()
    
    def _on_message(self, ws, message):
        """Process incoming WebSocket message"""
        try:
            self.metrics['messages_received'] += 1
            self.metrics['last_update'] = datetime.now()
            
            # Decode binary message (TradingLite uses binary format)
            decoded_data = self._decode_binary_message(message)
            
            if decoded_data:
                # Route to appropriate handler
                if decoded_data.get('type') == 'liquidity':
                    self._handle_liquidity_update(decoded_data)
                elif decoded_data.get('type') == 'orderflow':
                    self._handle_order_flow_update(decoded_data)
                elif decoded_data.get('type') == 'spread':
                    self._handle_spread_update(decoded_data)
                    
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            self.metrics['errors'] += 1
    
    def _on_error(self, ws, error):
        """WebSocket error callback"""
        self.logger.error(f"WebSocket error: {error}")
        self.metrics['errors'] += 1
    
    def _on_close(self, ws):
        """WebSocket closed callback"""
        self.connected = False
        self.logger.info("TradingLite WebSocket connection closed")
    
    def _decode_binary_message(self, message) -> Optional[Dict]:
        """Decode TradingLite binary message format"""
        try:
            # TradingLite uses custom binary encoding
            # This is simplified - actual implementation would need reverse engineering
            if isinstance(message, bytes):
                # Try to decode as JSON first
                try:
                    return json.loads(message.decode('utf-8'))
                except:
                    # Binary format decoding
                    # Format: [type:1byte][timestamp:8bytes][data:remaining]
                    msg_type = message[0]
                    timestamp = struct.unpack('>Q', message[1:9])[0]
                    data = message[9:]
                    
                    return {
                        'type': self._get_message_type(msg_type),
                        'timestamp': timestamp,
                        'data': data
                    }
            return None
            
        except Exception as e:
            self.logger.debug(f"Failed to decode message: {e}")
            return None
    
    def _get_message_type(self, type_byte: int) -> str:
        """Map byte to message type"""
        type_map = {
            0x01: 'liquidity',
            0x02: 'orderflow',
            0x03: 'spread',
            0x04: 'trade',
            0x05: 'indicator'
        }
        return type_map.get(type_byte, 'unknown')
    
    def _subscribe_to_feeds(self):
        """Subscribe to TradingLite data feeds"""
        # Subscribe to liquidity heatmap
        if self.config.subscription_level in ['gold', 'platinum']:
            self._send_subscription({
                'type': 'subscribe',
                'channels': [
                    'liquidity_heatmap',
                    'order_flow',
                    'bid_ask_spread',
                    'cumulative_delta'
                ]
            })
    
    def _send_subscription(self, subscription_data: Dict):
        """Send subscription request"""
        if self.ws and self.connected:
            self.ws.send(json.dumps(subscription_data))
    
    def _handle_liquidity_update(self, data: Dict):
        """Process liquidity heatmap update"""
        try:
            liquidity = LiquidityData(
                timestamp=datetime.fromtimestamp(data['timestamp'] / 1000),
                price_level=data.get('price', 0),
                bid_liquidity=data.get('bid_size', 0),
                ask_liquidity=data.get('ask_size', 0),
                cumulative_bid=data.get('cum_bid', 0),
                cumulative_ask=data.get('cum_ask', 0),
                liquidity_score=self._calculate_liquidity_score(data),
                is_significant=data.get('bid_size', 0) + data.get('ask_size', 0) > 100000
            )
            
            self.liquidity_data.append(liquidity)
            self.metrics['liquidity_updates'] += 1
            
            # Trigger callback
            if self.on_liquidity_update:
                self.on_liquidity_update(liquidity)
                
        except Exception as e:
            self.logger.error(f"Error handling liquidity update: {e}")
    
    def _handle_order_flow_update(self, data: Dict):
        """Process order flow update"""
        try:
            buy_vol = data.get('buy_volume', 0)
            sell_vol = data.get('sell_volume', 0)
            total_vol = buy_vol + sell_vol
            
            order_flow = OrderFlowData(
                timestamp=datetime.fromtimestamp(data['timestamp'] / 1000),
                buy_volume=buy_vol,
                sell_volume=sell_vol,
                delta=buy_vol - sell_vol,
                cumulative_delta=data.get('cum_delta', 0),
                buy_pressure=(buy_vol / total_vol * 100) if total_vol > 0 else 50,
                sell_pressure=(sell_vol / total_vol * 100) if total_vol > 0 else 50,
                flow_direction=self._determine_flow_direction(buy_vol, sell_vol)
            )
            
            self.order_flow_data.append(order_flow)
            self.metrics['order_flow_updates'] += 1
            
            # Trigger callback
            if self.on_order_flow_update:
                self.on_order_flow_update(order_flow)
                
        except Exception as e:
            self.logger.error(f"Error handling order flow update: {e}")
    
    def _handle_spread_update(self, data: Dict):
        """Process bid/ask spread update"""
        try:
            spread_data = {
                'timestamp': datetime.fromtimestamp(data['timestamp'] / 1000),
                'bid': data.get('bid', 0),
                'ask': data.get('ask', 0),
                'spread': data.get('ask', 0) - data.get('bid', 0),
                'spread_percent': ((data.get('ask', 0) - data.get('bid', 0)) / data.get('bid', 1)) * 100
            }
            
            self.bid_ask_spreads.append(spread_data)
            
        except Exception as e:
            self.logger.error(f"Error handling spread update: {e}")
    
    def _calculate_liquidity_score(self, data: Dict) -> float:
        """Calculate liquidity score (0-100)"""
        bid_size = data.get('bid_size', 0)
        ask_size = data.get('ask_size', 0)
        
        # Simple scoring based on size
        total_liquidity = bid_size + ask_size
        
        if total_liquidity > 1000000:
            return 100
        elif total_liquidity > 500000:
            return 80
        elif total_liquidity > 100000:
            return 60
        elif total_liquidity > 50000:
            return 40
        elif total_liquidity > 10000:
            return 20
        else:
            return 10
    
    def _determine_flow_direction(self, buy_vol: float, sell_vol: float) -> str:
        """Determine order flow direction"""
        if buy_vol > sell_vol * 1.2:
            return 'bullish'
        elif sell_vol > buy_vol * 1.2:
            return 'bearish'
        else:
            return 'neutral'
    
    def _process_data(self):
        """Background processing of collected data"""
        while self.running:
            try:
                # Process and analyze collected data
                self._analyze_liquidity_patterns()
                self._analyze_order_flow_patterns()
                
                # Sleep for processing interval
                asyncio.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Processing error: {e}")
    
    def _analyze_liquidity_patterns(self):
        """Analyze liquidity patterns for trading signals"""
        if len(self.liquidity_data) < 10:
            return
        
        recent_liquidity = list(self.liquidity_data)[-10:]
        
        # Check for liquidity walls
        high_liquidity_levels = [l for l in recent_liquidity if l.liquidity_score > 70]
        if high_liquidity_levels:
            self.logger.info(f"🧱 Liquidity wall detected at {high_liquidity_levels[0].price_level}")
    
    def _analyze_order_flow_patterns(self):
        """Analyze order flow for trading signals"""
        if len(self.order_flow_data) < 10:
            return
        
        recent_flow = list(self.order_flow_data)[-10:]
        
        # Check for persistent buy/sell pressure
        bullish_count = sum(1 for f in recent_flow if f.flow_direction == 'bullish')
        bearish_count = sum(1 for f in recent_flow if f.flow_direction == 'bearish')
        
        if bullish_count > 7:
            self.logger.info("📈 Strong bullish order flow detected")
        elif bearish_count > 7:
            self.logger.info("📉 Strong bearish order flow detected")
    
    def get_liquidity_analysis(self) -> Dict[str, Any]:
        """Get comprehensive liquidity analysis"""
        if not self.liquidity_data:
            return {'status': 'no_data'}
        
        recent_data = list(self.liquidity_data)[-100:]
        
        return {
            'status': 'success',
            'liquidity_score': sum(l.liquidity_score for l in recent_data) / len(recent_data),
            'significant_levels': [l.price_level for l in recent_data if l.is_significant],
            'bid_dominance': sum(l.bid_liquidity for l in recent_data) > sum(l.ask_liquidity for l in recent_data),
            'liquidity_walls': self._identify_liquidity_walls(recent_data),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_order_flow_analysis(self) -> Dict[str, Any]:
        """Get comprehensive order flow analysis"""
        if not self.order_flow_data:
            return {'status': 'no_data'}
        
        recent_data = list(self.order_flow_data)[-100:]
        
        total_buy = sum(f.buy_volume for f in recent_data)
        total_sell = sum(f.sell_volume for f in recent_data)
        cumulative_delta = recent_data[-1].cumulative_delta if recent_data else 0
        
        return {
            'status': 'success',
            'total_buy_volume': total_buy,
            'total_sell_volume': total_sell,
            'cumulative_delta': cumulative_delta,
            'buy_pressure_percent': (total_buy / (total_buy + total_sell) * 100) if (total_buy + total_sell) > 0 else 50,
            'flow_direction': self._determine_flow_direction(total_buy, total_sell),
            'trend_strength': abs(cumulative_delta) / max(total_buy + total_sell, 1),
            'timestamp': datetime.now().isoformat()
        }
    
    def _identify_liquidity_walls(self, liquidity_data: List[LiquidityData]) -> List[Dict]:
        """Identify significant liquidity walls"""
        walls = []
        
        for data in liquidity_data:
            if data.liquidity_score > 80:
                walls.append({
                    'price': data.price_level,
                    'type': 'bid' if data.bid_liquidity > data.ask_liquidity else 'ask',
                    'strength': data.liquidity_score,
                    'size': data.bid_liquidity + data.ask_liquidity
                })
        
        return sorted(walls, key=lambda x: x['strength'], reverse=True)[:5]
    
    def get_trading_signals(self) -> Dict[str, Any]:
        """Generate trading signals based on TradingLite data"""
        liquidity = self.get_liquidity_analysis()
        order_flow = self.get_order_flow_analysis()
        
        signals = {
            'timestamp': datetime.now().isoformat(),
            'signals': []
        }
        
        # Liquidity-based signals
        if liquidity.get('status') == 'success':
            if liquidity.get('bid_dominance') and liquidity.get('liquidity_score', 0) > 70:
                signals['signals'].append({
                    'type': 'liquidity',
                    'signal': 'BUY',
                    'strength': 'strong',
                    'reason': 'Strong bid liquidity dominance'
                })
        
        # Order flow-based signals
        if order_flow.get('status') == 'success':
            if order_flow.get('flow_direction') == 'bullish' and order_flow.get('buy_pressure_percent', 0) > 65:
                signals['signals'].append({
                    'type': 'order_flow',
                    'signal': 'BUY',
                    'strength': 'medium',
                    'reason': f"Bullish order flow ({order_flow['buy_pressure_percent']:.1f}% buy pressure)"
                })
            elif order_flow.get('flow_direction') == 'bearish' and order_flow.get('buy_pressure_percent', 0) < 35:
                signals['signals'].append({
                    'type': 'order_flow',
                    'signal': 'SELL',
                    'strength': 'medium',
                    'reason': f"Bearish order flow ({100 - order_flow['buy_pressure_percent']:.1f}% sell pressure)"
                })
        
        return signals
    
    def disconnect(self):
        """Disconnect from TradingLite"""
        self.running = False
        if self.ws:
            self.ws.close()
        self.logger.info("Disconnected from TradingLite")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get integration metrics"""
        return {
            **self.metrics,
            'connected': self.connected,
            'liquidity_data_points': len(self.liquidity_data),
            'order_flow_data_points': len(self.order_flow_data),
            'spread_data_points': len(self.bid_ask_spreads)
        }

# LitScript Generator for custom indicators
class LitScriptGenerator:
    """Generate LitScript code for TradingLite custom indicators"""
    
    @staticmethod
    def generate_smc_indicator() -> str:
        """Generate SMC (Smart Money Concepts) indicator in LitScript"""
        return """
//@version=1
study("SMC Analysis - Order Blocks & FVG", overlay=true)

// Inputs
var ob_lookback = input("Order Block Lookback", 50)
var fvg_threshold = input("FVG Threshold %", 0.1)
var show_zones = input("Show Zones", true)

// Order Block Detection
var ob_high = highest(high, ob_lookback)
var ob_low = lowest(low, ob_lookback)

// Bullish Order Block
if (low == ob_low && close > open) {
    rect(bar_index - ob_lookback, ob_low, bar_index, ob_high, color.green, 20)
    label(bar_index, ob_low, "Bullish OB", color.green)
}

// Bearish Order Block
if (high == ob_high && close < open) {
    rect(bar_index - ob_lookback, ob_low, bar_index, ob_high, color.red, 20)
    label(bar_index, ob_high, "Bearish OB", color.red)
}

// Fair Value Gap Detection
var gap_size = (high[1] - low[1]) * fvg_threshold / 100

// Bullish FVG
if (low > high[2] + gap_size) {
    rect(bar_index - 2, high[2], bar_index, low, color.lime, 30)
    label(bar_index - 1, (high[2] + low) / 2, "FVG", color.lime)
}

// Bearish FVG
if (high < low[2] - gap_size) {
    rect(bar_index - 2, high, bar_index, low[2], color.orange, 30)
    label(bar_index - 1, (high + low[2]) / 2, "FVG", color.orange)
}
"""
    
    @staticmethod
    def generate_liquidity_heatmap() -> str:
        """Generate liquidity heatmap indicator"""
        return """
//@version=1
study("Liquidity Heatmap Analysis", overlay=false)

// Liquidity data
var threshold = input("Alert Threshold", 100000)
var smoothing = input("Smoothing Period", 5)

// Get bid/ask data
var cum_bid = bid_sum()
var cum_ask = ask_sum()
var total_liquidity = cum_bid + cum_ask

// Calculate liquidity score
var liq_score = total_liquidity / 1000000 * 100
liq_score = min(liq_score, 100)

// Smooth the score
var smooth_score = sma(liq_score, smoothing)

// Plot liquidity levels
plot(smooth_score, color=gradient(smooth_score, 0, 100, color.red, color.green))
plot(50, color=color.gray, style=plot.style_dashed)

// Alert conditions
if (total_liquidity > threshold) {
    label(bar_index, smooth_score, "High Liquidity", color.green)
}

// Delta calculation
var delta = cum_bid - cum_ask
plot(delta / 1000, color=color.blue, title="Delta (K)")
"""
    
    @staticmethod  
    def generate_order_flow_indicator() -> str:
        """Generate order flow indicator"""
        return """
//@version=1
study("Order Flow Analysis", overlay=false, scale=scale.right)

// Settings
var delta_period = input("Delta Period", 20)
var show_cumulative = input("Show Cumulative", true)

// Calculate order flow
var buy_vol = volume * (close > open ? 1 : 0)
var sell_vol = volume * (close < open ? 1 : 0)
var delta = buy_vol - sell_vol

// Cumulative delta
seq cum_delta = 0
cum_delta = cum_delta[1] + delta

// Plot delta
plot(delta, color=delta > 0 ? color.green : color.red, style=plot.style_histogram)

// Plot cumulative if enabled
if (show_cumulative) {
    plot(cum_delta, color=color.blue, linewidth=2)
}

// Moving average of delta
var ma_delta = sma(delta, delta_period)
plot(ma_delta, color=color.yellow)

// Divergence detection
if (close > close[1] && delta < delta[1]) {
    label(bar_index, delta, "Bear Div", color.red)
}
if (close < close[1] && delta > delta[1]) {
    label(bar_index, delta, "Bull Div", color.green)
}
"""

# Singleton instance
_tradinglite_integration = None

def get_tradinglite_integration(config: Optional[TradingLiteConfig] = None) -> TradingLiteIntegration:
    """Get singleton instance of TradingLite integration"""
    global _tradinglite_integration
    
    if _tradinglite_integration is None:
        if config is None:
            # Default config - user needs to provide actual credentials
            config = TradingLiteConfig(
                account_token="YOUR_TRADINGLITE_TOKEN",
                workspace_id="YOUR_WORKSPACE_ID",
                subscription_level="gold"
            )
        _tradinglite_integration = TradingLiteIntegration(config)
    
    return _tradinglite_integration