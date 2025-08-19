#!/usr/bin/env python3
"""
System Health Monitor untuk GPTs API
Monitoring endpoint health dengan alerting ke Telegram
"""

import requests
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from threading import Thread
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitor kesehatan endpoint dan kirim alert jika ada masalah"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.health_log_file = "health.log"
        self.failure_counts = {}  # Track consecutive failures
        self.max_failures = 3    # Alert threshold
        self.check_interval = 300  # 5 minutes
        self.is_monitoring = False
        
        # Critical endpoints to monitor
        self.endpoints = {
            "gpts_signal": "/api/gpts/signal?symbol=BTCUSDT",
            "gpts_sinyal_tajam": "/api/gpts/sinyal/tajam",
            "gpts_chart": "/api/gpts/chart?symbol=BTCUSDT", 
            "gpts_status": "/api/gpts/status",
            "telegram_status": "/api/telegram/status" if self._check_telegram_routes() else None
        }
        
        # Remove None endpoints
        self.endpoints = {k: v for k, v in self.endpoints.items() if v is not None}
        
        logger.info(f"🔍 Health Monitor initialized with {len(self.endpoints)} endpoints")
    
    def _check_telegram_routes(self) -> bool:
        """Check if telegram routes are available"""
        try:
            response = requests.get(f"{self.base_url}/api/telegram/status", timeout=5)
            return response.status_code in [200, 404]  # 404 is OK, means route exists
        except:
            return False
    
    def check_endpoint_health(self, name: str, url: str) -> Dict:
        """Check health of single endpoint"""
        start_time = time.time()
        
        try:
            full_url = f"{self.base_url}{url}"
            
            # Different methods for different endpoints
            if "sinyal/tajam" in url:
                response = requests.post(full_url, 
                    json={"symbol": "BTCUSDT", "timeframe": "1H"}, 
                    timeout=10)
            else:
                response = requests.get(full_url, timeout=10)
            
            response_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            health_data = {
                "endpoint": name,
                "url": url,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "healthy": response.status_code == 200,
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
            
            # Reset failure count on success
            if response.status_code == 200:
                self.failure_counts[name] = 0
            else:
                self.failure_counts[name] = self.failure_counts.get(name, 0) + 1
                health_data["error"] = f"HTTP {response.status_code}"
            
            return health_data
            
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            self.failure_counts[name] = self.failure_counts.get(name, 0) + 1
            
            return {
                "endpoint": name,
                "url": url,
                "status_code": 0,
                "response_time_ms": response_time,
                "healthy": False,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def log_health_check(self, health_data: Dict):
        """Log health check results to file"""
        try:
            log_entry = {
                "timestamp": health_data["timestamp"],
                "endpoint": health_data["endpoint"],
                "healthy": health_data["healthy"],
                "response_time": health_data["response_time_ms"],
                "status_code": health_data["status_code"],
                "error": health_data.get("error")
            }
            
            # Append to health log file
            with open(self.health_log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
            # Also log to console
            status = "✅ HEALTHY" if health_data["healthy"] else "❌ UNHEALTHY"
            logger.info(f"{status} {health_data['endpoint']}: {health_data['response_time_ms']}ms")
            
        except Exception as e:
            logger.error(f"Failed to log health check: {e}")
    
    def send_telegram_alert(self, failed_endpoint: str, failure_count: int):
        """Send Telegram alert for endpoint failures"""
        try:
            # Import here to avoid circular imports
            from core.telegram_notifier import TelegramNotifier
            
            telegram = TelegramNotifier()
            
            alert_message = f"""
🚨 <b>SISTEM ALERT - ENDPOINT FAILURE</b>

❌ <b>Endpoint:</b> {failed_endpoint}
📊 <b>Consecutive Failures:</b> {failure_count}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🔧 <b>Action Required:</b>
System requires immediate attention to restore service.

📱 <i>RZC GPTs Health Monitor</i>
"""
            
            # Send to hardcoded admin chat ID
            admin_chat_id = "5899681906"  # Your chat ID
            success = telegram.send_message(admin_chat_id, alert_message)
            
            if success:
                logger.info(f"📱 Alert sent to Telegram for {failed_endpoint}")
            else:
                logger.error(f"Failed to send Telegram alert for {failed_endpoint}")
                
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
    
    def run_health_check(self):
        """Run complete health check on all endpoints"""
        logger.info("🔍 Starting health check cycle...")
        
        results = []
        
        for name, url in self.endpoints.items():
            health_data = self.check_endpoint_health(name, url)
            self.log_health_check(health_data)
            results.append(health_data)
            
            # Check if we need to send alert
            failure_count = self.failure_counts.get(name, 0)
            if failure_count >= self.max_failures:
                logger.warning(f"🚨 {name} failed {failure_count} times consecutively")
                self.send_telegram_alert(name, failure_count)
                # Reset counter after alert to avoid spam
                self.failure_counts[name] = 0
        
        # Summary log
        healthy_count = sum(1 for r in results if r["healthy"])
        total_count = len(results)
        logger.info(f"📊 Health check complete: {healthy_count}/{total_count} endpoints healthy")
        
        return results
    
    def start_monitoring(self):
        """Start continuous monitoring in background thread"""
        if self.is_monitoring:
            logger.warning("Health monitoring already running")
            return
        
        self.is_monitoring = True
        
        def monitor_loop():
            logger.info(f"🚀 Health monitoring started (interval: {self.check_interval}s)")
            
            while self.is_monitoring:
                try:
                    self.run_health_check()
                    time.sleep(self.check_interval)
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        # Start monitoring thread
        monitor_thread = Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        logger.info("✅ Health monitoring thread started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_monitoring = False
        logger.info("🛑 Health monitoring stopped")
    
    def get_health_summary(self) -> Dict:
        """Get current health summary"""
        results = self.run_health_check()
        
        healthy_endpoints = [r for r in results if r["healthy"]]
        unhealthy_endpoints = [r for r in results if not r["healthy"]]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_endpoints": len(results),
            "healthy_count": len(healthy_endpoints),
            "unhealthy_count": len(unhealthy_endpoints),
            "overall_health": len(healthy_endpoints) / len(results) * 100,
            "endpoints": results,
            "monitoring_active": self.is_monitoring
        }

# Global health monitor instance
health_monitor = None

def initialize_health_monitor():
    """Initialize global health monitor"""
    global health_monitor
    if health_monitor is None:
        health_monitor = HealthMonitor()
        # Start monitoring in background
        health_monitor.start_monitoring()
    return health_monitor

def get_health_monitor():
    """Get health monitor instance"""
    return health_monitor or initialize_health_monitor()