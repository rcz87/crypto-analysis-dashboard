"""
OKX WebSocket Simple Implementation
Compatible dengan Python modern tanpa asyncio issues
"""

import json
import logging
import threading
import time
from typing import Dict, Any, Optional
import websocket
import ssl

logger = logging.getLogger(__name__)

class OKXWebSocketSimple:
    """
    Simple WebSocket client for OKX real-time data
    Using websocket-client library (synchronous)
    """
    
    def __init__(self):
        self.url = "wss://ws.okx.com:8443/ws/v5/public"
        self.ws = None
        self.is_connected = False
        self.last_prices = {}
        self.running = False
        self.thread = None
        self.subscribed_symbols = []
        self.ping_interval = 20
        self.last_ping = time.time()
        
    def connect(self):
        """Establish WebSocket connection"""
        try:
            # Create WebSocket with SSL
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Start WebSocket in thread
            self.running = True
            self.thread = threading.Thread(
                target=self._run_forever,
                daemon=True
            )
            self.thread.start()
            
            # Wait for connection
            time.sleep(2)
            
            if self.is_connected:
                logger.info(f"✅ OKX WebSocket connected successfully")
                return True
            else:
                logger.error("❌ Failed to establish WebSocket connection")
                return False
                
        except Exception as e:
            logger.error(f"❌ WebSocket connection error: {e}")
            return False
    
    def _run_forever(self):
        """Run WebSocket in thread"""
        try:
            self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            logger.error(f"❌ WebSocket runtime error: {e}")
            self.is_connected = False
    
    def on_open(self, ws):
        """Handle connection open"""
        self.is_connected = True
        logger.info("📡 WebSocket connection opened")
        
        # Subscribe to stored symbols
        if self.subscribed_symbols:
            self.subscribe_tickers(self.subscribed_symbols)
    
    def on_message(self, ws, message):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            
            # Handle subscription confirmation
            if data.get("event") == "subscribe":
                if data.get("code") == "0":
                    logger.info(f"✅ Subscription confirmed")
                else:
                    logger.error(f"❌ Subscription failed: {data}")
                return
            
            # Handle ping/pong
            if data.get("op") == "ping":
                self.send_pong()
                return
            
            # Handle ticker data
            if "data" in data and "arg" in data:
                if data["arg"]["channel"] == "tickers":
                    self.handle_ticker_data(data["arg"]["instId"], data["data"])
                    
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
    
    def on_error(self, ws, error):
        """Handle errors"""
        logger.error(f"❌ WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle connection close"""
        self.is_connected = False
        logger.info(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")
        
        # Auto-reconnect if still running
        if self.running:
            time.sleep(5)
            logger.info("🔄 Attempting to reconnect...")
            self.connect()
    
    def subscribe_tickers(self, symbols: list):
        """Subscribe to ticker channels"""
        if not self.is_connected:
            logger.warning("❌ Not connected, storing symbols for later")
            self.subscribed_symbols = symbols
            return False
        
        # Create subscription message
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
            self.ws.send(json.dumps(message))
            self.subscribed_symbols = symbols
            logger.info(f"📊 Subscribed to tickers: {symbols}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to subscribe: {e}")
            return False
    
    def handle_ticker_data(self, symbol: str, ticker_list: list):
        """Process ticker data"""
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
                old_data = self.last_prices.get(symbol, {})
                old_price = old_data.get("price", current_price) if isinstance(old_data, dict) else current_price
                instant_change = ((current_price - old_price) / old_price * 100) if old_price > 0 else 0
                
                self.last_prices[symbol] = {
                    "price": current_price,
                    "change_24h": round(price_change_24h, 2),
                    "change_instant": round(instant_change, 4),
                    "volume_24h": volume_24h,
                    "high_24h": high_24h,
                    "low_24h": low_24h,
                    "timestamp": int(ticker["ts"]),
                    "updated": time.time()
                }
                
                # Log significant movements
                if abs(instant_change) > 0.1:  # 0.1% instant change
                    logger.info(f"⚡ {symbol}: ${current_price:,.2f} ({instant_change:+.3f}% instant, {price_change_24h:+.2f}% 24h)")
                
            except Exception as e:
                logger.error(f"❌ Error processing ticker for {symbol}: {e}")
    
    def send_pong(self):
        """Send pong message to keep connection alive"""
        try:
            pong_msg = json.dumps({"op": "pong"})
            self.ws.send(pong_msg)
            self.last_ping = time.time()
        except Exception as e:
            logger.error(f"❌ Failed to send pong: {e}")
    
    def get_last_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get last known price data for symbol"""
        return self.last_prices.get(symbol)
    
    def disconnect(self):
        """Close WebSocket connection"""
        self.running = False
        if self.ws:
            self.ws.close()
        logger.info("⏹️ WebSocket disconnected")
    
    def get_status(self) -> Dict[str, Any]:
        """Get connection status"""
        return {
            "connected": self.is_connected,
            "running": self.running,
            "subscribed_symbols": self.subscribed_symbols,
            "cached_prices": len(self.last_prices),
            "last_prices": {
                symbol: {
                    "price": data["price"],
                    "change_24h": data["change_24h"],
                    "age_seconds": time.time() - data["updated"]
                }
                for symbol, data in self.last_prices.items()
            }
        }


class OKXWebSocketManager:
    """Manager for simple WebSocket client"""
    
    def __init__(self):
        self.client = OKXWebSocketSimple()
        self.is_started = False
        
    def start(self, symbols: list = None):
        """Start WebSocket with symbols"""
        if self.is_started:
            logger.warning("WebSocket already started")
            return True
        
        if symbols is None:
            symbols = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "ADA-USDT", "DOT-USDT"]
        
        # Connect WebSocket
        if self.client.connect():
            # Subscribe to symbols
            time.sleep(1)  # Wait for connection to stabilize
            if self.client.subscribe_tickers(symbols):
                self.is_started = True
                logger.info(f"🚀 WebSocket manager started with {len(symbols)} symbols")
                return True
            else:
                logger.error("❌ Failed to subscribe to symbols")
                return False
        else:
            logger.error("❌ Failed to connect WebSocket")
            return False
    
    def stop(self):
        """Stop WebSocket"""
        self.client.disconnect()
        self.is_started = False
        logger.info("⏹️ WebSocket manager stopped")
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get last price for symbol"""
        data = self.client.get_last_price(symbol)
        if data:
            return data["price"]
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get WebSocket status"""
        status = self.client.get_status()
        status["manager_started"] = self.is_started
        return status


# Global instance
ws_manager_simple = OKXWebSocketManager()