"""
Metrics Collection System for CausalLLM

Provides comprehensive metrics collection for monitoring performance,
usage patterns, and system behavior.
"""

import time
import threading
import psutil
from collections import defaultdict, deque
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class MetricValue:
    """Represents a single metric value with metadata."""
    value: Any
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value,
            'timestamp': self.timestamp,
            'tags': self.tags
        }


class MetricsRegistry:
    """Thread-safe registry for storing and managing metrics."""
    
    def __init__(self, max_history: int = 1000):
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self._lock = threading.RLock()
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        
    def record_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a counter metric."""
        with self._lock:
            self._counters[name] += value
            self._metrics[name].append(MetricValue(value, tags=tags or {}))
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value."""
        with self._lock:
            self._gauges[name] = value
            self._metrics[name].append(MetricValue(value, tags=tags or {}))
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram metric."""
        with self._lock:
            self._histograms[name].append(value)
            self._metrics[name].append(MetricValue(value, tags=tags or {}))
    
    def get_counter(self, name: str) -> float:
        """Get current counter value."""
        with self._lock:
            return self._counters[name]
    
    def get_gauge(self, name: str) -> float:
        """Get current gauge value."""
        with self._lock:
            return self._gauges[name]
    
    def get_histogram_stats(self, name: str) -> Dict[str, float]:
        """Get histogram statistics."""
        with self._lock:
            values = self._histograms[name]
            if not values:
                return {}
            
            sorted_values = sorted(values)
            n = len(sorted_values)
            
            return {
                'count': n,
                'min': min(sorted_values),
                'max': max(sorted_values),
                'mean': sum(sorted_values) / n,
                'median': sorted_values[n // 2],
                'p95': sorted_values[int(n * 0.95)] if n > 0 else 0,
                'p99': sorted_values[int(n * 0.99)] if n > 0 else 0
            }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as a dictionary."""
        with self._lock:
            return {
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'histograms': {name: self.get_histogram_stats(name) 
                             for name in self._histograms}
            }
    
    def clear(self) -> None:
        """Clear all metrics."""
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


class MetricsCollector:
    """Main metrics collection system for CausalLLM."""
    
    def __init__(self, enabled: bool = True, collection_interval: float = 5.0):
        self.enabled = enabled
        self.collection_interval = collection_interval
        self.registry = MetricsRegistry()
        self._system_metrics_thread: Optional[threading.Thread] = None
        self._shutdown = threading.Event()
        
        if self.enabled:
            self._start_system_metrics_collection()
    
    def _start_system_metrics_collection(self) -> None:
        """Start background thread for system metrics collection."""
        self._system_metrics_thread = threading.Thread(
            target=self._collect_system_metrics,
            daemon=True
        )
        self._system_metrics_thread.start()
    
    def _collect_system_metrics(self) -> None:
        """Collect system-level metrics periodically."""
        while not self._shutdown.is_set():
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                self.registry.set_gauge('system.cpu.percent', cpu_percent)
                
                # Memory metrics
                memory = psutil.virtual_memory()
                self.registry.set_gauge('system.memory.percent', memory.percent)
                self.registry.set_gauge('system.memory.used_bytes', memory.used)
                self.registry.set_gauge('system.memory.available_bytes', memory.available)
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                self.registry.set_gauge('system.disk.percent', (disk.used / disk.total) * 100)
                self.registry.set_gauge('system.disk.used_bytes', disk.used)
                self.registry.set_gauge('system.disk.free_bytes', disk.free)
                
            except Exception as e:
                # Silently continue on errors to avoid disrupting the main application
                pass
            
            self._shutdown.wait(self.collection_interval)
    
    def record_operation_start(self, operation: str, **tags) -> str:
        """Record the start of an operation and return a correlation ID."""
        correlation_id = f"{operation}_{int(time.time() * 1000000)}"
        self.registry.record_counter(f'operations.{operation}.started', 1.0, tags)
        return correlation_id
    
    def record_operation_end(self, operation: str, correlation_id: str, 
                           success: bool = True, duration: Optional[float] = None, **tags) -> None:
        """Record the end of an operation."""
        if success:
            self.registry.record_counter(f'operations.{operation}.success', 1.0, tags)
        else:
            self.registry.record_counter(f'operations.{operation}.failure', 1.0, tags)
        
        if duration is not None:
            self.registry.record_histogram(f'operations.{operation}.duration', duration, tags)
    
    def record_causal_discovery(self, variables_count: int, duration: float, 
                              method: str, success: bool = True) -> None:
        """Record causal discovery metrics."""
        tags = {'method': method}
        
        self.registry.record_counter('causal_discovery.requests', 1.0, tags)
        self.registry.record_histogram('causal_discovery.duration', duration, tags)
        self.registry.record_histogram('causal_discovery.variables_count', variables_count, tags)
        
        if success:
            self.registry.record_counter('causal_discovery.success', 1.0, tags)
        else:
            self.registry.record_counter('causal_discovery.failure', 1.0, tags)
    
    def record_llm_request(self, model: str, tokens_used: int, duration: float,
                          success: bool = True, cost: Optional[float] = None) -> None:
        """Record LLM API request metrics."""
        tags = {'model': model}
        
        self.registry.record_counter('llm.requests', 1.0, tags)
        self.registry.record_histogram('llm.duration', duration, tags)
        self.registry.record_histogram('llm.tokens_used', tokens_used, tags)
        
        if cost is not None:
            self.registry.record_histogram('llm.cost', cost, tags)
        
        if success:
            self.registry.record_counter('llm.success', 1.0, tags)
        else:
            self.registry.record_counter('llm.failure', 1.0, tags)
    
    def record_data_processing(self, rows_processed: int, columns_processed: int,
                             duration: float, operation: str) -> None:
        """Record data processing metrics."""
        tags = {'operation': operation}
        
        self.registry.record_histogram('data_processing.rows', rows_processed, tags)
        self.registry.record_histogram('data_processing.columns', columns_processed, tags)
        self.registry.record_histogram('data_processing.duration', duration, tags)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics."""
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.registry.get_all_metrics()
        }
    
    def export_metrics_json(self, filepath: str) -> None:
        """Export metrics to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.get_metrics_summary(), f, indent=2)
    
    def shutdown(self) -> None:
        """Shutdown the metrics collector."""
        self._shutdown.set()
        if self._system_metrics_thread and self._system_metrics_thread.is_alive():
            self._system_metrics_thread.join(timeout=5.0)


# Decorator for automatic operation tracking
def track_operation(collector: MetricsCollector, operation_name: str, **tags):
    """Decorator to automatically track operation metrics."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            if not collector.enabled:
                return func(*args, **kwargs)
            
            correlation_id = collector.record_operation_start(operation_name, **tags)
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                collector.record_operation_end(operation_name, correlation_id, 
                                             success=True, duration=duration, **tags)
                return result
            except Exception as e:
                duration = time.time() - start_time
                collector.record_operation_end(operation_name, correlation_id,
                                             success=False, duration=duration, **tags)
                raise
        
        return wrapper
    return decorator


# Global metrics collector instance
_global_collector: Optional[MetricsCollector] = None


def get_global_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


def configure_metrics(enabled: bool = True, collection_interval: float = 5.0) -> MetricsCollector:
    """Configure the global metrics collector."""
    global _global_collector
    if _global_collector is not None:
        _global_collector.shutdown()
    
    _global_collector = MetricsCollector(enabled=enabled, collection_interval=collection_interval)
    return _global_collector