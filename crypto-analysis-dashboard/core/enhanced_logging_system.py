"""
Enhanced Logging System - Comprehensive Logging untuk Debug & Monitoring
Mengatasi masalah: Replit hosting mati, tidak ada log fallback, debug sulit
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import traceback
import sys

class EnhancedLogger:
    """
    Enhanced logging system dengan multiple outputs dan fallback
    """
    
    def __init__(self):
        self.setup_logging()
        self.log_file = "logs/system_debug.log"
        self.error_log = "logs/error_fallback.log"
        self.ensure_log_directories()
        
    def setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create custom formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Console handler dengan colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # File handler untuk debug
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler('logs/system_debug.log', mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Error file handler
        error_handler = logging.FileHandler('logs/error_fallback.log', mode='a')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Add handlers
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_handler)
        
        print("🔧 Enhanced Logging System initialized")
        
    def ensure_log_directories(self):
        """Ensure log directories exist"""
        os.makedirs('logs', exist_ok=True)
        os.makedirs('logs/endpoints', exist_ok=True)
        os.makedirs('logs/errors', exist_ok=True)
        
    def log_endpoint_call(self, endpoint: str, params: Dict, response_time: float = None):
        """Log endpoint calls dengan detail"""
        timestamp = datetime.now().isoformat()
        
        log_data = {
            'timestamp': timestamp,
            'endpoint': endpoint,
            'parameters': params,
            'response_time_ms': response_time * 1000 if response_time else None,
            'status': 'called'
        }
        
        # Console log
        print(f"🌐 ENDPOINT: {endpoint} | PARAMS: {params} | TIME: {response_time*1000:.1f}ms" if response_time else f"🌐 ENDPOINT: {endpoint} | PARAMS: {params}")
        
        # File log
        logging.info(f"ENDPOINT_CALL: {json.dumps(log_data)}")
        
        # Detailed endpoint log
        endpoint_log_file = f"logs/endpoints/{endpoint.replace('/', '_')}.log"
        try:
            with open(endpoint_log_file, 'a') as f:
                f.write(f"{timestamp} - {json.dumps(log_data)}\n")
        except Exception as e:
            print(f"⚠️ Failed to write endpoint log: {e}")
    
    def log_error_with_context(self, error: Exception, context: Dict = None, endpoint: str = None):
        """Log errors dengan full context dan traceback"""
        timestamp = datetime.now().isoformat()
        
        error_data = {
            'timestamp': timestamp,
            'endpoint': endpoint,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        # Console log dengan warna merah
        print(f"🚨 ERROR in {endpoint}: {type(error).__name__}: {str(error)}")
        print(f"📍 Context: {context}")
        
        # Logging
        logging.error(f"ERROR_WITH_CONTEXT: {json.dumps(error_data, indent=2)}")
        
        # Fallback error file
        error_file = f"logs/errors/{datetime.now().strftime('%Y-%m-%d')}_errors.log"
        try:
            with open(error_file, 'a') as f:
                f.write(f"{timestamp} - {json.dumps(error_data, indent=2)}\n\n")
        except:
            # Ultimate fallback - print to stdout jika file gagal
            print(f"💾 FALLBACK ERROR LOG: {json.dumps(error_data)}")
    
    def log_performance_metrics(self, endpoint: str, metrics: Dict):
        """Log performance metrics"""
        timestamp = datetime.now().isoformat()
        
        perf_data = {
            'timestamp': timestamp,
            'endpoint': endpoint,
            'metrics': metrics
        }
        
        print(f"📊 PERFORMANCE {endpoint}: {metrics}")
        logging.info(f"PERFORMANCE_METRICS: {json.dumps(perf_data)}")
        
        # Performance log file
        try:
            with open('logs/performance.log', 'a') as f:
                f.write(f"{timestamp} - {json.dumps(perf_data)}\n")
        except Exception as e:
            print(f"⚠️ Failed to write performance log: {e}")
    
    def log_system_health(self, status: str, details: Dict = None):
        """Log system health status"""
        timestamp = datetime.now().isoformat()
        
        health_data = {
            'timestamp': timestamp,
            'status': status,
            'details': details or {},
            'memory_usage': self.get_memory_usage(),
            'uptime': self.get_uptime()
        }
        
        print(f"💚 SYSTEM_HEALTH: {status} | {details}")
        logging.info(f"SYSTEM_HEALTH: {json.dumps(health_data)}")
        
        try:
            with open('logs/system_health.log', 'a') as f:
                f.write(f"{timestamp} - {json.dumps(health_data)}\n")
        except Exception as e:
            print(f"⚠️ Failed to write health log: {e}")
    
    def get_memory_usage(self) -> Dict:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            return {
                'memory_percent': process.memory_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024
            }
        except ImportError:
            return {'memory_info': 'psutil not available'}
    
    def get_uptime(self) -> str:
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return f"{uptime_seconds:.0f}s"
        except:
            return "unknown"

def endpoint_logger(endpoint_name: str):
    """Decorator untuk logging endpoint calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            # Get logger instance
            logger = enhanced_logger
            
            # Extract request parameters
            try:
                from flask import request
                params = {
                    'query_params': dict(request.args),
                    'method': request.method,
                    'remote_addr': request.remote_addr
                }
            except:
                params = {'args': args[:2], 'kwargs': list(kwargs.keys())}
            
            # Start timing
            start_time = time.time()
            
            try:
                # Log start
                logger.log_endpoint_call(endpoint_name, params)
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log completion
                end_time = time.time()
                response_time = end_time - start_time
                
                logger.log_endpoint_call(f"{endpoint_name}_completed", params, response_time)
                logger.log_performance_metrics(endpoint_name, {
                    'response_time_ms': response_time * 1000,
                    'status': 'success'
                })
                
                return result
                
            except Exception as e:
                # Log error
                end_time = time.time()
                response_time = end_time - start_time
                
                context = {
                    'parameters': params,
                    'response_time_ms': response_time * 1000,
                    'function': func.__name__
                }
                
                logger.log_error_with_context(e, context, endpoint_name)
                logger.log_performance_metrics(endpoint_name, {
                    'response_time_ms': response_time * 1000,
                    'status': 'error',
                    'error': str(e)
                })
                
                # Re-raise untuk handling normal
                raise
                
        return wrapper
    return decorator

def safe_execute(operation_name: str, fallback_result=None):
    """Decorator untuk safe execution dengan fallback"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                print(f"✅ {operation_name}: SUCCESS")
                return result
            except Exception as e:
                logger = enhanced_logger
                context = {
                    'operation': operation_name,
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                
                logger.log_error_with_context(e, context, operation_name)
                print(f"🔄 {operation_name}: FALLBACK activated due to error")
                
                return fallback_result
        return wrapper
    return decorator

# Global logger instance
enhanced_logger = EnhancedLogger()

# Convenience functions
def log_info(message: str, context: Dict = None):
    """Quick info logging"""
    print(f"ℹ️ {message}")
    logging.info(f"{message} | Context: {context}")

def log_warning(message: str, context: Dict = None):
    """Quick warning logging"""
    print(f"⚠️ {message}")
    logging.warning(f"{message} | Context: {context}")

def log_error(message: str, context: Dict = None):
    """Quick error logging"""
    print(f"🚨 {message}")
    logging.error(f"{message} | Context: {context}")

def log_debug(message: str, context: Dict = None):
    """Quick debug logging"""
    print(f"🔍 {message}")
    logging.debug(f"{message} | Context: {context}")

def log_success(message: str, context: Dict = None):
    """Quick success logging"""
    print(f"✅ {message}")
    logging.info(f"SUCCESS: {message} | Context: {context}")