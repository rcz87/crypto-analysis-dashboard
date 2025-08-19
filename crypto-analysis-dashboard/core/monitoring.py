"""
Professional Trading AI Monitoring System
Comprehensive monitoring infrastructure for Sentry, Prometheus, and Grafana integration
"""

import os
import time
import psutil
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional

import sentry_sdk
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import request, jsonify, g
from sqlalchemy import text

from app import db
from models import TradingSignal, TradingAnalysis, SystemMetrics

logger = logging.getLogger(__name__)


class TradingMonitor:
    """
    Comprehensive monitoring system for Trading AI Application
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Import metrics from app.py
        from app import (
            trading_signals_total, api_response_time, active_signals, 
            win_rate, analysis_confidence, okx_api_calls, 
            ai_narrative_requests, system_health, database_connections
        )
        
        self.trading_signals_total = trading_signals_total
        self.api_response_time = api_response_time
        self.active_signals = active_signals
        self.win_rate = win_rate
        self.analysis_confidence = analysis_confidence
        self.okx_api_calls = okx_api_calls
        self.ai_narrative_requests = ai_narrative_requests
        self.system_health = system_health
        self.database_connections = database_connections
        
        # Initialize monitoring
        self._initialize_metrics()

    def _initialize_metrics(self):
        """Initialize baseline metrics"""
        try:
            # Set initial system health
            self.system_health.set(100)
            
            # Update active signals count
            self.update_active_signals_count()
            
            # Update win rate metrics
            self.update_win_rate_metrics()
            
            self.logger.info("Monitoring system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize monitoring: {e}")
            sentry_sdk.capture_exception(e)

    def track_trading_signal(self, symbol: str, action: str, confidence: float = 0.0):
        """Track new trading signal generation"""
        try:
            # Increment signal counter
            self.trading_signals_total.labels(symbol=symbol, action=action).inc()
            
            # Record confidence score
            self.analysis_confidence.labels(symbol=symbol).observe(confidence)
            
            # Update active signals
            self.update_active_signals_count()
            
            # Send to Sentry as breadcrumb
            sentry_sdk.add_breadcrumb(
                message=f"Trading signal generated: {symbol} {action}",
                data={
                    'symbol': symbol,
                    'action': action,
                    'confidence': confidence
                },
                level='info',
                category='trading'
            )
            
            self.logger.info(f"Trading signal tracked: {symbol} {action} confidence={confidence}")
            
        except Exception as e:
            self.logger.error(f"Failed to track trading signal: {e}")
            sentry_sdk.capture_exception(e)

    def track_api_call(self, endpoint: str, duration: float, status: str = "success"):
        """Track API call performance"""
        try:
            # Record response time
            self.api_response_time.labels(endpoint=endpoint).observe(duration)
            
            # Track OKX API calls specifically
            if 'okx' in endpoint.lower():
                self.okx_api_calls.labels(endpoint=endpoint, status=status).inc()
            
            # Update system health based on response time
            health_score = self._calculate_health_score(duration)
            self.system_health.set(health_score)
            
            self.logger.debug(f"API call tracked: {endpoint} {duration:.3f}s {status}")
            
        except Exception as e:
            self.logger.error(f"Failed to track API call: {e}")
            sentry_sdk.capture_exception(e)

    def track_ai_narrative(self, model: str, status: str = "success", duration: float = 0.0):
        """Track AI narrative generation"""
        try:
            # Increment AI requests counter
            self.ai_narrative_requests.labels(model=model, status=status).inc()
            
            # Add Sentry breadcrumb
            sentry_sdk.add_breadcrumb(
                message=f"AI narrative request: {model}",
                data={
                    'model': model,
                    'status': status,
                    'duration': duration
                },
                level='info',
                category='ai'
            )
            
            self.logger.info(f"AI narrative tracked: {model} {status} {duration:.3f}s")
            
        except Exception as e:
            self.logger.error(f"Failed to track AI narrative: {e}")
            sentry_sdk.capture_exception(e)

    def update_active_signals_count(self):
        """Update active signals count metrics"""
        try:
            from app import app
            with app.app_context():
                symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'TIA-USDT', 'RENDER-USDT']
                
                for symbol in symbols:
                    # Count active signals for each symbol
                    active_count = db.session.query(TradingSignal).filter(
                        TradingSignal.symbol == symbol,
                        TradingSignal.status == 'active'
                    ).count()
                    
                    self.active_signals.labels(symbol=symbol).set(active_count)
                    
                self.logger.debug("Active signals count updated")
            
        except Exception as e:
            self.logger.error(f"Failed to update active signals count: {e}")
            sentry_sdk.capture_exception(e)

    def update_win_rate_metrics(self):
        """Calculate and update win rate metrics"""
        try:
            from app import app
            with app.app_context():
                symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'TIA-USDT', 'RENDER-USDT']
                
                for symbol in symbols:
                    # Calculate win rate for last 30 days
                    cutoff_date = datetime.now() - timedelta(days=30)
                    
                    total_signals = db.session.query(TradingSignal).filter(
                        TradingSignal.symbol == symbol,
                        TradingSignal.created_at >= cutoff_date,
                        TradingSignal.status.in_(['hit_tp1', 'hit_tp2', 'hit_tp3', 'stopped'])
                    ).count()
                    
                    winning_signals = db.session.query(TradingSignal).filter(
                        TradingSignal.symbol == symbol,
                        TradingSignal.created_at >= cutoff_date,
                        TradingSignal.status.in_(['hit_tp1', 'hit_tp2', 'hit_tp3'])
                    ).count()
                    
                    if total_signals > 0:
                        win_rate_pct = (winning_signals / total_signals) * 100
                        self.win_rate.labels(symbol=symbol).set(win_rate_pct)
                        
                self.logger.debug("Win rate metrics updated")
            
        except Exception as e:
            self.logger.error(f"Failed to update win rate metrics: {e}")
            sentry_sdk.capture_exception(e)

    def update_database_connections(self):
        """Update database connection metrics"""
        try:
            from app import app
            with app.app_context():
                # Get active database connections
                result = db.session.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
                active_connections = result.scalar()
                
                self.database_connections.set(active_connections)
                
                self.logger.debug(f"Database connections updated: {active_connections}")
            
        except Exception as e:
            self.logger.error(f"Failed to update database connections: {e}")
            sentry_sdk.capture_exception(e)

    def _calculate_health_score(self, api_response_time: float) -> float:
        """Calculate system health score based on various factors"""
        try:
            # Base score
            health_score = 100.0
            
            # Deduct points for slow API responses
            if api_response_time > 5.0:
                health_score -= 30
            elif api_response_time > 2.0:
                health_score -= 15
            elif api_response_time > 1.0:
                health_score -= 5
            
            # Check system resources
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            
            # Deduct points for high resource usage
            if cpu_usage > 80:
                health_score -= 20
            elif cpu_usage > 60:
                health_score -= 10
                
            if memory_usage > 80:
                health_score -= 20
            elif memory_usage > 60:
                health_score -= 10
            
            return max(0, min(100, health_score))
            
        except Exception as e:
            self.logger.error(f"Failed to calculate health score: {e}")
            return 50.0  # Default middle score

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            # System resources
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database metrics
            db_result = db.session.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
            db_connections = db_result.scalar()
            
            # Trading metrics
            total_signals = db.session.query(TradingSignal).count()
            active_signals_count = db.session.query(TradingSignal).filter(
                TradingSignal.status == 'active'
            ).count()
            
            # Recent analysis count
            recent_analysis = db.session.query(TradingAnalysis).filter(
                TradingAnalysis.created_at >= datetime.now() - timedelta(hours=24)
            ).count()
            
            return {
                'system': {
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory.percent,
                    'memory_available': memory.available,
                    'disk_usage': disk.percent,
                    'disk_free': disk.free
                },
                'database': {
                    'active_connections': db_connections,
                    'total_signals': total_signals,
                    'active_signals': active_signals_count
                },
                'trading': {
                    'total_signals': total_signals,
                    'active_signals': active_signals_count,
                    'recent_analysis': recent_analysis
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            sentry_sdk.capture_exception(e)
            return {'error': str(e)}

    def send_alert(self, message: str, level: str = "error", extra_data: Optional[Dict] = None):
        """Send alert to monitoring systems"""
        try:
            # Send to Sentry
            with sentry_sdk.push_scope() as scope:
                if extra_data:
                    for key, value in extra_data.items():
                        scope.set_extra(key, value)
                
                scope.set_tag("alert_type", "trading_system")
                scope.set_level(level)
                
                if level == "error":
                    sentry_sdk.capture_message(message, level="error")
                else:
                    sentry_sdk.capture_message(message, level="info")
            
            # Log locally
            if level == "error":
                self.logger.error(f"ALERT: {message}")
            else:
                self.logger.info(f"ALERT: {message}")
                
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")


# Global monitoring instance
monitor = TradingMonitor()


def monitor_api_performance(endpoint_name: str = None):
    """Decorator to monitor API performance"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = endpoint_name or request.endpoint or f.__name__
            
            try:
                # Execute the function
                result = f(*args, **kwargs)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Track the API call
                monitor.track_api_call(endpoint, duration, "success")
                
                return result
                
            except Exception as e:
                # Calculate duration even for errors
                duration = time.time() - start_time
                
                # Track the failed API call
                monitor.track_api_call(endpoint, duration, "error")
                
                # Send alert for API errors
                monitor.send_alert(
                    f"API Error in {endpoint}: {str(e)}",
                    level="error",
                    extra_data={
                        'endpoint': endpoint,
                        'duration': duration,
                        'error': str(e)
                    }
                )
                
                # Re-raise the exception
                raise
                
        return wrapper
    return decorator


def track_trading_signal(symbol: str, action: str, confidence: float = 0.0):
    """Helper function to track trading signals"""
    monitor.track_trading_signal(symbol, action, confidence)


def track_ai_narrative(model: str, status: str = "success", duration: float = 0.0):
    """Helper function to track AI narrative generation"""
    monitor.track_ai_narrative(model, status, duration)