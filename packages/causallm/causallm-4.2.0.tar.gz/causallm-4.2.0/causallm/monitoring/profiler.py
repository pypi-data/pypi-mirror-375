"""
Performance Profiling System for CausalLLM

Provides comprehensive performance profiling capabilities including
execution timing, memory usage tracking, and statistical analysis.
"""

import time
import cProfile
import pstats
import tracemalloc
import threading
import functools
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
from collections import defaultdict
import gc
import psutil
import json
from datetime import datetime
import io


@dataclass
class ProfileResult:
    """Result of a performance profiling session."""
    name: str
    duration_ms: float
    memory_peak_mb: float
    memory_delta_mb: float
    cpu_percent: float
    timestamp: datetime
    call_count: int = 0
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'duration_ms': self.duration_ms,
            'memory_peak_mb': self.memory_peak_mb,
            'memory_delta_mb': self.memory_delta_mb,
            'cpu_percent': self.cpu_percent,
            'call_count': self.call_count,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }


@dataclass
class FunctionStats:
    """Statistics for a profiled function."""
    total_calls: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    last_call: Optional[datetime] = None
    
    def update(self, duration: float) -> None:
        """Update statistics with a new call."""
        self.total_calls += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.avg_time = self.total_time / self.total_calls
        self.last_call = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_calls': self.total_calls,
            'total_time': self.total_time,
            'min_time': self.min_time if self.min_time != float('inf') else 0,
            'max_time': self.max_time,
            'avg_time': self.avg_time,
            'last_call': self.last_call.isoformat() if self.last_call else None
        }


