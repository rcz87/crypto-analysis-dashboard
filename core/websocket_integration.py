"""
WebSocket Integration with Flask-SocketIO
Optimized for high-performance real-time data streaming
"""

import os
import json
import time
import logging
import msgpack
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from threading import Thread, Lock
from queue import Queue, Empty
import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS

from core.websocket_data_manager import ws_data_manager
from core.realtime_signal_enhancer import RealtimeSignalEnhancer
from core.okx_websocket_simple import ws_manager_simple

logger = logging.getLogger(__name__)

class OptimizedWebSocketServer:
    """
    High-performance WebSocket server with optimizations:
    - Message batching and throttling
    - Compression enabled
    - Async processing with eventlet
    - Separate worker threads for heavy tasks
    - MessagePack for binary encoding
    """
    
    def __init__(self, app: Flask, cors_origins="*"):
        # Initialize Flask-SocketIO with eventlet async mode
        self.socketio = SocketIO(
            app, 
            cors_allowed_origins=cors_origins,
            async_mode='eventlet',
            ping_timeout=60,
            ping_interval=25,
            compress=True,  # Enable compression
            engineio_logger=False,  # Reduce logging overhead
            logger=False
        )
        
        self.app = app
        CORS(app)
        
        # Message batching configuration
        self.batch_config = {
            'price_update': {
                'interval': 1.0,  # Send price updates every 1 second
                'min_change_percent': 0.1,  # Only send if price changes > 0.1%
                'max_batch_size': 50
            },
            'signal': {
                'interval': 0.5,  # Send signals immediately (0.5s batch)
                'max_batch_size': 10
            },
            'orderbook': {
                'interval': 2.0,  # Orderbook updates every 2 seconds
                'min_imbalance_change': 0.05,  # 5% imbalance change threshold
                'max_batch_size': 20
            }
        }
        
        # Message queues for batching
        self.message_queues = {
            'price_update': Queue(maxsize=1000),
            'signal': Queue(maxsize=100),
            'orderbook': Queue(maxsize=500),
            'metrics': Queue(maxsize=100)
        }
        
        # Worker threads for heavy processing
        self.worker_threads = {}
        self.worker_running = False
        
        # Track last sent values to avoid redundant updates
        self.last_sent_values = {}
        self.value_lock = Lock()
        
        # Connection tracking
        self.active_connections = set()
        self.connection_subscriptions = {}  # sid -> [symbols]
        
        # Performance metrics
        self.metrics = {
            'messages_sent': 0,
            'messages_batched': 0,
            'messages_dropped': 0,
            'bytes_sent': 0,
            'active_connections': 0,
            'processing_time_ms': 0,
            'last_batch_size': 0
        }
        
        # Initialize signal enhancer
        self.signal_enhancer = RealtimeSignalEnhancer(ws_data_manager)
        
        # Register WebSocket event handlers
        self._register_handlers()
        
        # Start worker threads
        self._start_workers()
    
    def _register_handlers(self):
        """Register SocketIO event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            from flask import request
            sid = request.sid
            self.active_connections.add(sid)
            self.connection_subscriptions[sid] = []
            self.metrics['active_connections'] = len(self.active_connections)
            
            logger.info(f"✅ Client connected: {sid} | Total: {self.metrics['active_connections']}")
            
            # Send initial connection acknowledgment
            emit('connected', {
                'status': 'connected',
                'sid': sid,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'compression': 'enabled',
                'batch_intervals': self.batch_config
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            from flask import request
            sid = request.sid
            self.active_connections.discard(sid)
            self.connection_subscriptions.pop(sid, None)
            self.metrics['active_connections'] = len(self.active_connections)
            
            logger.info(f"❌ Client disconnected: {sid} | Remaining: {self.metrics['active_connections']}")
        
        @self.socketio.on('subscribe')
        def handle_subscribe(data):
            """Handle symbol subscription"""
            from flask import request
            sid = request.sid
            symbols = data.get('symbols', [])
            
            if sid in self.connection_subscriptions:
                self.connection_subscriptions[sid].extend(symbols)
                
                # Start WebSocket data feed if not running
                if not ws_manager_simple.is_started:
                    ws_manager_simple.start(symbols)
                
                emit('subscribed', {
                    'symbols': symbols,
                    'status': 'success',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                logger.info(f"📊 Client {sid} subscribed to: {symbols}")
        
        @self.socketio.on('unsubscribe')
        def handle_unsubscribe(data):
            """Handle symbol unsubscription"""
            from flask import request
            sid = request.sid
            symbols = data.get('symbols', [])
            
            if sid in self.connection_subscriptions:
                for symbol in symbols:
                    if symbol in self.connection_subscriptions[sid]:
                        self.connection_subscriptions[sid].remove(symbol)
                
                emit('unsubscribed', {
                    'symbols': symbols,
                    'status': 'success'
                })
        
        @self.socketio.on('request_signal')
        def handle_signal_request(data):
            """Handle signal generation request - async processing"""
            from flask import request
            sid = request.sid
            symbol = data.get('symbol')
            
            # Queue heavy processing
            self.message_queues['signal'].put({
                'type': 'generate',
                'symbol': symbol,
                'sid': sid,
                'timestamp': time.time()
            })
            
            emit('signal_queued', {
                'symbol': symbol,
                'status': 'processing'
            })
    
    def _start_workers(self):
        """Start worker threads for async processing"""
        self.worker_running = True
        
        # Price update batching worker
        self.worker_threads['price_batcher'] = Thread(
            target=self._price_batch_worker,
            daemon=True
        )
        self.worker_threads['price_batcher'].start()
        
        # Signal processing worker
        self.worker_threads['signal_processor'] = Thread(
            target=self._signal_processing_worker,
            daemon=True
        )
        self.worker_threads['signal_processor'].start()
        
        # Metrics collector worker
        self.worker_threads['metrics'] = Thread(
            target=self._metrics_worker,
            daemon=True
        )
        self.worker_threads['metrics'].start()
        
        logger.info("🚀 Started WebSocket worker threads")
    
    def _price_batch_worker(self):
        """Worker thread for batching price updates"""
        batch = []
        last_send_time = time.time()
        config = self.batch_config['price_update']
        
        while self.worker_running:
            try:
                current_time = time.time()
                
                # Collect messages for batching
                while len(batch) < config['max_batch_size']:
                    try:
                        msg = self.message_queues['price_update'].get(timeout=0.1)
                        
                        # Check if change is significant
                        if self._is_significant_change('price', msg):
                            batch.append(msg)
                        else:
                            self.metrics['messages_dropped'] += 1
                            
                    except Empty:
                        break
                
                # Send batch if interval reached or batch is full
                if (current_time - last_send_time >= config['interval'] and batch) or \
                   len(batch) >= config['max_batch_size']:
                    
                    # Compress with MessagePack for binary encoding
                    compressed_batch = msgpack.packb(batch)
                    
                    # Emit to all connected clients
                    self.socketio.emit('price_batch', compressed_batch, 
                                      namespace='/', 
                                      binary=True)  # Send as binary
                    
                    self.metrics['messages_sent'] += len(batch)
                    self.metrics['messages_batched'] += 1
                    self.metrics['bytes_sent'] += len(compressed_batch)
                    self.metrics['last_batch_size'] = len(batch)
                    
                    batch.clear()
                    last_send_time = current_time
                
                # Small sleep to prevent CPU spinning
                eventlet.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Price batch worker error: {e}")
    
    def _signal_processing_worker(self):
        """Worker thread for heavy signal processing"""
        while self.worker_running:
            try:
                # Get signal request from queue
                request = self.message_queues['signal'].get(timeout=1.0)
                
                if request['type'] == 'generate':
                    start_time = time.time()
                    
                    # Heavy processing in separate thread
                    signal = self._generate_enhanced_signal(request['symbol'])
                    
                    processing_time = (time.time() - start_time) * 1000
                    self.metrics['processing_time_ms'] = processing_time
                    
                    # Send result back to specific client or broadcast
                    if 'sid' in request:
                        self.socketio.emit('signal_generated', signal, 
                                         room=request['sid'],
                                         namespace='/')
                    else:
                        self.socketio.emit('signal_broadcast', signal,
                                         namespace='/')
                    
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Signal processing worker error: {e}")
    
    def _metrics_worker(self):
        """Worker thread for metrics collection"""
        while self.worker_running:
            try:
                # Collect and emit metrics every 10 seconds
                eventlet.sleep(10)
                
                metrics_data = {
                    **self.metrics,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'ws_data_manager_metrics': ws_data_manager.get_metrics()
                }
                
                # Emit metrics to monitoring namespace
                self.socketio.emit('metrics_update', metrics_data,
                                 namespace='/')
                
                # Log important metrics
                if self.metrics['active_connections'] > 0:
                    logger.info(f"📊 WebSocket Metrics: Connections={self.metrics['active_connections']}, "
                              f"Messages/s={self.metrics['messages_sent']/10:.1f}, "
                              f"Batch Size={self.metrics['last_batch_size']}")
                
                # Reset counters
                self.metrics['messages_sent'] = 0
                self.metrics['messages_batched'] = 0
                
            except Exception as e:
                logger.error(f"Metrics worker error: {e}")
    
    def _is_significant_change(self, data_type: str, message: Dict) -> bool:
        """Check if change is significant enough to send"""
        try:
            with self.value_lock:
                key = f"{data_type}_{message.get('symbol', '')}"
                
                if data_type == 'price':
                    current_price = message.get('price', 0)
                    last_price = self.last_sent_values.get(key, 0)
                    
                    if last_price == 0:
                        self.last_sent_values[key] = current_price
                        return True
                    
                    # Calculate percentage change
                    change_percent = abs((current_price - last_price) / last_price * 100)
                    
                    # Only send if change exceeds threshold
                    if change_percent >= self.batch_config['price_update']['min_change_percent']:
                        self.last_sent_values[key] = current_price
                        return True
                    return False
                
                elif data_type == 'orderbook':
                    current_imbalance = message.get('imbalance_ratio', 0.5)
                    last_imbalance = self.last_sent_values.get(key, 0.5)
                    
                    change = abs(current_imbalance - last_imbalance)
                    
                    if change >= self.batch_config['orderbook']['min_imbalance_change']:
                        self.last_sent_values[key] = current_imbalance
                        return True
                    return False
                
                # Always send signals
                return True
                
        except Exception as e:
            logger.error(f"Error checking significant change: {e}")
            return True
    
    def _generate_enhanced_signal(self, symbol: str) -> Dict[str, Any]:
        """Generate enhanced signal with heavy processing"""
        try:
            # This would normally call your signal generation logic
            # For now, return a mock enhanced signal
            market_data = ws_data_manager.get_market_snapshot(symbol)
            
            # Heavy processing here (AI, ML models, etc.)
            # ... your signal generation logic ...
            
            signal = {
                'symbol': symbol,
                'action': 'BUY',
                'confidence': 85,
                'entry_price': market_data['price_data'].get('price', 0),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Enhance with real-time data
            enhanced = self.signal_enhancer.enhance_signal(signal)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error generating enhanced signal: {e}")
            return {'error': str(e)}
    
    def queue_price_update(self, data: Dict):
        """Queue price update for batching"""
        try:
            if not self.message_queues['price_update'].full():
                self.message_queues['price_update'].put(data)
        except Exception as e:
            logger.error(f"Error queuing price update: {e}")
    
    def broadcast_signal(self, signal: Dict):
        """Broadcast signal to all clients"""
        try:
            # High priority - send immediately
            self.socketio.emit('signal_alert', signal, namespace='/')
            logger.info(f"📢 Broadcast signal: {signal.get('symbol')} - {signal.get('action')}")
        except Exception as e:
            logger.error(f"Error broadcasting signal: {e}")
    
    def stop_workers(self):
        """Stop all worker threads"""
        self.worker_running = False
        for name, thread in self.worker_threads.items():
            if thread.is_alive():
                thread.join(timeout=2)
        logger.info("⏹️ WebSocket workers stopped")

# This will be initialized in app.py
ws_server = None