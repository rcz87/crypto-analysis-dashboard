#!/usr/bin/env python3
"""
Memory Optimizer - Advanced memory management and optimization
Garbage collection tuning, memory pools, object caching, dan memory leak detection
"""

import logging
import gc
import sys
import time
import threading
import tracemalloc
import weakref
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class MemorySnapshot:
    timestamp: float
    total_memory_mb: float
    process_memory_mb: float
    gc_objects: int
    gc_collections: Dict[int, int]
    top_allocations: List[Dict[str, Any]]

@dataclass
class MemoryLeak:
    object_type: str
    count_increase: int
    growth_rate: float
    first_detected: float
    severity: str  # low, medium, high, critical

class ObjectPool:
    """
    Generic object pool untuk reuse objects dan reduce garbage collection
    """
    
    def __init__(self, factory: Callable, max_size: int = 100, reset_func: Optional[Callable] = None):
        self.factory = factory
        self.max_size = max_size
        self.reset_func = reset_func
        self.pool = deque()
        self.created_objects = 0
        self.reused_objects = 0
        self.lock = threading.Lock()
        
        self.logger = logging.getLogger(__name__)
    
    def acquire(self):
        """Get object from pool atau create new one"""
        with self.lock:
            if self.pool:
                obj = self.pool.popleft()
                self.reused_objects += 1
                return obj
            else:
                obj = self.factory()
                self.created_objects += 1
                return obj
    
    def release(self, obj):
        """Return object to pool"""
        with self.lock:
            if len(self.pool) < self.max_size:
                # Reset object state if reset function provided
                if self.reset_func:
                    try:
                        self.reset_func(obj)
                    except Exception as e:
                        self.logger.warning(f"Error resetting object: {e}")
                        return  # Don't add to pool if reset failed
                
                self.pool.append(obj)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        with self.lock:
            total_objects = self.created_objects
            reuse_rate = (self.reused_objects / max(1, total_objects)) * 100
            
            return {
                'pool_size': len(self.pool),
                'max_size': self.max_size,
                'created_objects': self.created_objects,
                'reused_objects': self.reused_objects,
                'reuse_rate_percent': round(reuse_rate, 2),
                'pool_utilization_percent': (len(self.pool) / self.max_size) * 100
            }

