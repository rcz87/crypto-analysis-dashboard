"""
Real-time Market Data Streamer
Enhanced from OkxCandleTracker for live market updates
"""

import time
import threading
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, asdict

import requests
import pandas as pd
from flask_socketio import SocketIO, emit

from core.okx_fetcher import OKXAPIManager
from core.analyzer import TechnicalAnalyzer
from config import Config

@dataclass
class StreamingData:
    """Streaming data structure"""
    symbol: str
    price: float
    change_24h: float
    volume: float
    timestamp: int
    high_24h: float
    low_24h: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RealtimeDataStreamer:
    """Real-time data streaming system"""
    
    def __init__(self, socketio: SocketIO = None):
        self.socketio = socketio
        self.okx_manager = OKXAPIManager()
        self.analyzer = TechnicalAnalyzer()
        self.streaming_threads = {}
        self.is_streaming = False
        self.stream_interval = 30  # seconds
        self.subscribers = {}
        self.last_prices = {}
        
        # Trading pairs to stream
        self.symbols = Config.TRADING_SYMBOLS
        
    def start_streaming(self):
        """Start real-time streaming for all symbols"""
        self.is_streaming = True
        
        for symbol in self.symbols:
            if symbol not in self.streaming_threads:
                thread = threading.Thread(
                    target=self._stream_symbol,
                    args=(symbol,),
                    daemon=True
                )
                thread.start()
                self.streaming_threads[symbol] = thread
                
        print(f"✅ Real-time streaming started for {len(self.symbols)} symbols")
    
    def stop_streaming(self):
        """Stop real-time streaming"""
        self.is_streaming = False
        self.streaming_threads.clear()
        print("❌ Real-time streaming stopped")
    
    def subscribe(self, symbol: str, callback: Callable):
        """Subscribe to real-time updates for a symbol"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        self.subscribers[symbol].append(callback)
    
    def _stream_symbol(self, symbol: str):
        """Stream real-time data for a specific symbol"""
        while self.is_streaming:
            try:
                # Get current ticker data
                ticker_data = self.okx_manager.get_ticker(symbol)
                
                if ticker_data:
                    # Calculate 24h price change percentage correctly
                    current_price = float(ticker_data.get('last', 0))
                    open_24h = float(ticker_data.get('open24h', 0))
                    
                    try:
                        if open_24h > 0:
                            price_change = ((current_price - open_24h) / open_24h) * 100
                        else:
                            price_change = 0.0
                    except (ValueError, TypeError, ZeroDivisionError):
                        price_change = 0.0
                    
                    # Create streaming data object
                    streaming_data = StreamingData(
                        symbol=symbol,
                        price=current_price,
                        change_24h=round(price_change, 2),
                        volume=float(ticker_data.get('volCcy24h', 0)),
                        timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
                        high_24h=float(ticker_data.get('high24h', 0)),
                        low_24h=float(ticker_data.get('low24h', 0))
                    )
                    
                    # Check for significant price changes
                    price_change = self._calculate_price_change(symbol, streaming_data.price)
                    
                    # Emit to WebSocket clients
                    if self.socketio:
                        self.socketio.emit('price_update', {
                            'symbol': symbol,
                            'data': streaming_data.to_dict(),
                            'price_change': price_change,
                            'timestamp': streaming_data.timestamp
                        })
                    
                    # Notify subscribers
                    if symbol in self.subscribers:
                        for callback in self.subscribers[symbol]:
                            callback(streaming_data, price_change)
                    
                    # Store last price for comparison
                    self.last_prices[symbol] = streaming_data.price
                    
                    # If significant change, trigger analysis
                    if abs(price_change) > 0.5:  # 0.5% threshold
                        self._trigger_analysis(symbol, streaming_data)
                
            except Exception as e:
                print(f"❌ Error streaming {symbol}: {e}")
            
            time.sleep(self.stream_interval)
    
    def _calculate_price_change(self, symbol: str, current_price: float) -> float:
        """Calculate percentage price change from last known price"""
        if symbol not in self.last_prices:
            return 0.0
        
        last_price = self.last_prices[symbol]
        if last_price == 0:
            return 0.0
        
        return ((current_price - last_price) / last_price) * 100
    
    def _trigger_analysis(self, symbol: str, streaming_data: StreamingData):
        """Trigger technical analysis on significant price changes"""
        try:
            # Get recent candle data
            df = self.okx_manager.get_candles(symbol, timeframe='1H', limit=100)
            
            if df is not None and not df.empty:
                # Run technical analysis
                analysis = self.analyzer.analyze_comprehensive(df, symbol, '1H')
                
                if analysis.get('signal_detected'):
                    # Emit signal alert
                    if self.socketio:
                        self.socketio.emit('signal_alert', {
                            'symbol': symbol,
                            'signal': analysis,
                            'trigger_price': streaming_data.price,
                            'timestamp': streaming_data.timestamp
                        })
                    
                    print(f"🚨 Signal detected for {symbol} at ${streaming_data.price:,.2f}")
                    
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming statistics"""
        return {
            'is_streaming': self.is_streaming,
            'active_streams': len(self.streaming_threads),
            'symbols': self.symbols,
            'subscribers': {k: len(v) for k, v in self.subscribers.items()},
            'last_prices': self.last_prices,
            'stream_interval': self.stream_interval
        }
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get quick market overview for all symbols"""
        market_data = {}
        
        for symbol in self.symbols:
            try:
                ticker_data = self.okx_manager.get_ticker(symbol)
                if ticker_data:
                    # Calculate 24h price change percentage correctly
                    current_price = float(ticker_data.get('last', 0))
                    open_24h = float(ticker_data.get('open24h', 0))
                    
                    try:
                        if open_24h > 0:
                            price_change = ((current_price - open_24h) / open_24h) * 100
                        else:
                            price_change = 0.0
                    except (ValueError, TypeError, ZeroDivisionError):
                        price_change = 0.0
                    
                    market_data[symbol] = {
                        'price': current_price,
                        'change_24h': round(price_change, 2),
                        'volume': float(ticker_data.get('volCcy24h', 0)),
                        'high_24h': float(ticker_data.get('high24h', 0)),
                        'low_24h': float(ticker_data.get('low24h', 0))
                    }
            except Exception as e:
                print(f"❌ Error getting market data for {symbol}: {e}")
                market_data[symbol] = {
                    'price': 0,
                    'change_24h': 0,
                    'volume': 0,
                    'high_24h': 0,
                    'low_24h': 0
                }
        
        return {
            'success': True,
            'market_data': market_data,
            'timestamp': int(datetime.now(timezone.utc).timestamp() * 1000)
        }
    
    def force_update(self, symbol: str) -> Optional[StreamingData]:
        """Force an immediate update for a symbol"""
        try:
            ticker_data = self.okx_manager.get_ticker(symbol)
            
            if ticker_data:
                streaming_data = StreamingData(
                    symbol=symbol,
                    price=float(ticker_data.get('last', 0)),
                    change_24h=float(ticker_data.get('sodUtc0', 0)),
                    volume=float(ticker_data.get('volCcy24h', 0)),
                    timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),
                    high_24h=float(ticker_data.get('high24h', 0)),
                    low_24h=float(ticker_data.get('low24h', 0))
                )
                
                return streaming_data
                
        except Exception as e:
            print(f"❌ Error forcing update for {symbol}: {e}")
            
        return None

# Global streamer instance
streamer = RealtimeDataStreamer()