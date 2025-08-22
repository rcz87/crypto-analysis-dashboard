#!/usr/bin/env python3
"""
Real-Time Analytics Engine
Advanced analytics untuk 50+ endpoints dengan:
- Real-time performance monitoring
- Predictive load analysis
- Usage pattern detection
- Anomaly detection
- Business intelligence dashboards
"""

import time
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsEvent:
    """Real-time analytics event"""
    timestamp: float
    event_type: str  # 'request', 'error', 'cache_hit', 'cache_miss'
    endpoint_id: str
    data: Dict[str, Any]
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

@dataclass
class TimeSeriesPoint:
    """Time series data point"""
    timestamp: float
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class RealTimeMetrics:
    """Real-time metrics collector"""
    
    def __init__(self, max_points: int = 1440):  # 24 hours of minute-by-minute data
        self.max_points = max_points
        self.data_points: deque = deque(maxlen=max_points)
        self.current_minute_data: Dict[str, List] = defaultdict(list)
        self.last_minute = int(time.time() // 60)
        self.lock = threading.RLock()
    
    def add_data_point(self, metric_name: str, value: float, metadata: Dict = None):
        """Add real-time data point"""
        current_minute = int(time.time() // 60)
        
        with self.lock:
            # Check if we moved to a new minute
            if current_minute != self.last_minute:
                self._aggregate_minute_data()
                self.last_minute = current_minute
            
            # Add to current minute data
            self.current_minute_data[metric_name].append({
                'value': value,
                'timestamp': time.time(),
                'metadata': metadata or {}
            })
    
    def _aggregate_minute_data(self):
        """Aggregate current minute data"""
        if not self.current_minute_data:
            return
        
        aggregated = {}
        for metric_name, data_list in self.current_minute_data.items():
            values = [d['value'] for d in data_list]
            if values:
                aggregated[metric_name] = {
                    'avg': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'count': len(values),
                    'sum': sum(values)
                }
        
        # Add aggregated minute to time series
        if aggregated:
            self.data_points.append(TimeSeriesPoint(
                timestamp=self.last_minute * 60,
                value=0,  # Will be used for primary metric
                metadata=aggregated
            ))
        
        # Clear current minute data
        self.current_minute_data.clear()
    
    def get_time_series(self, metric_name: str, minutes: int = 60) -> List[TimeSeriesPoint]:
        """Get time series untuk specific metric"""
        with self.lock:
            cutoff_time = time.time() - (minutes * 60)
            
            result = []
            for point in self.data_points:
                if point.timestamp >= cutoff_time:
                    if metric_name in point.metadata:
                        new_point = TimeSeriesPoint(
                            timestamp=point.timestamp,
                            value=point.metadata[metric_name].get('avg', 0),
                            metadata=point.metadata[metric_name]
                        )
                        result.append(new_point)
            
            return result

class PredictiveAnalyzer:
    """Predictive analytics untuk load forecasting"""
    
    def __init__(self):
        self.historical_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=168))  # 1 week of hourly data
        self.prediction_cache: Dict[str, Dict] = {}
        self.last_prediction_time = 0
        self.prediction_interval = 300  # 5 minutes
    
    def add_hourly_data(self, endpoint_id: str, requests_count: int, avg_response_time: float):
        """Add hourly aggregated data"""
        hour_timestamp = int(time.time() // 3600) * 3600
        
        self.historical_data[endpoint_id].append({
            'timestamp': hour_timestamp,
            'requests': requests_count,
            'response_time': avg_response_time,
            'hour_of_day': datetime.fromtimestamp(hour_timestamp).hour,
            'day_of_week': datetime.fromtimestamp(hour_timestamp).weekday()
        })
    
    def predict_load(self, endpoint_id: str, hours_ahead: int = 1) -> Dict[str, Any]:
        """Predict future load untuk endpoint"""
        current_time = time.time()
        
        # Check if we need to update predictions
        if current_time - self.last_prediction_time < self.prediction_interval:
            return self.prediction_cache.get(endpoint_id, {})
        
        historical = list(self.historical_data[endpoint_id])
        if len(historical) < 24:  # Need at least 1 day of data
            return {'status': 'insufficient_data', 'prediction': None}
        
        # Simple pattern-based prediction
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        # Find similar time periods
        similar_periods = []
        for data_point in historical[-48:]:  # Last 2 days
            if (data_point['hour_of_day'] == current_hour and 
                data_point['day_of_week'] == current_day):
                similar_periods.append(data_point)
        
        if not similar_periods:
            # Fall back to same hour any day
            similar_periods = [d for d in historical[-72:] if d['hour_of_day'] == current_hour]
        
        if similar_periods:
            predicted_requests = statistics.mean([p['requests'] for p in similar_periods])
            predicted_response_time = statistics.mean([p['response_time'] for p in similar_periods])
            
            # Add trend analysis
            recent_trend = self._calculate_trend(historical[-24:])  # Last 24 hours
            predicted_requests *= (1 + recent_trend)
            
            prediction = {
                'status': 'success',
                'prediction': {
                    'requests_per_hour': round(predicted_requests, 2),
                    'avg_response_time_ms': round(predicted_response_time, 2),
                    'confidence': min(len(similar_periods) * 10, 100),  # More data = higher confidence
                    'trend_factor': recent_trend,
                    'predicted_for': hours_ahead
                }
            }
        else:
            prediction = {'status': 'no_pattern_found', 'prediction': None}
        
        self.prediction_cache[endpoint_id] = prediction
        self.last_prediction_time = current_time
        
        return prediction
    
    def _calculate_trend(self, recent_data: List[Dict]) -> float:
        """Calculate trend dari recent data"""
        if len(recent_data) < 2:
            return 0.0
        
        # Simple linear trend
        requests_series = [d['requests'] for d in recent_data]
        n = len(requests_series)
        
        if n < 2:
            return 0.0
        
        # Calculate slope
        x_avg = (n - 1) / 2
        y_avg = sum(requests_series) / n
        
        numerator = sum((i - x_avg) * (requests_series[i] - y_avg) for i in range(n))
        denominator = sum((i - x_avg) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Convert to percentage change
        return slope / max(y_avg, 1) if y_avg > 0 else 0.0

class AnomalyDetector:
    """Anomaly detection untuk endpoint behavior"""
    
    def __init__(self):
        self.baseline_metrics: Dict[str, Dict] = defaultdict(lambda: {
            'avg_response_time': 0.0,
            'std_response_time': 0.0,
            'avg_requests_per_minute': 0.0,
            'std_requests_per_minute': 0.0,
            'error_rate': 0.0,
            'last_updated': 0
        })
        self.anomalies: deque = deque(maxlen=100)  # Keep last 100 anomalies
    
    def update_baseline(self, endpoint_id: str, metrics: Dict[str, Any]):
        """Update baseline metrics untuk endpoint"""
        baseline = self.baseline_metrics[endpoint_id]
        
        # Update with exponential moving average
        alpha = 0.1  # Learning rate
        
        current_response_time = metrics.get('avg_response_time_ms', 0)
        current_requests_per_minute = metrics.get('requests_per_minute', 0)
        current_error_rate = metrics.get('error_rate_percent', 0)
        
        baseline['avg_response_time'] = (baseline['avg_response_time'] * (1 - alpha) + 
                                       current_response_time * alpha)
        baseline['avg_requests_per_minute'] = (baseline['avg_requests_per_minute'] * (1 - alpha) + 
                                             current_requests_per_minute * alpha)
        baseline['error_rate'] = (baseline['error_rate'] * (1 - alpha) + 
                                current_error_rate * alpha)
        baseline['last_updated'] = time.time()
    
    def detect_anomalies(self, endpoint_id: str, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in endpoint behavior"""
        baseline = self.baseline_metrics[endpoint_id]
        if baseline['last_updated'] == 0:
            return []  # No baseline yet
        
        anomalies = []
        current_time = time.time()
        
        # Response time anomaly
        current_response_time = current_metrics.get('avg_response_time_ms', 0)
        if (baseline['avg_response_time'] > 0 and 
            current_response_time > baseline['avg_response_time'] * 3):  # 3x normal
            anomalies.append({
                'type': 'high_response_time',
                'severity': 'high',
                'current_value': current_response_time,
                'baseline_value': baseline['avg_response_time'],
                'ratio': current_response_time / baseline['avg_response_time'],
                'endpoint_id': endpoint_id,
                'timestamp': current_time
            })
        
        # Error rate anomaly
        current_error_rate = current_metrics.get('error_rate_percent', 0)
        if current_error_rate > baseline['error_rate'] * 2 + 5:  # 2x normal + 5%
            anomalies.append({
                'type': 'high_error_rate',
                'severity': 'critical',
                'current_value': current_error_rate,
                'baseline_value': baseline['error_rate'],
                'endpoint_id': endpoint_id,
                'timestamp': current_time
            })
        
        # Traffic spike anomaly
        current_requests = current_metrics.get('requests_per_minute', 0)
        if (baseline['avg_requests_per_minute'] > 0 and 
            current_requests > baseline['avg_requests_per_minute'] * 5):  # 5x normal traffic
            anomalies.append({
                'type': 'traffic_spike',
                'severity': 'medium',
                'current_value': current_requests,
                'baseline_value': baseline['avg_requests_per_minute'],
                'ratio': current_requests / baseline['avg_requests_per_minute'],
                'endpoint_id': endpoint_id,
                'timestamp': current_time
            })
        
        # Store anomalies
        for anomaly in anomalies:
            self.anomalies.append(anomaly)
        
        return anomalies

class RealTimeAnalyticsEngine:
    """
    Real-Time Analytics Engine untuk 50+ endpoints
    """
    
    def __init__(self):
        # Core components
        self.metrics_collector = defaultdict(lambda: RealTimeMetrics())
        self.predictive_analyzer = PredictiveAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        # Event processing
        self.event_queue: deque = deque(maxlen=10000)
        self.event_processors: List[Callable] = []
        
        # Real-time dashboards data
        self.dashboard_data: Dict[str, Any] = {
            'endpoint_performance': {},
            'system_overview': {},
            'alerts': [],
            'predictions': {},
            'trends': {}
        }
        
        # Background processing
        self.processing_active = True
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Configuration
        self.alert_thresholds = {
            'response_time_ms': 5000,
            'error_rate_percent': 10,
            'requests_per_minute': 1000
        }
        
        self._start_background_processing()
        
        self.logger = logging.getLogger(f"{__name__}.RealTimeAnalyticsEngine")
        self.logger.info("📊 Real-Time Analytics Engine initialized - Advanced monitoring active")
    
    def record_event(self, event_type: str, endpoint_id: str, 
                    data: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Record analytics event"""
        event = AnalyticsEvent(
            timestamp=time.time(),
            event_type=event_type,
            endpoint_id=endpoint_id,
            data=data,
            user_agent=metadata.get('user_agent') if metadata else None,
            ip_address=metadata.get('ip_address') if metadata else None
        )
        
        self.event_queue.append(event)
    
    def record_request_metrics(self, endpoint_id: str, 
                             response_time_ms: float,
                             success: bool,
                             metadata: Dict[str, Any] = None):
        """Record request performance metrics"""
        metrics = self.metrics_collector[endpoint_id]
        
        # Record response time
        metrics.add_data_point('response_time_ms', response_time_ms, metadata)
        
        # Record success/failure
        metrics.add_data_point('requests_total', 1, metadata)
        if success:
            metrics.add_data_point('requests_success', 1, metadata)
        else:
            metrics.add_data_point('requests_error', 1, metadata)
        
        # Record event
        self.record_event(
            'request_completed' if success else 'request_failed',
            endpoint_id,
            {'response_time_ms': response_time_ms, 'success': success},
            metadata
        )
    
    def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        current_time = time.time()
        
        # Update dashboard with latest data
        dashboard = {
            'timestamp': current_time,
            'system_overview': self._get_system_overview(),
            'endpoint_performance': self._get_endpoint_performance(),
            'top_endpoints': self._get_top_endpoints(),
            'recent_alerts': self._get_recent_alerts(),
            'predictions': self._get_predictions(),
            'performance_trends': self._get_performance_trends(),
            'anomalies': list(self.anomaly_detector.anomalies)[-20:]  # Last 20 anomalies
        }
        
        self.dashboard_data = dashboard
        return dashboard
    
    def _get_system_overview(self) -> Dict[str, Any]:
        """Get overall system performance overview"""
        total_requests = 0
        total_errors = 0
        response_times = []
        active_endpoints = 0
        
        for endpoint_id, metrics in self.metrics_collector.items():
            recent_points = metrics.get_time_series('requests_total', minutes=5)
            if recent_points:
                active_endpoints += 1
                
                # Sum requests in last 5 minutes
                endpoint_requests = sum(p.metadata.get('sum', 0) for p in recent_points)
                total_requests += endpoint_requests
                
                # Get error data
                error_points = metrics.get_time_series('requests_error', minutes=5)
                endpoint_errors = sum(p.metadata.get('sum', 0) for p in error_points)
                total_errors += endpoint_errors
                
                # Get response times
                rt_points = metrics.get_time_series('response_time_ms', minutes=5)
                for point in rt_points:
                    response_times.append(point.value)
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        error_rate = (total_errors / max(total_requests, 1)) * 100
        requests_per_minute = total_requests / 5  # 5 minutes of data
        
        return {
            'active_endpoints': active_endpoints,
            'total_requests_5min': total_requests,
            'requests_per_minute': round(requests_per_minute, 2),
            'avg_response_time_ms': round(avg_response_time, 2),
            'error_rate_percent': round(error_rate, 2),
            'status': 'healthy' if error_rate < 5 and avg_response_time < 2000 else 'degraded'
        }
    
    def _get_endpoint_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get per-endpoint performance data"""
        performance_data = {}
        
        for endpoint_id, metrics in self.metrics_collector.items():
            # Get recent metrics
            request_points = metrics.get_time_series('requests_total', minutes=10)
            response_points = metrics.get_time_series('response_time_ms', minutes=10)
            error_points = metrics.get_time_series('requests_error', minutes=10)
            
            if request_points:
                total_requests = sum(p.metadata.get('sum', 0) for p in request_points)
                total_errors = sum(p.metadata.get('sum', 0) for p in error_points)
                
                avg_response_time = 0
                if response_points:
                    avg_response_time = statistics.mean([p.value for p in response_points])
                
                error_rate = (total_errors / max(total_requests, 1)) * 100
                
                performance_data[endpoint_id] = {
                    'requests_10min': total_requests,
                    'requests_per_minute': round(total_requests / 10, 2),
                    'avg_response_time_ms': round(avg_response_time, 2),
                    'error_rate_percent': round(error_rate, 2),
                    'status': 'healthy' if error_rate < 10 and avg_response_time < 3000 else 'degraded'
                }
                
                # Update anomaly detector baseline
                self.anomaly_detector.update_baseline(endpoint_id, performance_data[endpoint_id])
                
                # Check for anomalies
                anomalies = self.anomaly_detector.detect_anomalies(endpoint_id, performance_data[endpoint_id])
                if anomalies:
                    performance_data[endpoint_id]['anomalies'] = anomalies
        
        return performance_data
    
    def _get_top_endpoints(self) -> List[Dict[str, Any]]:
        """Get top endpoints by various metrics"""
        endpoint_stats = []
        
        for endpoint_id, metrics in self.metrics_collector.items():
            request_points = metrics.get_time_series('requests_total', minutes=60)  # Last hour
            if request_points:
                total_requests = sum(p.metadata.get('sum', 0) for p in request_points)
                endpoint_stats.append({
                    'endpoint_id': endpoint_id,
                    'requests_per_hour': total_requests,
                    'requests_per_minute': round(total_requests / 60, 2)
                })
        
        # Sort by requests per hour
        top_by_traffic = sorted(endpoint_stats, key=lambda x: x['requests_per_hour'], reverse=True)[:10]
        
        return {
            'by_traffic': top_by_traffic
        }
    
    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        alerts = []
        current_time = time.time()
        
        for endpoint_id, metrics in self.metrics_collector.items():
            recent_points = metrics.get_time_series('response_time_ms', minutes=5)
            if recent_points:
                avg_response_time = statistics.mean([p.value for p in recent_points])
                
                # Check thresholds
                if avg_response_time > self.alert_thresholds['response_time_ms']:
                    alerts.append({
                        'type': 'high_response_time',
                        'severity': 'warning',
                        'endpoint_id': endpoint_id,
                        'current_value': round(avg_response_time, 2),
                        'threshold': self.alert_thresholds['response_time_ms'],
                        'timestamp': current_time
                    })
        
        return alerts
    
    def _get_predictions(self) -> Dict[str, Any]:
        """Get load predictions for endpoints"""
        predictions = {}
        
        # Get predictions for top 10 most active endpoints
        top_endpoints = self._get_top_endpoints()
        for endpoint_data in top_endpoints.get('by_traffic', [])[:10]:
            endpoint_id = endpoint_data['endpoint_id']
            prediction = self.predictive_analyzer.predict_load(endpoint_id, hours_ahead=1)
            if prediction['status'] == 'success':
                predictions[endpoint_id] = prediction['prediction']
        
        return predictions
    
    def _get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends"""
        trends = {}
        
        for endpoint_id, metrics in self.metrics_collector.items():
            # Get last 2 hours of data
            points_2h = metrics.get_time_series('response_time_ms', minutes=120)
            points_1h = metrics.get_time_series('response_time_ms', minutes=60)
            
            if len(points_2h) >= 2 and len(points_1h) >= 1:
                # Calculate trend
                avg_2h = statistics.mean([p.value for p in points_2h])
                avg_1h = statistics.mean([p.value for p in points_1h])
                
                trend_direction = 'improving' if avg_1h < avg_2h else 'degrading'
                trend_magnitude = abs(avg_1h - avg_2h) / avg_2h * 100 if avg_2h > 0 else 0
                
                trends[endpoint_id] = {
                    'direction': trend_direction,
                    'magnitude_percent': round(trend_magnitude, 2),
                    'current_avg_ms': round(avg_1h, 2),
                    'previous_avg_ms': round(avg_2h, 2)
                }
        
        return trends
    
    def _start_background_processing(self):
        """Start background processing threads"""
        def process_events():
            while self.processing_active:
                try:
                    # Process events in batches
                    batch_size = min(100, len(self.event_queue))
                    if batch_size > 0:
                        events = [self.event_queue.popleft() for _ in range(batch_size)]
                        self._process_event_batch(events)
                    
                    time.sleep(1)  # Process every second
                except Exception as e:
                    self.logger.error(f"Event processing error: {e}")
        
        # Start event processing thread
        event_thread = threading.Thread(target=process_events, daemon=True)
        event_thread.start()
    
    def _process_event_batch(self, events: List[AnalyticsEvent]):
        """Process batch of events"""
        # Group events by endpoint for efficient processing
        by_endpoint = defaultdict(list)
        for event in events:
            by_endpoint[event.endpoint_id].append(event)
        
        # Process each endpoint's events
        for endpoint_id, endpoint_events in by_endpoint.items():
            self._process_endpoint_events(endpoint_id, endpoint_events)
    
    def _process_endpoint_events(self, endpoint_id: str, events: List[AnalyticsEvent]):
        """Process events for specific endpoint"""
        # Aggregate hourly data for predictive analysis
        hour_timestamp = int(time.time() // 3600) * 3600
        
        requests_this_hour = len([e for e in events if e.event_type.startswith('request')])
        response_times = [e.data.get('response_time_ms', 0) for e in events 
                         if 'response_time_ms' in e.data and e.data['response_time_ms'] > 0]
        
        if requests_this_hour > 0 and response_times:
            avg_response_time = statistics.mean(response_times)
            self.predictive_analyzer.add_hourly_data(endpoint_id, requests_this_hour, avg_response_time)
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        return {
            'real_time_dashboard': self.get_real_time_dashboard(),
            'system_health': self._get_system_overview(),
            'predictions': self._get_predictions(),
            'anomalies_count': len(self.anomaly_detector.anomalies),
            'monitored_endpoints': len(self.metrics_collector),
            'events_processed': len(self.event_queue),
            'alert_thresholds': self.alert_thresholds
        }

# Singleton instance
_analytics_engine = None

def get_real_time_analytics_engine() -> RealTimeAnalyticsEngine:
    """Get singleton instance"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = RealTimeAnalyticsEngine()
    return _analytics_engine