class MemoryTracker:
    """
    Advanced memory tracking dan leak detection
    """
    
    def __init__(self, snapshot_interval: int = 60):
        self.snapshot_interval = snapshot_interval
        self.snapshots = deque(maxlen=1440)  # Keep 24 hours of data (1 minute intervals)
        self.object_counts = defaultdict(lambda: deque(maxlen=100))
        self.potential_leaks = {}
        self.tracking_enabled = False
        
        self.logger = logging.getLogger(__name__)
        
        # Start memory tracking thread
        self.tracking_thread = threading.Thread(target=self._memory_tracking_loop, daemon=True)
        self.tracking_thread.start()
        
        self.logger.info(f"📊 Memory Tracker initialized with {snapshot_interval}s intervals")
    
    def start_tracking(self):
        """Start detailed memory tracking"""
        if not self.tracking_enabled:
            tracemalloc.start()
            self.tracking_enabled = True
            self.logger.info("🔍 Detailed memory tracking started")
    
    def stop_tracking(self):
        """Stop detailed memory tracking"""
        if self.tracking_enabled:
            tracemalloc.stop()
            self.tracking_enabled = False
            self.logger.info("⏹️ Detailed memory tracking stopped")
    
    def take_snapshot(self) -> MemorySnapshot:
        """Take comprehensive memory snapshot"""
        # System memory info
        memory_info = psutil.virtual_memory()
        
        # Process memory info
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # Garbage collection info
        gc_stats = gc.get_stats()
        gc_counts = {i: gc.get_count()[i] for i in range(len(gc.get_count()))}
        
        # Top memory allocations (if tracking enabled)
        top_allocations = []
        if self.tracking_enabled:
            try:
                snapshot = tracemalloc.take_snapshot()
                top_stats = snapshot.statistics('lineno')[:10]
                
                for stat in top_stats:
                    top_allocations.append({
                        'filename': stat.traceback.format()[-1] if stat.traceback else 'unknown',
                        'size_mb': stat.size / 1024 / 1024,
                        'count': stat.count
                    })
            except Exception as e:
                self.logger.warning(f"Error getting memory allocations: {e}")
        
        snapshot = MemorySnapshot(
            timestamp=time.time(),
            total_memory_mb=memory_info.used / 1024 / 1024,
            process_memory_mb=process_memory.rss / 1024 / 1024,
            gc_objects=len(gc.get_objects()),
            gc_collections=gc_counts,
            top_allocations=top_allocations
        )
        
        self.snapshots.append(snapshot)
        self._update_object_tracking()
        self._detect_memory_leaks()
        
        return snapshot
    
    def _update_object_tracking(self):
        """Update object count tracking"""
        # Track different object types
        object_types = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            object_types[obj_type] = object_types.get(obj_type, 0) + 1
        
        # Update tracking for each type
        current_time = time.time()
        for obj_type, count in object_types.items():
            self.object_counts[obj_type].append((current_time, count))
    
    def _detect_memory_leaks(self):
        """Detect potential memory leaks"""
        current_time = time.time()
        
        for obj_type, counts in self.object_counts.items():
            if len(counts) < 10:  # Need enough data points
                continue
            
            # Calculate growth rate
            recent_counts = list(counts)[-10:]
            if len(recent_counts) >= 2:
                time_span = recent_counts[-1][0] - recent_counts[0][0]
                count_increase = recent_counts[-1][1] - recent_counts[0][1]
                
                if time_span > 0 and count_increase > 0:
                    growth_rate = count_increase / time_span  # objects per second
                    
                    # Detect potential leak with stricter thresholds
                    if growth_rate > 5 and count_increase > 500:  # Stricter threshold values
                        severity = self._calculate_leak_severity(growth_rate, count_increase)
                        
                        leak_id = f"{obj_type}"
                        if leak_id not in self.potential_leaks:
                            self.potential_leaks[leak_id] = MemoryLeak(
                                object_type=obj_type,
                                count_increase=count_increase,
                                growth_rate=growth_rate,
                                first_detected=current_time,
                                severity=severity
                            )
                            
                            self.logger.warning(f"🚨 Potential memory leak detected: {obj_type} (+{count_increase} objects, {growth_rate:.2f}/s)")
    
    def _calculate_leak_severity(self, growth_rate: float, count_increase: int) -> str:
        """Calculate memory leak severity"""
        if growth_rate > 10 or count_increase > 1000:
            return "critical"
        elif growth_rate > 5 or count_increase > 500:
            return "high"
        elif growth_rate > 2 or count_increase > 200:
            return "medium"
        else:
            return "low"
    
    def _memory_tracking_loop(self):
        """Background memory tracking loop"""
        while True:
            try:
                time.sleep(self.snapshot_interval)
                self.take_snapshot()
            except Exception as e:
                self.logger.error(f"Error in memory tracking: {e}")
    
    def get_memory_report(self, hours: int = 1) -> Dict[str, Any]:
        """Generate comprehensive memory report"""
        cutoff_time = time.time() - (hours * 3600)
        recent_snapshots = [s for s in self.snapshots if s.timestamp > cutoff_time]
        
        if not recent_snapshots:
            return {'error': 'No recent memory data available'}
        
        # Calculate memory trends
        memory_values = [s.process_memory_mb for s in recent_snapshots]
        memory_trend = "increasing" if memory_values[-1] > memory_values[0] else "decreasing"
        memory_change = memory_values[-1] - memory_values[0]
        
        # GC statistics
        gc_collections_total = sum(recent_snapshots[-1].gc_collections.values())
        
        current_memory_mb = recent_snapshots[-1].process_memory_mb if recent_snapshots else 0
        
        return {
            'period_hours': hours,
            'snapshots_count': len(recent_snapshots),
            'current_memory_mb': current_memory_mb,
            'memory_trend': memory_trend,
            'memory_change_mb': round(memory_change, 2),
            'max_memory_mb': max(memory_values) if memory_values else 0,
            'min_memory_mb': min(memory_values) if memory_values else 0,
            'avg_memory_mb': round(sum(memory_values) / len(memory_values), 2) if memory_values else 0,
            'gc_objects': recent_snapshots[-1].gc_objects if recent_snapshots else 0,
            'gc_collections_total': gc_collections_total,
            'potential_leaks': len(self.potential_leaks),
            'leak_details': [
                {
                    'object_type': leak.object_type,
                    'severity': leak.severity,
                    'growth_rate': round(leak.growth_rate, 2),
                    'count_increase': leak.count_increase
                }
                for leak in self.potential_leaks.values()
            ],
            'top_allocations': recent_snapshots[-1].top_allocations[:5] if recent_snapshots and recent_snapshots[-1].top_allocations else [],
            'recommendations': self._generate_memory_recommendations(recent_snapshots)
        }
    
    def _generate_memory_recommendations(self, snapshots: List[MemorySnapshot]) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = []
        
        if not snapshots:
            return recommendations
        
        current = snapshots[-1]
        
        # High memory usage
        if current.process_memory_mb > 1000:  # 1GB
            recommendations.append("⚠️ High memory usage detected - consider optimization")
        
        # Memory growth
        if len(snapshots) > 1:
            growth = current.process_memory_mb - snapshots[0].process_memory_mb
            if growth > 100:  # 100MB growth
                recommendations.append(f"📈 Memory increased by {growth:.1f}MB - monitor for leaks")
        
        # Too many objects
        if current.gc_objects > 1000000:  # 1M objects
            recommendations.append("🗑️ High object count - consider object pooling")
        
        # Potential leaks
        if self.potential_leaks:
            critical_leaks = [l for l in self.potential_leaks.values() if l.severity in ['critical', 'high']]
            if critical_leaks:
                recommendations.append(f"🚨 {len(critical_leaks)} critical memory leak(s) detected")
        
        # General recommendations
        recommendations.extend([
            "🔄 Run garbage collection periodically",
            "📦 Use object pools untuk frequently created objects",
            "💾 Monitor memory allocations in hot paths"
        ])
        
        return recommendations

