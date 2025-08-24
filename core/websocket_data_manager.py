"""
WebSocket Data Manager with Full Integration
Handles real-time data distribution to all trading components
Uses Flask-SocketIO with eventlet for async operations
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone
from threading import Lock
import eventlet
eventlet.monkey_patch()

logger = logging.getLogger(__name__)

class WebSocketDataManager:
    """
    Central hub for WebSocket data distribution
    Integrates with Holly Signal Engine, SMC Analysis, AI Reasoning
    """
    
    def __init__(self):
        self.last_prices: Dict[str, Dict[str, Any]] = {}
        self.price_history: Dict[str, List[float]] = {}
        self.volume_data: Dict[str, Dict[str, Any]] = {}
        self.orderbook_data: Dict[str, Dict[str, Any]] = {}
        self.liquidation_data: Dict[str, List[Dict]] = {}
        
        self.data_lock = Lock()
        self.subscribers: Dict[str, List[Callable]] = {
            'price_update': [],
            'volume_spike': [],
            'orderbook_imbalance': [],
            'liquidation_event': [],
            'signal_trigger': []
        }
        
        self.signal_engines = {}
        self.analysis_engines = {}
        self.alert_handlers = []
        
        self.is_running = False
        self.connected_clients = set()
        
        # Performance metrics
        self.metrics = {
            'messages_processed': 0,
            'signals_generated': 0,
            'alerts_triggered': 0,
            'last_update': None
        }
        
        # Price change thresholds for triggering analysis
        self.trigger_thresholds = {
            'price_change_percent': 0.5,  # 0.5% change triggers analysis
            'volume_spike_multiplier': 2.0,  # 2x average volume
            'orderbook_imbalance_ratio': 0.7,  # 70% imbalance
            'liquidation_threshold': 1000000  # $1M liquidations
        }
    
    def register_signal_engine(self, name: str, engine: Any):
        """Register a signal generation engine"""
        self.signal_engines[name] = engine
        logger.info(f"✅ Registered signal engine: {name}")
    
    def register_analysis_engine(self, name: str, engine: Any):
        """Register an analysis engine"""
        self.analysis_engines[name] = engine
        logger.info(f"✅ Registered analysis engine: {name}")
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to specific events"""
        if event_type in self.subscribers:
            self.subscribers[event_type].append(callback)
            logger.info(f"📡 Subscribed to {event_type}")
    
    def process_ticker_update(self, data: Dict[str, Any]):
        """Process ticker update from WebSocket"""
        try:
            with self.data_lock:
                symbol = data.get('instId', '')
                price = float(data.get('last', 0))
                volume = float(data.get('vol24h', 0))
                change_24h = float(data.get('sodUtc0', 0))
                
                # Store previous price for comparison
                prev_price = self.last_prices.get(symbol, {}).get('price', price)
                
                # Update price data
                self.last_prices[symbol] = {
                    'price': price,
                    'prev_price': prev_price,
                    'volume_24h': volume,
                    'change_24h': change_24h,
                    'change_percent': ((price - prev_price) / prev_price * 100) if prev_price else 0,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'updated': time.time()
                }
                
                # Update price history (keep last 100 prices)
                if symbol not in self.price_history:
                    self.price_history[symbol] = []
                self.price_history[symbol].append(price)
                if len(self.price_history[symbol]) > 100:
                    self.price_history[symbol].pop(0)
                
                # Check for significant events
                self._check_price_triggers(symbol, price, prev_price, volume)
                
                # Notify subscribers
                self._notify_subscribers('price_update', {
                    'symbol': symbol,
                    'price': price,
                    'prev_price': prev_price,
                    'volume': volume
                })
                
                self.metrics['messages_processed'] += 1
                self.metrics['last_update'] = datetime.now(timezone.utc).isoformat()
                
        except Exception as e:
            logger.error(f"Error processing ticker update: {e}")
    
    def process_orderbook_update(self, data: Dict[str, Any]):
        """Process orderbook update"""
        try:
            with self.data_lock:
                symbol = data.get('instId', '')
                bids = data.get('bids', [])
                asks = data.get('asks', [])
                
                if bids and asks:
                    bid_volume = sum(float(bid[1]) for bid in bids[:10])
                    ask_volume = sum(float(ask[1]) for ask in asks[:10])
                    
                    imbalance_ratio = bid_volume / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else 0.5
                    
                    self.orderbook_data[symbol] = {
                        'bid_volume': bid_volume,
                        'ask_volume': ask_volume,
                        'imbalance_ratio': imbalance_ratio,
                        'best_bid': float(bids[0][0]) if bids else 0,
                        'best_ask': float(asks[0][0]) if asks else 0,
                        'spread': float(asks[0][0]) - float(bids[0][0]) if bids and asks else 0,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Check for significant imbalance
                    if abs(imbalance_ratio - 0.5) > (self.trigger_thresholds['orderbook_imbalance_ratio'] - 0.5):
                        self._notify_subscribers('orderbook_imbalance', {
                            'symbol': symbol,
                            'imbalance_ratio': imbalance_ratio,
                            'bid_volume': bid_volume,
                            'ask_volume': ask_volume
                        })
                        
        except Exception as e:
            logger.error(f"Error processing orderbook update: {e}")
    
    def process_liquidation_update(self, data: Dict[str, Any]):
        """Process liquidation data"""
        try:
            with self.data_lock:
                symbol = data.get('instId', '')
                liquidation_amount = float(data.get('sz', 0))
                side = data.get('side', '')
                price = float(data.get('px', 0))
                
                if symbol not in self.liquidation_data:
                    self.liquidation_data[symbol] = []
                
                liquidation_event = {
                    'amount_usd': liquidation_amount * price,
                    'side': side,
                    'price': price,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                self.liquidation_data[symbol].append(liquidation_event)
                
                # Keep only last 50 liquidations
                if len(self.liquidation_data[symbol]) > 50:
                    self.liquidation_data[symbol].pop(0)
                
                # Check for significant liquidations
                if liquidation_event['amount_usd'] > self.trigger_thresholds['liquidation_threshold']:
                    self._notify_subscribers('liquidation_event', {
                        'symbol': symbol,
                        'liquidation': liquidation_event
                    })
                    
        except Exception as e:
            logger.error(f"Error processing liquidation update: {e}")
    
    def _check_price_triggers(self, symbol: str, price: float, prev_price: float, volume: float):
        """Check if price movement triggers signal generation"""
        try:
            # Calculate price change percentage
            if prev_price and prev_price != price:
                change_percent = abs((price - prev_price) / prev_price * 100)
                
                # Trigger analysis if significant price change
                if change_percent >= self.trigger_thresholds['price_change_percent']:
                    self._trigger_signal_generation(symbol, 'price_breakout', {
                        'price': price,
                        'prev_price': prev_price,
                        'change_percent': change_percent
                    })
            
            # Check volume spike
            avg_volume = self.volume_data.get(symbol, {}).get('avg_volume', volume)
            if avg_volume and volume > avg_volume * self.trigger_thresholds['volume_spike_multiplier']:
                self._notify_subscribers('volume_spike', {
                    'symbol': symbol,
                    'volume': volume,
                    'avg_volume': avg_volume,
                    'spike_ratio': volume / avg_volume
                })
                
        except Exception as e:
            logger.error(f"Error checking price triggers: {e}")
    
    def _trigger_signal_generation(self, symbol: str, trigger_type: str, data: Dict[str, Any]):
        """Trigger signal generation in registered engines"""
        try:
            # Holly Signal Engine Integration
            if 'holly' in self.signal_engines:
                holly_engine = self.signal_engines['holly']
                # Use real-time data for signal generation
                signal = holly_engine.generate_signal_with_realtime_data(
                    symbol=symbol,
                    current_price=data.get('price'),
                    price_history=self.price_history.get(symbol, []),
                    volume_data=self.volume_data.get(symbol, {}),
                    orderbook_data=self.orderbook_data.get(symbol, {})
                )
                
                if signal and signal.get('confidence', 0) > 70:
                    self._broadcast_signal(signal)
                    self.metrics['signals_generated'] += 1
            
            # SMC Analysis Integration
            if 'smc' in self.analysis_engines:
                smc_engine = self.analysis_engines['smc']
                # Update SMC levels with real-time data
                smc_engine.update_realtime_levels(
                    symbol=symbol,
                    current_price=data.get('price'),
                    orderbook=self.orderbook_data.get(symbol, {})
                )
            
            # AI Reasoning Engine Integration
            if 'ai_reasoning' in self.analysis_engines:
                ai_engine = self.analysis_engines['ai_reasoning']
                # Generate AI reasoning based on real-time events
                reasoning = ai_engine.analyze_realtime_event(
                    symbol=symbol,
                    event_type=trigger_type,
                    event_data=data,
                    market_context={
                        'orderbook': self.orderbook_data.get(symbol, {}),
                        'liquidations': self.liquidation_data.get(symbol, []),
                        'price_history': self.price_history.get(symbol, [])
                    }
                )
                
                if reasoning:
                    logger.info(f"🤖 AI Reasoning: {reasoning}")
            
            # Notify signal trigger subscribers
            self._notify_subscribers('signal_trigger', {
                'symbol': symbol,
                'trigger_type': trigger_type,
                'data': data
            })
            
        except Exception as e:
            logger.error(f"Error triggering signal generation: {e}")
    
    def _broadcast_signal(self, signal: Dict[str, Any]):
        """Broadcast signal to all connected clients"""
        try:
            # Send to all alert handlers
            for handler in self.alert_handlers:
                handler(signal)
            
            # Log signal
            logger.info(f"📢 Broadcasting signal: {signal.get('symbol')} - {signal.get('action')} @ {signal.get('entry_price')}")
            
            self.metrics['alerts_triggered'] += 1
            
        except Exception as e:
            logger.error(f"Error broadcasting signal: {e}")
    
    def _notify_subscribers(self, event_type: str, data: Dict[str, Any]):
        """Notify all subscribers of an event"""
        try:
            if event_type in self.subscribers:
                # Use eventlet to handle callbacks asynchronously
                for callback in self.subscribers[event_type]:
                    eventlet.spawn_n(callback, data)
                    
        except Exception as e:
            logger.error(f"Error notifying subscribers: {e}")
    
    def get_real_time_price(self, symbol: str) -> Optional[float]:
        """Get real-time price for symbol"""
        with self.data_lock:
            data = self.last_prices.get(symbol, {})
            return data.get('price')
    
    def get_market_snapshot(self, symbol: str) -> Dict[str, Any]:
        """Get complete market snapshot for symbol"""
        with self.data_lock:
            return {
                'price_data': self.last_prices.get(symbol, {}),
                'orderbook': self.orderbook_data.get(symbol, {}),
                'recent_liquidations': self.liquidation_data.get(symbol, [])[-10:],
                'price_history': self.price_history.get(symbol, [])[-20:],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            **self.metrics,
            'active_symbols': len(self.last_prices),
            'connected_clients': len(self.connected_clients),
            'registered_engines': {
                'signal_engines': list(self.signal_engines.keys()),
                'analysis_engines': list(self.analysis_engines.keys())
            }
        }
    
    def update_trigger_thresholds(self, thresholds: Dict[str, float]):
        """Update trigger thresholds"""
        self.trigger_thresholds.update(thresholds)
        logger.info(f"📊 Updated trigger thresholds: {thresholds}")
    
    def start(self):
        """Start the data manager"""
        self.is_running = True
        logger.info("🚀 WebSocket Data Manager started with full integration")
    
    def stop(self):
        """Stop the data manager"""
        self.is_running = False
        logger.info("⏹️ WebSocket Data Manager stopped")


# Global instance
ws_data_manager = WebSocketDataManager()