class PerformanceProfiler:
    """Main performance profiling system for CausalLLM."""
    
    def __init__(self, enabled: bool = True, detailed_profiling: bool = False):
        self.enabled = enabled
        self.detailed_profiling = detailed_profiling
        self.function_stats: Dict[str, FunctionStats] = defaultdict(FunctionStats)
        self.profile_results: List[ProfileResult] = []
        self._lock = threading.RLock()
        self._profiling_sessions: Dict[str, Dict[str, Any]] = {}
        
        if self.enabled and self.detailed_profiling:
            tracemalloc.start()
    
    @contextmanager
    def profile_context(self, name: str, track_memory: bool = True, 
                       track_cpu: bool = True, **metadata):
        """Context manager for profiling a block of code."""
        if not self.enabled:
            yield
            return
        
        session_id = f"{name}_{int(time.time() * 1000000)}"
        start_time = time.time()
        
        # Memory tracking setup
        memory_start = None
        if track_memory and tracemalloc.is_tracing():
            memory_start = tracemalloc.get_traced_memory()
        elif track_memory:
            tracemalloc.start()
            memory_start = tracemalloc.get_traced_memory()
        
        # CPU tracking setup  
        process = psutil.Process() if track_cpu else None
        cpu_start = process.cpu_percent() if process else 0
        
        # Store session info
        with self._lock:
            self._profiling_sessions[session_id] = {
                'name': name,
                'start_time': start_time,
                'memory_start': memory_start,
                'cpu_start': cpu_start,
                'metadata': metadata
            }
        
        try:
            yield session_id
        finally:
            self._finalize_profile_session(session_id, track_memory, track_cpu)
    
    def _finalize_profile_session(self, session_id: str, track_memory: bool, track_cpu: bool):
        """Finalize a profiling session and record results."""
        with self._lock:
            session = self._profiling_sessions.pop(session_id, None)
            if not session:
                return
            
            end_time = time.time()
            duration_ms = (end_time - session['start_time']) * 1000
            
            # Memory tracking
            memory_peak_mb = 0
            memory_delta_mb = 0
            if track_memory and session['memory_start']:
                try:
                    memory_current, memory_peak = tracemalloc.get_traced_memory()
                    memory_start_current, _ = session['memory_start']
                    memory_peak_mb = memory_peak / (1024 * 1024)
                    memory_delta_mb = (memory_current - memory_start_current) / (1024 * 1024)
                except Exception:
                    pass  # Memory tracking failed
            
            # CPU tracking
            cpu_percent = 0
            if track_cpu:
                try:
                    process = psutil.Process()
                    cpu_percent = process.cpu_percent()
                except Exception:
                    pass  # CPU tracking failed
            
            # Create profile result
            result = ProfileResult(
                name=session['name'],
                duration_ms=duration_ms,
                memory_peak_mb=memory_peak_mb,
                memory_delta_mb=memory_delta_mb,
                cpu_percent=cpu_percent,
                timestamp=datetime.now(),
                call_count=1,
                details=session['metadata']
            )
            
            self.profile_results.append(result)
            
            # Update function stats
            self.function_stats[session['name']].update(duration_ms / 1000)
    
    def profile_function(self, name: Optional[str] = None, track_memory: bool = True,
                        track_cpu: bool = True, **metadata):
        """Decorator for profiling functions."""
        def decorator(func: Callable) -> Callable:
            func_name = name or f"{func.__module__}.{func.__name__}"
            
            if not self.enabled:
                return func
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self.profile_context(func_name, track_memory, track_cpu, **metadata):
                    return func(*args, **kwargs)
            
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.profile_context(func_name, track_memory, track_cpu, **metadata):
                    return await func(*args, **kwargs)
            
            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def profile_detailed(self, name: str, sort_by: str = 'cumtime', top_n: int = 20) -> Dict[str, Any]:
        """Perform detailed profiling using cProfile."""
        if not self.enabled:
            return {}
        
        profiler = cProfile.Profile()
        
        def run_with_profiler(func_to_profile):
            profiler.enable()
            try:
                result = func_to_profile()
                return result
            finally:
                profiler.disable()
        
        # This is a context for detailed profiling
        # The actual function to profile would be passed to run_with_profiler
        
        # Convert profile results to string
        string_io = io.StringIO()
        stats = pstats.Stats(profiler, stream=string_io)
        stats.sort_stats(sort_by)
        stats.print_stats(top_n)
        
        profile_output = string_io.getvalue()
        
        return {
            'name': name,
            'profile_output': profile_output,
            'timestamp': datetime.now().isoformat(),
            'sort_by': sort_by,
            'top_n': top_n
        }
    
    def get_function_stats(self, function_name: Optional[str] = None) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """Get function performance statistics."""
        with self._lock:
            if function_name:
                stats = self.function_stats.get(function_name)
                return stats.to_dict() if stats else {}
            else:
                return {name: stats.to_dict() for name, stats in self.function_stats.items()}
    
    def get_performance_summary(self, last_n_results: Optional[int] = None) -> Dict[str, Any]:
        """Get a summary of performance profiling results."""
        with self._lock:
            results = self.profile_results[-last_n_results:] if last_n_results else self.profile_results
            
            if not results:
                return {'summary': 'No profiling results available'}
            
            # Calculate summary statistics
            total_calls = len(results)
            total_duration = sum(r.duration_ms for r in results)
            avg_duration = total_duration / total_calls if total_calls > 0 else 0
            max_duration = max((r.duration_ms for r in results), default=0)
            min_duration = min((r.duration_ms for r in results), default=0)
            
            total_memory_delta = sum(r.memory_delta_mb for r in results)
            avg_memory_peak = sum(r.memory_peak_mb for r in results) / total_calls if total_calls > 0 else 0
            max_memory_peak = max((r.memory_peak_mb for r in results), default=0)
            
            # Group by function name
            by_function = defaultdict(list)
            for result in results:
                by_function[result.name].append(result)
            
            function_summaries = {}
            for func_name, func_results in by_function.items():
                func_calls = len(func_results)
                func_total_duration = sum(r.duration_ms for r in func_results)
                func_avg_duration = func_total_duration / func_calls
                
                function_summaries[func_name] = {
                    'call_count': func_calls,
                    'total_duration_ms': func_total_duration,
                    'avg_duration_ms': func_avg_duration,
                    'max_duration_ms': max(r.duration_ms for r in func_results),
                    'min_duration_ms': min(r.duration_ms for r in func_results),
                    'avg_memory_peak_mb': sum(r.memory_peak_mb for r in func_results) / func_calls,
                    'total_memory_delta_mb': sum(r.memory_delta_mb for r in func_results)
                }
            
            return {
                'summary': {
                    'total_calls': total_calls,
                    'total_duration_ms': total_duration,
                    'avg_duration_ms': avg_duration,
                    'max_duration_ms': max_duration,
                    'min_duration_ms': min_duration,
                    'total_memory_delta_mb': total_memory_delta,
                    'avg_memory_peak_mb': avg_memory_peak,
                    'max_memory_peak_mb': max_memory_peak
                },
                'by_function': function_summaries,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_slowest_operations(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get the slowest operations."""
        with self._lock:
            sorted_results = sorted(self.profile_results, key=lambda r: r.duration_ms, reverse=True)
            return [result.to_dict() for result in sorted_results[:top_n]]
    
    def get_memory_intensive_operations(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get the most memory-intensive operations."""
        with self._lock:
            sorted_results = sorted(self.profile_results, key=lambda r: r.memory_peak_mb, reverse=True)
            return [result.to_dict() for result in sorted_results[:top_n]]
    
    def export_profile_data(self, filepath: str, format: str = 'json') -> None:
        """Export profiling data to a file."""
        data = {
            'summary': self.get_performance_summary(),
            'function_stats': self.get_function_stats(),
            'all_results': [result.to_dict() for result in self.profile_results],
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def clear_results(self) -> None:
        """Clear all profiling results."""
        with self._lock:
            self.profile_results.clear()
            self.function_stats.clear()
    
    def enable_detailed_profiling(self) -> None:
        """Enable detailed memory profiling."""
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        self.detailed_profiling = True
    
    def disable_detailed_profiling(self) -> None:
        """Disable detailed memory profiling."""
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        self.detailed_profiling = False


class MemoryProfiler:
    """Specialized memory profiling utilities."""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage statistics."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / (1024 * 1024),  # Resident Set Size
            'vms_mb': memory_info.vms / (1024 * 1024),  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / (1024 * 1024)
        }
    
    @staticmethod
    def get_memory_snapshot() -> Optional[Dict[str, Any]]:
        """Get a memory snapshot if tracemalloc is active."""
        if not tracemalloc.is_tracing():
            return None
        
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        return {
            'total_memory_mb': sum(stat.size for stat in top_stats) / (1024 * 1024),
            'top_allocations': [
                {
                    'filename': stat.traceback.format()[0],
                    'size_mb': stat.size / (1024 * 1024),
                    'count': stat.count
                }
                for stat in top_stats[:10]
            ],
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    @contextmanager
    def track_memory_diff():
        """Track memory allocation differences in a context."""
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            started_here = True
        else:
            started_here = False
        
        snapshot1 = tracemalloc.take_snapshot()
        yield
        snapshot2 = tracemalloc.take_snapshot()
        
        if started_here:
            tracemalloc.stop()
        
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        return {
            'memory_diff_mb': sum(stat.size_diff for stat in top_stats) / (1024 * 1024),
            'top_changes': [
                {
                    'filename': stat.traceback.format()[0],
                    'size_diff_mb': stat.size_diff / (1024 * 1024),
                    'count_diff': stat.count_diff
                }
                for stat in top_stats[:10] if stat.size_diff > 0
            ]
        }


# Global profiler instance
_global_profiler: Optional[PerformanceProfiler] = None


def get_global_profiler() -> PerformanceProfiler:
    """Get the global performance profiler instance."""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()
    return _global_profiler


def configure_profiler(enabled: bool = True, detailed_profiling: bool = False) -> PerformanceProfiler:
    """Configure the global performance profiler."""
    global _global_profiler
    _global_profiler = PerformanceProfiler(enabled=enabled, detailed_profiling=detailed_profiling)
    return _global_profiler


# Convenience decorators using global profiler
def profile(name: Optional[str] = None, **kwargs):
    """Decorator for profiling functions using the global profiler."""
    return get_global_profiler().profile_function(name, **kwargs)


@contextmanager
def profile_block(name: str, **kwargs):
    """Context manager for profiling code blocks using the global profiler."""
    with get_global_profiler().profile_context(name, **kwargs):
        yield