class GCOptimizer:
    """
    Garbage Collection optimization dan tuning
    """
    
    def __init__(self):
        self.gc_stats = defaultdict(int)
        self.auto_gc_enabled = True
        self.gc_threshold_multiplier = 1.0
        
        self.logger = logging.getLogger(__name__)
        
        # Store original GC thresholds
        self.original_thresholds = gc.get_threshold()
        
        self.logger.info("🗑️ GC Optimizer initialized")
    
    def optimize_gc_thresholds(self, memory_pressure: str = "normal"):
        """Optimize GC thresholds berdasarkan memory pressure"""
        base_thresholds = self.original_thresholds
        
        if memory_pressure == "high":
            # More aggressive GC
            multiplier = 0.5
        elif memory_pressure == "low":
            # Less aggressive GC untuk better performance
            multiplier = 2.0
        else:
            # Normal
            multiplier = 1.0
        
        new_thresholds = tuple(int(t * multiplier) for t in base_thresholds)
        gc.set_threshold(*new_thresholds)
        
        self.logger.info(f"GC thresholds updated: {new_thresholds} (pressure: {memory_pressure})")
    
    def force_gc_collection(self) -> Dict[str, Any]:
        """Force comprehensive garbage collection"""
        before_objects = len(gc.get_objects())
        before_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Collect all generations
        collected = {}
        for generation in range(3):
            collected[generation] = gc.collect(generation)
        
        after_objects = len(gc.get_objects())
        after_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        objects_freed = before_objects - after_objects
        memory_freed = before_memory - after_memory
        
        result = {
            'objects_before': before_objects,
            'objects_after': after_objects,
            'objects_freed': objects_freed,
            'memory_before_mb': round(before_memory, 2),
            'memory_after_mb': round(after_memory, 2),
            'memory_freed_mb': round(memory_freed, 2),
            'collections_by_generation': collected
        }
        
        self.logger.info(f"Forced GC: freed {objects_freed} objects, {memory_freed:.1f}MB memory")
        return result
    
    def get_gc_stats(self) -> Dict[str, Any]:
        """Get garbage collection statistics"""
        stats = gc.get_stats()
        counts = gc.get_count()
        thresholds = gc.get_threshold()
        
        return {
            'current_counts': counts,
            'thresholds': thresholds,
            'total_objects': len(gc.get_objects()),
            'generation_stats': [
                {
                    'generation': i,
                    'collections': stats[i]['collections'],
                    'collected': stats[i]['collected'],
                    'uncollectable': stats[i]['uncollectable']
                }
                for i in range(len(stats))
            ],
            'gc_enabled': gc.isenabled(),
            'recommendations': [
                f"Current objects: {len(gc.get_objects())}",
                f"GC enabled: {gc.isenabled()}",
                f"Thresholds: {thresholds}",
                "Consider manual GC if memory usage is high"
            ]
        }

