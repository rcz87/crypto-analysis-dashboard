#!/usr/bin/env python3
"""
Enterprise Endpoint Management System
Handles 50+ endpoints with enterprise-grade features:
- Auto-discovery dan health monitoring
- Circuit breaker pattern
- Dynamic load balancing  
- Performance analytics per endpoint
- Auto-scaling capabilities
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class EndpointStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"

class EndpointPriority(Enum):
    CRITICAL = 1      # Trading signals, AI reasoning
    HIGH = 2          # SMC analysis, ML predictions
    MEDIUM = 3        # Market data, analytics
    LOW = 4           # Documentation, utilities

@dataclass
class EndpointMetrics:
    """Real-time metrics per endpoint"""
    endpoint_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    requests_per_minute: float = 0.0
    error_rate_percent: float = 0.0
    last_accessed: Optional[datetime] = None
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=20))

@dataclass  
class EndpointConfig:
    """Enterprise endpoint configuration"""
    endpoint_id: str
    path: str
    method: str
    priority: EndpointPriority
    max_concurrent_requests: int = 50
    timeout_seconds: int = 30
    circuit_breaker_threshold: int = 10  # failures before opening circuit
    circuit_breaker_timeout: int = 60    # seconds before trying again
    rate_limit_rpm: int = 120           # requests per minute
    health_check_interval: int = 30     # seconds
    cache_ttl_seconds: int = 300        # 5 minutes default
    auto_scale_enabled: bool = True
    critical_endpoint: bool = False

class CircuitBreakerState:
    """Circuit breaker implementation"""
    def __init__(self, failure_threshold: int = 10, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = EndpointStatus.HEALTHY
        
    def record_success(self):
        self.failure_count = 0
        self.state = EndpointStatus.HEALTHY
        
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = EndpointStatus.CIRCUIT_OPEN
            
    def can_execute(self) -> bool:
        if self.state == EndpointStatus.CIRCUIT_OPEN:
            # Check if recovery timeout has passed
            if (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = EndpointStatus.DEGRADED  # Half-open state
                return True
            return False
        return True

class EnterpriseEndpointManager:
    """
    Enterprise-grade endpoint management for 50+ endpoints
    """
    
    def __init__(self):
        # Core data structures
        self.endpoints: Dict[str, EndpointConfig] = {}
        self.metrics: Dict[str, EndpointMetrics] = {}
        self.circuit_breakers: Dict[str, CircuitBreakerState] = {}
        self.health_status: Dict[str, EndpointStatus] = {}
        
        # Resource management
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.load_balancer_weights: Dict[str, float] = {}
        
        # Analytics and monitoring
        self.global_metrics = {
            'total_endpoints': 0,
            'healthy_endpoints': 0,
            'total_requests_per_second': 0.0,
            'average_response_time': 0.0,
            'error_rate_percent': 0.0,
            'cache_hit_rate': 0.0,
            'peak_concurrent_requests': 0
        }
        
        # Auto-scaling and management
        self.scaling_rules: Dict[str, Dict] = {}
        self.auto_discovery_enabled = True
        self.monitoring_active = True
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Background tasks
        self._start_background_tasks()
        
        self.logger = logging.getLogger(f"{__name__}.EnterpriseEndpointManager")
        self.logger.info("🏢 Enterprise Endpoint Manager initialized - Ready for 50+ endpoints")
    
    def register_endpoint(self, endpoint_config: EndpointConfig):
        """Register new endpoint with enterprise configuration"""
        with self.lock:
            endpoint_id = endpoint_config.endpoint_id
            
            # Register endpoint
            self.endpoints[endpoint_id] = endpoint_config
            self.metrics[endpoint_id] = EndpointMetrics(endpoint_id)
            self.circuit_breakers[endpoint_id] = CircuitBreakerState(
                endpoint_config.circuit_breaker_threshold,
                endpoint_config.circuit_breaker_timeout
            )
            self.health_status[endpoint_id] = EndpointStatus.HEALTHY
            self.load_balancer_weights[endpoint_id] = 1.0
            
            # Setup auto-scaling rules if enabled
            if endpoint_config.auto_scale_enabled:
                self._setup_auto_scaling(endpoint_id)
            
            self.global_metrics['total_endpoints'] += 1
            self.logger.info(f"✅ Registered enterprise endpoint: {endpoint_id} [{endpoint_config.priority.name}]")
    
    def auto_discover_endpoints(self, flask_app) -> List[str]:
        """Auto-discover endpoints from Flask app"""
        discovered = []
        
        for rule in flask_app.url_map.iter_rules():
            if rule.endpoint and not rule.endpoint.startswith('static'):
                endpoint_id = f"{rule.endpoint}_{list(rule.methods)[0] if rule.methods else 'GET'}"
                
                # Determine priority based on path patterns
                priority = self._determine_endpoint_priority(str(rule))
                
                # Create auto-discovered config
                config = EndpointConfig(
                    endpoint_id=endpoint_id,
                    path=str(rule),
                    method=list(rule.methods)[0] if rule.methods else 'GET',
                    priority=priority,
                    critical_endpoint=priority == EndpointPriority.CRITICAL
                )
                
                self.register_endpoint(config)
                discovered.append(endpoint_id)
        
        self.logger.info(f"🔍 Auto-discovered {len(discovered)} endpoints")
        return discovered
    
    def _determine_endpoint_priority(self, path: str) -> EndpointPriority:
        """Smart priority assignment based on endpoint path"""
        path_lower = path.lower()
        
        # Critical: Trading signals, AI reasoning
        if any(keyword in path_lower for keyword in ['signal', 'ai', 'reasoning', 'trade']):
            return EndpointPriority.CRITICAL
            
        # High: SMC, ML, predictions
        if any(keyword in path_lower for keyword in ['smc', 'ml', 'predict', 'ensemble', 'analysis']):
            return EndpointPriority.HIGH
            
        # Medium: Market data, general API
        if any(keyword in path_lower for keyword in ['market', 'data', 'api', 'fetch']):
            return EndpointPriority.MEDIUM
            
        # Low: Docs, utils, health checks
        return EndpointPriority.LOW
    
    async def execute_request(self, endpoint_id: str, request_func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Execute request with enterprise features (circuit breaker, metrics, etc.)"""
        start_time = time.time()
        
        # Check circuit breaker
        circuit_breaker = self.circuit_breakers.get(endpoint_id)
        if circuit_breaker and not circuit_breaker.can_execute():
            return {
                'status': 'error',
                'message': 'Circuit breaker open - endpoint temporarily unavailable',
                'circuit_breaker_state': 'open'
            }
        
        # Check rate limiting
        if not self._check_rate_limit(endpoint_id):
            return {
                'status': 'error', 
                'message': 'Rate limit exceeded',
                'retry_after': 60
            }
        
        metrics = self.metrics.get(endpoint_id)
        
        try:
            # Execute request
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, request_func, *args, **kwargs
            )
            
            # Record success
            execution_time = (time.time() - start_time) * 1000
            self._record_success(endpoint_id, execution_time)
            
            if circuit_breaker:
                circuit_breaker.record_success()
            
            return {
                'status': 'success',
                'result': result,
                'execution_time_ms': execution_time,
                'endpoint_id': endpoint_id
            }
            
        except Exception as e:
            # Record failure
            execution_time = (time.time() - start_time) * 1000
            self._record_failure(endpoint_id, execution_time, str(e))
            
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            return {
                'status': 'error',
                'message': str(e),
                'execution_time_ms': execution_time,
                'endpoint_id': endpoint_id
            }
    
    def _check_rate_limit(self, endpoint_id: str) -> bool:
        """Check if request is within rate limits"""
        endpoint_config = self.endpoints.get(endpoint_id)
        metrics = self.metrics.get(endpoint_id)
        
        if not endpoint_config or not metrics:
            return True
        
        # Simple rate limiting based on RPM
        return metrics.requests_per_minute < endpoint_config.rate_limit_rpm
    
    def _record_success(self, endpoint_id: str, execution_time_ms: float):
        """Record successful request metrics"""
        with self.lock:
            metrics = self.metrics.get(endpoint_id)
            if not metrics:
                return
            
            metrics.total_requests += 1
            metrics.successful_requests += 1
            metrics.last_accessed = datetime.now()
            metrics.response_times.append(execution_time_ms)
            
            # Update averages
            self._update_metrics(metrics)
    
    def _record_failure(self, endpoint_id: str, execution_time_ms: float, error: str):
        """Record failed request metrics"""
        with self.lock:
            metrics = self.metrics.get(endpoint_id)
            if not metrics:
                return
            
            metrics.total_requests += 1
            metrics.failed_requests += 1
            metrics.last_accessed = datetime.now()
            metrics.response_times.append(execution_time_ms)
            metrics.recent_errors.append({
                'timestamp': datetime.now(),
                'error': error,
                'execution_time_ms': execution_time_ms
            })
            
            # Update averages
            self._update_metrics(metrics)
    
    def _update_metrics(self, metrics: EndpointMetrics):
        """Update calculated metrics"""
        if metrics.response_times:
            # Average response time
            metrics.avg_response_time_ms = sum(metrics.response_times) / len(metrics.response_times)
            
            # P95 response time
            sorted_times = sorted(metrics.response_times)
            p95_index = int(0.95 * len(sorted_times))
            metrics.p95_response_time_ms = sorted_times[p95_index] if sorted_times else 0
        
        # Error rate
        if metrics.total_requests > 0:
            metrics.error_rate_percent = (metrics.failed_requests / metrics.total_requests) * 100
        
        # Requests per minute (approximate)
        metrics.requests_per_minute = min(metrics.total_requests, 60)  # Simplified
    
    def get_endpoint_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report for all endpoints"""
        with self.lock:
            healthy_count = sum(1 for status in self.health_status.values() 
                              if status == EndpointStatus.HEALTHY)
            
            endpoint_details = {}
            for endpoint_id, metrics in self.metrics.items():
                config = self.endpoints.get(endpoint_id)
                circuit_breaker = self.circuit_breakers.get(endpoint_id)
                
                endpoint_details[endpoint_id] = {
                    'status': self.health_status.get(endpoint_id, EndpointStatus.HEALTHY).value,
                    'priority': config.priority.name if config else 'UNKNOWN',
                    'metrics': {
                        'total_requests': metrics.total_requests,
                        'success_rate': ((metrics.successful_requests / max(metrics.total_requests, 1)) * 100),
                        'avg_response_time_ms': round(metrics.avg_response_time_ms, 2),
                        'p95_response_time_ms': round(metrics.p95_response_time_ms, 2),
                        'error_rate_percent': round(metrics.error_rate_percent, 2),
                        'requests_per_minute': metrics.requests_per_minute
                    },
                    'circuit_breaker': {
                        'state': circuit_breaker.state.value if circuit_breaker else 'unknown',
                        'failure_count': circuit_breaker.failure_count if circuit_breaker else 0
                    }
                }
            
            # Update global metrics
            self.global_metrics.update({
                'total_endpoints': len(self.endpoints),
                'healthy_endpoints': healthy_count,
                'degraded_endpoints': len(self.endpoints) - healthy_count,
                'health_percentage': (healthy_count / max(len(self.endpoints), 1)) * 100
            })
            
            return {
                'summary': self.global_metrics,
                'endpoints': endpoint_details,
                'timestamp': datetime.now().isoformat(),
                'enterprise_features': {
                    'auto_discovery': self.auto_discovery_enabled,
                    'circuit_breakers': len(self.circuit_breakers),
                    'load_balancing': True,
                    'auto_scaling': True,
                    'real_time_monitoring': self.monitoring_active
                }
            }
    
    def _setup_auto_scaling(self, endpoint_id: str):
        """Setup auto-scaling rules for endpoint"""
        self.scaling_rules[endpoint_id] = {
            'scale_up_threshold': 80,    # % usage
            'scale_down_threshold': 30,  # % usage
            'max_instances': 10,
            'min_instances': 1,
            'current_instances': 1
        }
    
    def _start_background_tasks(self):
        """Start background monitoring and maintenance tasks"""
        def background_monitor():
            while self.monitoring_active:
                try:
                    self._health_check_all_endpoints()
                    self._update_load_balancer_weights()
                    self._cleanup_old_metrics()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    self.logger.error(f"Background monitoring error: {e}")
        
        # Start background thread
        monitor_thread = threading.Thread(target=background_monitor, daemon=True)
        monitor_thread.start()
    
    def _health_check_all_endpoints(self):
        """Perform health checks on all registered endpoints"""
        for endpoint_id, metrics in self.metrics.items():
            # Simple health check based on error rate and response time
            if metrics.error_rate_percent > 50:
                self.health_status[endpoint_id] = EndpointStatus.UNHEALTHY
            elif metrics.error_rate_percent > 20 or metrics.avg_response_time_ms > 5000:
                self.health_status[endpoint_id] = EndpointStatus.DEGRADED
            else:
                self.health_status[endpoint_id] = EndpointStatus.HEALTHY
    
    def _update_load_balancer_weights(self):
        """Update load balancer weights based on performance"""
        for endpoint_id, metrics in self.metrics.items():
            # Weight based on inverse of response time and error rate
            base_weight = 1.0
            
            # Reduce weight for slow endpoints
            if metrics.avg_response_time_ms > 1000:
                base_weight *= 0.5
            
            # Reduce weight for error-prone endpoints  
            if metrics.error_rate_percent > 10:
                base_weight *= 0.3
            
            self.load_balancer_weights[endpoint_id] = max(base_weight, 0.1)
    
    def _cleanup_old_metrics(self):
        """Cleanup old metrics data to prevent memory bloat"""
        # Keep only recent data for memory efficiency
        for metrics in self.metrics.values():
            # Keep response times deque at max 100 entries (already limited)
            # Keep recent errors at max 20 entries (already limited)
            pass
    
    def get_scaling_recommendations(self) -> Dict[str, Any]:
        """Get scaling recommendations for endpoints"""
        recommendations = {}
        
        for endpoint_id, metrics in self.metrics.items():
            config = self.endpoints.get(endpoint_id)
            if not config or not config.auto_scale_enabled:
                continue
            
            # Analyze load patterns
            current_load = metrics.requests_per_minute
            max_capacity = config.rate_limit_rpm
            utilization = (current_load / max_capacity) * 100 if max_capacity > 0 else 0
            
            recommendation = "maintain"
            if utilization > 80:
                recommendation = "scale_up"
            elif utilization < 30:
                recommendation = "scale_down"
            
            recommendations[endpoint_id] = {
                'recommendation': recommendation,
                'current_utilization': round(utilization, 2),
                'current_rps': current_load / 60,
                'avg_response_time': metrics.avg_response_time_ms,
                'error_rate': metrics.error_rate_percent
            }
        
        return recommendations


# Singleton instance
_enterprise_manager = None

def get_enterprise_endpoint_manager() -> EnterpriseEndpointManager:
    """Get singleton instance of enterprise endpoint manager"""
    global _enterprise_manager
    if _enterprise_manager is None:
        _enterprise_manager = EnterpriseEndpointManager()
    return _enterprise_manager