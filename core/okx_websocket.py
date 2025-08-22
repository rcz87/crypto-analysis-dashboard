"""
OKX WebSocket Real-time Data Stream
Implementation berdasarkan OKX WebSocket API v5
"""

import asyncio
import json
import logging
import time
import threading
from typing import Dict, Any, Callable, Optional, List

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

logger = logging.getLogger(__name__)

class OKXWebSocketClient:
    """
    OKX WebSocket client untuk real-time market data
    Menggunakan public channel tanpa perlu authentication
    """
    
    def __init__(self):
        self.url = "wss://ws.okx.com:8443/ws/v5/public"
        self.websocket = None
        self.is_connected = False
        self.callbacks = {}
        self.subscribed_channels = set()
        self.last_prices = {}
        self.reconnect_delay = 5
        self.max_reconnect_attempts = 10
        self.reconnect_count = 0
        
    async def connect(self):
        """Establish WebSocket connection"""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("❌ websockets package not available")
            return False
            
        try:
            self.websocket = await websockets.connect(
                self.url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            self.is_connected = True
            self.reconnect_count = 0
            logger.info(f"✅ OKX WebSocket connected: {self.url}")
            
            # Start listening for messages
            loop = asyncio.get_event_loop()
            loop.create_task(self._listen())
            
            return True
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            self.is_connected = False
            await self._reconnect()
            return False
    
    async def disconnect(self):
        """Close WebSocket connection"""
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()
            logger.info("🔌 OKX WebSocket disconnected")
    
    async def subscribe_ticker(self, symbols: List[str]):
        """
        Subscribe to ticker data for multiple symbols
        Format: ["BTC-USDT", "ETH-USDT", "SOL-USDT"]
        """
        if not self.is_connected:
            await self.connect()
        
        # Format subscription message
        args = []
        for symbol in symbols:
            args.append({
                "channel": "tickers",
                "instId": symbol
            })
        
        message = {
            "op": "subscribe",
            "args": args
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            
            # Track subscriptions
            for symbol in symbols:
                channel_key = f"tickers:{symbol}"
                self.subscribed_channels.add(channel_key)
            
            logger.info(f"📡 Subscribed to tickers: {symbols}")
            
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to tickers: {e}")
    
    async def subscribe_orderbook(self, symbols: List[str], depth: str = "5"):
        """
        Subscribe to order book data
        depth: "1", "5", "10", "15", "20", "50", "100", "200", "400"
        """
        if not self.is_connected:
            await self.connect()
        
        args = []
        for symbol in symbols:
            args.append({
                "channel": f"books{depth}",
                "instId": symbol
            })
        
        message = {
            "op": "subscribe",
            "args": args
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            
            for symbol in symbols:
                channel_key = f"books{depth}:{symbol}"
                self.subscribed_channels.add(channel_key)
            
            logger.info(f"📖 Subscribed to orderbook depth {depth}: {symbols}")
            
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to orderbook: {e}")
    
    def register_callback(self, channel: str, symbol: str, callback: Callable):
        """Register callback for specific channel and symbol"""
        key = f"{channel}:{symbol}"
        if key not in self.callbacks:
            self.callbacks[key] = []
        self.callbacks[key].append(callback)
    
    async def _listen(self):
        """Listen for incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"🔥 Invalid JSON received: {e}")
                except Exception as e:
                    logger.error(f"❌ Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("🔌 WebSocket connection closed")
            self.is_connected = False
            await self._reconnect()
        except Exception as e:
            logger.error(f"❌ Error in WebSocket listener: {e}")
            self.is_connected = False
            await self._reconnect()
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        
        # Handle subscription confirmation
        if data.get("event") == "subscribe":
            if data.get("code") == "0":
                logger.info(f"✅ Subscription confirmed: {data.get('arg', {})}")
            else:
                logger.error(f"❌ Subscription failed: {data}")
            return
        
        # Handle ping/pong
        if data.get("event") == "pong":
            return
        
        # Handle error messages
        if data.get("event") == "error":
            logger.error(f"❌ WebSocket error: {data}")
            return
        
        # Handle data messages
        if "data" in data and "arg" in data:
            channel = data["arg"]["channel"]
            inst_id = data["arg"]["instId"]
            
            # Process ticker data
            if channel == "tickers":
                await self._handle_ticker_data(inst_id, data["data"])
            
            # Process orderbook data
            elif channel.startswith("books"):
                await self._handle_orderbook_data(inst_id, data["data"])
    
    async def _handle_ticker_data(self, symbol: str, ticker_list: List[Dict]):
        """Handle ticker data updates"""
        for ticker in ticker_list:
            try:
                # Parse ticker data
                current_price = float(ticker["last"])
                open_24h = float(ticker.get("open24h", current_price))
                high_24h = float(ticker.get("high24h", current_price))
                low_24h = float(ticker.get("low24h", current_price))
                volume_24h = float(ticker.get("vol24h", 0))
                
                # Calculate price change
                price_change_24h = 0.0
                if open_24h > 0:
                    price_change_24h = ((current_price - open_24h) / open_24h) * 100
                
                # Store last price
                last_price = self.last_prices.get(symbol, current_price)
                price_change_instant = 0.0
                if last_price > 0:
                    price_change_instant = ((current_price - last_price) / last_price) * 100
                
                self.last_prices[symbol] = current_price
                
                # Create standardized ticker data
                ticker_data = {
                    "symbol": symbol,
                    "last": current_price,
                    "open24h": open_24h,
                    "high24h": high_24h,
                    "low24h": low_24h,
                    "vol24h": volume_24h,
                    "change_24h": round(price_change_24h, 2),
                    "change_instant": round(price_change_instant, 4),
                    "timestamp": int(ticker["ts"]),
                    "raw": ticker
                }
                
                # Call registered callbacks
                callback_key = f"tickers:{symbol}"
                if callback_key in self.callbacks:
                    for callback in self.callbacks[callback_key]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(ticker_data)
                            else:
                                callback(ticker_data)
                        except Exception as e:
                            logger.error(f"❌ Callback error for {symbol}: {e}")
                
                # Log significant price movements
                if abs(price_change_instant) > 0.1:  # 0.1% instant change
                    logger.info(f"📈 {symbol}: ${current_price:,.2f} ({price_change_instant:+.2f}%)")
                
            except Exception as e:
                logger.error(f"❌ Error processing ticker data for {symbol}: {e}")
    
    async def _handle_orderbook_data(self, symbol: str, orderbook_list: List[Dict]):
        """Handle orderbook data updates"""
        for orderbook in orderbook_list:
            try:
                # Create standardized orderbook data
                orderbook_data = {
                    "symbol": symbol,
                    "bids": [[float(bid[0]), float(bid[1])] for bid in orderbook.get("bids", [])],
                    "asks": [[float(ask[0]), float(ask[1])] for ask in orderbook.get("asks", [])],
                    "timestamp": int(orderbook["ts"]),
                    "raw": orderbook
                }
                
                # Call registered callbacks
                callback_key = f"books:{symbol}"
                if callback_key in self.callbacks:
                    for callback in self.callbacks[callback_key]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(orderbook_data)
                            else:
                                callback(orderbook_data)
                        except Exception as e:
                            logger.error(f"❌ Orderbook callback error for {symbol}: {e}")
                            
            except Exception as e:
                logger.error(f"❌ Error processing orderbook data for {symbol}: {e}")
    
    async def _reconnect(self):
        """Attempt to reconnect WebSocket"""
        if self.reconnect_count >= self.max_reconnect_attempts:
            logger.error("❌ Max reconnection attempts reached")
            return
        
        self.reconnect_count += 1
        logger.info(f"🔄 Reconnecting... (attempt {self.reconnect_count}/{self.max_reconnect_attempts})")
        
        await asyncio.sleep(self.reconnect_delay)
        
        try:
            await self.connect()
            
            # Re-subscribe to previous channels
            if self.subscribed_channels:
                symbols_by_channel = {}
                for channel_key in self.subscribed_channels:
                    parts = channel_key.split(":")
                    channel = parts[0]
                    symbol = parts[1]
                    
                    if channel not in symbols_by_channel:
                        symbols_by_channel[channel] = []
                    symbols_by_channel[channel].append(symbol)
                
                # Re-subscribe
                for channel, symbols in symbols_by_channel.items():
                    if channel == "tickers":
                        await self.subscribe_ticker(symbols)
                    elif channel.startswith("books"):
                        depth = channel.replace("books", "")
                        await self.subscribe_orderbook(symbols, depth)
                        
        except Exception as e:
            logger.error(f"❌ Reconnection failed: {e}")
            await self._reconnect()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get WebSocket connection status"""
        return {
            "connected": self.is_connected,
            "subscribed_channels": list(self.subscribed_channels),
            "reconnect_count": self.reconnect_count,
            "last_prices": self.last_prices,
            "registered_callbacks": len(self.callbacks)
        }


class OKXWebSocketManager:
    """
    Manager untuk WebSocket client dengan threading support
    """
    
    def __init__(self):
        self.client = OKXWebSocketClient()
        self.loop = None
        self.thread = None
        self.is_running = False
        
    def start(self, symbols: List[str] = None):
        """Start WebSocket client in background thread"""
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("❌ WebSocket not available - websockets package missing")
            return False
            
        if self.is_running:
            logger.warning("WebSocket already running")
            return True
        
        if symbols is None:
            symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "ADA-USDT", "DOT-USDT"]
        
        try:
            self.is_running = True
            self.thread = threading.Thread(
                target=self._run_websocket,
                args=(symbols,),
                daemon=True
            )
            self.thread.start()
            logger.info(f"🚀 OKX WebSocket manager started for {symbols}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start WebSocket: {e}")
            self.is_running = False
            return False
    
    def stop(self):
        """Stop WebSocket client"""
        self.is_running = False
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
        logger.info("⏹️ OKX WebSocket manager stopped")
    
    def _run_websocket(self, symbols: List[str]):
        """Run WebSocket in asyncio event loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._websocket_main(symbols))
        except Exception as e:
            logger.error(f"❌ WebSocket loop error: {e}")
        finally:
            self.loop.close()
    
    async def _websocket_main(self, symbols: List[str]):
        """Main WebSocket coroutine"""
        await self.client.connect()
        await self.client.subscribe_ticker(symbols)
        
        # Keep the connection alive
        while self.is_running:
            await asyncio.sleep(1)
    
    def register_ticker_callback(self, symbol: str, callback: Callable):
        """Register callback for ticker updates"""
        self.client.register_callback("tickers", symbol, callback)
    
    def get_status(self) -> Dict[str, Any]:
        """Get WebSocket status"""
        try:
            return {
                "manager_running": self.is_running,
                "thread_alive": self.thread.is_alive() if self.thread else False,
                "client_status": self.client.get_connection_status(),
                "websockets_available": WEBSOCKETS_AVAILABLE
            }
        except Exception as e:
            logger.error(f"Error getting WebSocket status: {e}")
            return {
                "manager_running": False,
                "thread_alive": False,
                "client_status": {
                    "connected": False,
                    "subscribed_channels": [],
                    "reconnect_count": 0,
                    "last_prices": {},
                    "registered_callbacks": 0
                },
                "websockets_available": WEBSOCKETS_AVAILABLE,
                "error": str(e)
            }
    
    def get_last_price(self, symbol: str) -> Optional[float]:
        """Get last known price for symbol"""
        return self.client.last_prices.get(symbol)


# Global WebSocket manager instance
ws_manager = OKXWebSocketManager()