class MemoryOptimizer:
    """
    Main Memory Optimization Engine
    """
    
    def __init__(self):
        self.tracker = MemoryTracker(snapshot_interval=30)  # 30 second intervals
        self.gc_optimizer = GCOptimizer()
        self.object_pools = {}
        
        # Default object pools
        self._initialize_default_pools()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Memory Optimizer initialized")
    
    def _initialize_default_pools(self):
        """Initialize default object pools"""
        # List pool
        self.object_pools['list'] = ObjectPool(
            factory=list,
            max_size=50,
            reset_func=lambda x: x.clear()
        )
        
        # Dict pool
        self.object_pools['dict'] = ObjectPool(
            factory=dict,
            max_size=50,
            reset_func=lambda x: x.clear()
        )
    
    def get_pooled_object(self, object_type: str):
        """Get object from pool"""
        if object_type in self.object_pools:
            return self.object_pools[object_type].acquire()
        else:
            raise ValueError(f"No pool available for object type: {object_type}")
    
    def return_pooled_object(self, object_type: str, obj):
        """Return object to pool"""
        if object_type in self.object_pools:
            self.object_pools[object_type].release(obj)
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Comprehensive memory optimization"""
        # Take snapshot before optimization
        before_snapshot = self.tracker.take_snapshot()
        
        # Force garbage collection
        gc_result = self.gc_optimizer.force_gc_collection()
        
        # Optimize GC thresholds berdasarkan current memory usage
        if before_snapshot.process_memory_mb > 1000:
            pressure = "high"
        elif before_snapshot.process_memory_mb < 200:
            pressure = "low"
        else:
            pressure = "normal"
        
        self.gc_optimizer.optimize_gc_thresholds(pressure)
        
        # Take snapshot after optimization
        time.sleep(1)  # Allow some time untuk GC
        after_snapshot = self.tracker.take_snapshot()
        
        memory_saved = before_snapshot.process_memory_mb - after_snapshot.process_memory_mb
        objects_removed = before_snapshot.gc_objects - after_snapshot.gc_objects
        
        result = {
            'optimization_timestamp': time.time(),
            'memory_before_mb': round(before_snapshot.process_memory_mb, 2),
            'memory_after_mb': round(after_snapshot.process_memory_mb, 2),
            'memory_saved_mb': round(memory_saved, 2),
            'objects_before': before_snapshot.gc_objects,
            'objects_after': after_snapshot.gc_objects,
            'objects_removed': objects_removed,
            'gc_collections': gc_result['collections_by_generation'],
            'memory_pressure': pressure,
            'optimization_effective': memory_saved > 0 or objects_removed > 0
        }
        
        self.logger.info(f"Memory optimization completed: saved {memory_saved:.1f}MB, removed {objects_removed} objects")
        return result
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive memory optimization status"""
        memory_report = self.tracker.get_memory_report()
        gc_stats = self.gc_optimizer.get_gc_stats()
        
        # Object pool statistics
        pool_stats = {}
        for pool_name, pool in self.object_pools.items():
            pool_stats[pool_name] = pool.get_stats()
        
        return {
            'timestamp': time.time(),
            'memory_tracking': memory_report,
            'garbage_collection': gc_stats,
            'object_pools': pool_stats,
            'optimization_features': {
                'memory_tracking': True,
                'leak_detection': True,
                'gc_optimization': True,
                'object_pooling': True,
                'automatic_optimization': True
            }
        }

# Global instance
memory_optimizer = MemoryOptimizer()

def get_memory_optimizer():
    """Get global memory optimizer instance"""
    return memory_optimizer

logger.info("🧠 Memory Optimization Engine module initialized")