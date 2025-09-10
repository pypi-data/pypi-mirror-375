"""
Performance Benchmarking System for CausalLLM

Provides comprehensive performance benchmarking capabilities for
measuring and comparing algorithm performance across different scenarios.
"""

import time
import gc
import functools
import statistics
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import pandas as pd
import numpy as np
import psutil
import json
from datetime import datetime
import tracemalloc
import pytest


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    name: str
    duration_seconds: float
    memory_peak_mb: float
    memory_delta_mb: float
    iterations: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'duration_seconds': self.duration_seconds,
            'memory_peak_mb': self.memory_peak_mb,
            'memory_delta_mb': self.memory_delta_mb,
            'iterations': self.iterations,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class BenchmarkStats:
    """Statistical analysis of benchmark results."""
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    percentile_95: float
    percentile_99: float
    count: int
    
    @classmethod
    def from_values(cls, values: List[float]) -> 'BenchmarkStats':
        """Create stats from a list of values."""
        if not values:
            return cls(0, 0, 0, 0, 0, 0, 0, 0)
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return cls(
            mean=statistics.mean(values),
            median=statistics.median(values),
            std_dev=statistics.stdev(values) if n > 1 else 0,
            min_value=min(values),
            max_value=max(values),
            percentile_95=sorted_values[int(n * 0.95)] if n > 0 else 0,
            percentile_99=sorted_values[int(n * 0.99)] if n > 0 else 0,
            count=n
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'mean': self.mean,
            'median': self.median,
            'std_dev': self.std_dev,
            'min': self.min_value,
            'max': self.max_value,
            'p95': self.percentile_95,
            'p99': self.percentile_99,
            'count': self.count
        }


class PerformanceBenchmark:
    """Class for running performance benchmarks."""
    
    def __init__(self, name: str, warmup_iterations: int = 3, 
                 benchmark_iterations: int = 10, track_memory: bool = True):
        self.name = name
        self.warmup_iterations = warmup_iterations
        self.benchmark_iterations = benchmark_iterations
        self.track_memory = track_memory
        self.results: List[BenchmarkResult] = []
    
    def run(self, func: Callable, *args, **kwargs) -> BenchmarkResult:
        """Run a single benchmark."""
        # Warmup runs
        for _ in range(self.warmup_iterations):
            try:
                func(*args, **kwargs)
                gc.collect()
            except Exception:
                pass  # Ignore warmup failures
        
        # Memory tracking setup
        if self.track_memory:
            if not tracemalloc.is_tracing():
                tracemalloc.start()
                started_tracemalloc = True
            else:
                started_tracemalloc = False
            
            memory_start = tracemalloc.get_traced_memory()
        else:
            memory_start = None
            started_tracemalloc = False
        
        # Actual benchmark runs
        durations = []
        for i in range(self.benchmark_iterations):
            gc.collect()  # Clean up before each iteration
            
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                result = None
                success = False
                print(f"Benchmark iteration {i+1} failed: {e}")
            
            end_time = time.perf_counter()
            duration = end_time - start_time
            durations.append(duration)
        
        # Memory tracking finalization
        memory_peak_mb = 0
        memory_delta_mb = 0
        if self.track_memory and memory_start:
            try:
                memory_current, memory_peak = tracemalloc.get_traced_memory()
                memory_start_current, _ = memory_start
                memory_peak_mb = memory_peak / (1024 * 1024)
                memory_delta_mb = (memory_current - memory_start_current) / (1024 * 1024)
            except Exception:
                pass  # Memory tracking failed
            
            if started_tracemalloc:
                tracemalloc.stop()
        
        # Calculate average duration
        avg_duration = statistics.mean(durations) if durations else 0
        
        benchmark_result = BenchmarkResult(
            name=self.name,
            duration_seconds=avg_duration,
            memory_peak_mb=memory_peak_mb,
            memory_delta_mb=memory_delta_mb,
            iterations=self.benchmark_iterations,
            timestamp=datetime.now(),
            metadata={
                'all_durations': durations,
                'warmup_iterations': self.warmup_iterations,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            }
        )
        
        self.results.append(benchmark_result)
        return benchmark_result
    
    def run_with_different_inputs(self, func: Callable, input_sets: List[Tuple]) -> List[BenchmarkResult]:
        """Run benchmarks with different input sets."""
        results = []
        for i, inputs in enumerate(input_sets):
            self.name = f"{self.name}_input_{i}"
            if isinstance(inputs, tuple) and len(inputs) == 2 and isinstance(inputs[1], dict):
                args, kwargs = inputs
                result = self.run(func, *args, **kwargs)
            else:
                result = self.run(func, *inputs)
            results.append(result)
        return results
    
    def get_stats(self) -> Dict[str, BenchmarkStats]:
        """Get statistical analysis of all benchmark results."""
        if not self.results:
            return {}
        
        durations = [r.duration_seconds for r in self.results]
        memory_peaks = [r.memory_peak_mb for r in self.results]
        memory_deltas = [r.memory_delta_mb for r in self.results]
        
        return {
            'duration': BenchmarkStats.from_values(durations),
            'memory_peak': BenchmarkStats.from_values(memory_peaks),
            'memory_delta': BenchmarkStats.from_values(memory_deltas)
        }


class CausalBenchmarkSuite:
    """Benchmark suite specifically for causal inference algorithms."""
    
    def __init__(self, data_sizes: List[int] = None, variable_counts: List[int] = None):
        self.data_sizes = data_sizes or [100, 500, 1000, 5000]
        self.variable_counts = variable_counts or [3, 5, 10, 15]
        self.results: Dict[str, List[BenchmarkResult]] = defaultdict(list)
    
    def generate_test_data(self, n_rows: int, n_vars: int) -> pd.DataFrame:
        """Generate synthetic data for benchmarking."""
        return pd.DataFrame({
            f'var_{i}': np.random.normal(0, 1, n_rows)
            for i in range(n_vars)
        })
    
    def benchmark_causal_discovery(self, discovery_func: Callable, 
                                 algorithm_name: str) -> Dict[str, Any]:
        """Benchmark causal discovery algorithms."""
        results = []
        
        for n_vars in self.variable_counts:
            for n_rows in self.data_sizes:
                if n_rows < n_vars * 10:  # Skip if insufficient data
                    continue
                
                data = self.generate_test_data(n_rows, n_vars)
                variables = {f'var_{i}': 'continuous' for i in range(n_vars)}
                
                benchmark_name = f"{algorithm_name}_v{n_vars}_r{n_rows}"
                benchmark = PerformanceBenchmark(
                    name=benchmark_name,
                    warmup_iterations=1,
                    benchmark_iterations=3  # Fewer iterations for expensive algorithms
                )
                
                try:
                    result = benchmark.run(discovery_func, data, variables)
                    result.metadata.update({
                        'n_variables': n_vars,
                        'n_rows': n_rows,
                        'algorithm': algorithm_name
                    })
                    results.append(result)
                    self.results[algorithm_name].append(result)
                except Exception as e:
                    print(f"Benchmark failed for {benchmark_name}: {e}")
        
        return self._analyze_results(results, algorithm_name)
    
    def benchmark_statistical_tests(self, test_func: Callable, 
                                  test_name: str) -> Dict[str, Any]:
        """Benchmark statistical test functions."""
        results = []
        
        for n_rows in self.data_sizes:
            data = self.generate_test_data(n_rows, 4)  # Fixed 4 variables for CI tests
            
            benchmark_name = f"{test_name}_r{n_rows}"
            benchmark = PerformanceBenchmark(
                name=benchmark_name,
                benchmark_iterations=10
            )
            
            try:
                result = benchmark.run(test_func, data, 'var_0', 'var_1', ['var_2'])
                result.metadata.update({
                    'n_rows': n_rows,
                    'test_name': test_name
                })
                results.append(result)
                self.results[test_name].append(result)
            except Exception as e:
                print(f"Benchmark failed for {benchmark_name}: {e}")
        
        return self._analyze_results(results, test_name)
    
    def benchmark_do_calculus(self, do_func: Callable, 
                            method_name: str) -> Dict[str, Any]:
        """Benchmark do-calculus implementations."""
        results = []
        
        for n_rows in self.data_sizes:
            data = self.generate_test_data(n_rows, 5)
            
            benchmark_name = f"{method_name}_r{n_rows}"
            benchmark = PerformanceBenchmark(
                name=benchmark_name,
                benchmark_iterations=5
            )
            
            try:
                result = benchmark.run(do_func, data, 'var_0', 'var_1')
                result.metadata.update({
                    'n_rows': n_rows,
                    'method': method_name
                })
                results.append(result)
                self.results[method_name].append(result)
            except Exception as e:
                print(f"Benchmark failed for {benchmark_name}: {e}")
        
        return self._analyze_results(results, method_name)
    
    def _analyze_results(self, results: List[BenchmarkResult], 
                        algorithm_name: str) -> Dict[str, Any]:
        """Analyze benchmark results."""
        if not results:
            return {'error': f'No successful benchmarks for {algorithm_name}'}
        
        durations = [r.duration_seconds for r in results]
        memory_usage = [r.memory_peak_mb for r in results]
        
        # Performance scaling analysis
        scaling_analysis = self._analyze_scaling(results)
        
        return {
            'algorithm': algorithm_name,
            'total_benchmarks': len(results),
            'performance_stats': {
                'duration': BenchmarkStats.from_values(durations).to_dict(),
                'memory_peak': BenchmarkStats.from_values(memory_usage).to_dict()
            },
            'scaling_analysis': scaling_analysis,
            'fastest_config': min(results, key=lambda r: r.duration_seconds).metadata,
            'most_memory_efficient': min(results, key=lambda r: r.memory_peak_mb).metadata
        }
    
    def _analyze_scaling(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Analyze how performance scales with data size."""
        scaling_data = defaultdict(list)
        
        for result in results:
            n_rows = result.metadata.get('n_rows', 0)
            n_vars = result.metadata.get('n_variables', 0)
            
            if n_rows > 0:
                scaling_data['by_rows'].append((n_rows, result.duration_seconds))
            if n_vars > 0:
                scaling_data['by_variables'].append((n_vars, result.duration_seconds))
        
        analysis = {}
        
        # Analyze scaling by number of rows
        if scaling_data['by_rows']:
            row_data = sorted(scaling_data['by_rows'])
            analysis['row_scaling'] = {
                'data_points': len(row_data),
                'min_time_at_size': {
                    'size': row_data[0][0],
                    'time': row_data[0][1]
                },
                'max_time_at_size': {
                    'size': row_data[-1][0], 
                    'time': row_data[-1][1]
                }
            }
        
        # Analyze scaling by number of variables
        if scaling_data['by_variables']:
            var_data = sorted(scaling_data['by_variables'])
            analysis['variable_scaling'] = {
                'data_points': len(var_data),
                'min_time_at_size': {
                    'size': var_data[0][0],
                    'time': var_data[0][1]
                },
                'max_time_at_size': {
                    'size': var_data[-1][0],
                    'time': var_data[-1][1]
                }
            }
        
        return analysis
    
    def compare_algorithms(self, results_dict: Dict[str, List[BenchmarkResult]]) -> Dict[str, Any]:
        """Compare performance of different algorithms."""
        if not results_dict or len(results_dict) < 2:
            return {'error': 'Need at least 2 algorithms to compare'}
        
        comparison = {}
        
        # Compare average performance
        for alg_name, results in results_dict.items():
            if results:
                avg_duration = statistics.mean([r.duration_seconds for r in results])
                avg_memory = statistics.mean([r.memory_peak_mb for r in results])
                
                comparison[alg_name] = {
                    'avg_duration_seconds': avg_duration,
                    'avg_memory_peak_mb': avg_memory,
                    'total_benchmarks': len(results)
                }
        
        # Find fastest and most memory efficient
        if comparison:
            fastest = min(comparison.items(), key=lambda x: x[1]['avg_duration_seconds'])
            most_efficient = min(comparison.items(), key=lambda x: x[1]['avg_memory_peak_mb'])
            
            comparison['_summary'] = {
                'fastest_algorithm': fastest[0],
                'fastest_avg_duration': fastest[1]['avg_duration_seconds'],
                'most_memory_efficient': most_efficient[0],
                'most_efficient_memory': most_efficient[1]['avg_memory_peak_mb']
            }
        
        return comparison
    
    def export_results(self, filepath: str, format: str = 'json') -> None:
        """Export benchmark results to file."""
        export_data = {
            'benchmark_suite': 'CausalBenchmarkSuite',
            'export_timestamp': datetime.now().isoformat(),
            'data_sizes_tested': self.data_sizes,
            'variable_counts_tested': self.variable_counts,
            'results': {
                name: [result.to_dict() for result in results]
                for name, results in self.results.items()
            }
        }
        
        if format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")


class BenchmarkSuite:
    """General purpose benchmark suite."""
    
    def __init__(self):
        self.benchmarks: Dict[str, PerformanceBenchmark] = {}
        self.causal_suite = CausalBenchmarkSuite()
    
    def add_benchmark(self, name: str, func: Callable, *args, 
                     warmup_iterations: int = 3,
                     benchmark_iterations: int = 10, **kwargs) -> BenchmarkResult:
        """Add and run a benchmark."""
        benchmark = PerformanceBenchmark(
            name=name,
            warmup_iterations=warmup_iterations,
            benchmark_iterations=benchmark_iterations
        )
        
        result = benchmark.run(func, *args, **kwargs)
        self.benchmarks[name] = benchmark
        return result
    
    def run_causal_benchmarks(self, algorithms: Dict[str, Callable]) -> Dict[str, Any]:
        """Run comprehensive causal inference benchmarks."""
        all_results = {}
        
        for alg_name, alg_func in algorithms.items():
            try:
                if 'discovery' in alg_name.lower():
                    result = self.causal_suite.benchmark_causal_discovery(alg_func, alg_name)
                elif 'test' in alg_name.lower() or 'independence' in alg_name.lower():
                    result = self.causal_suite.benchmark_statistical_tests(alg_func, alg_name)
                elif 'do' in alg_name.lower() or 'causal_effect' in alg_name.lower():
                    result = self.causal_suite.benchmark_do_calculus(alg_func, alg_name)
                else:
                    # Generic benchmark
                    benchmark = PerformanceBenchmark(alg_name)
                    data = self.causal_suite.generate_test_data(1000, 5)
                    result = benchmark.run(alg_func, data)
                
                all_results[alg_name] = result
            except Exception as e:
                all_results[alg_name] = {'error': str(e)}
        
        # Add comparison analysis
        comparison_results = {}
        for category in ['discovery', 'test', 'do']:
            category_results = {
                name: self.causal_suite.results[name]
                for name in self.causal_suite.results
                if category in name.lower()
            }
            if len(category_results) >= 2:
                comparison_results[f'{category}_comparison'] = self.causal_suite.compare_algorithms(category_results)
        
        all_results['comparisons'] = comparison_results
        return all_results


def benchmark_test(warmup: int = 3, iterations: int = 10, track_memory: bool = True):
    """Decorator for creating benchmark tests."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            benchmark = PerformanceBenchmark(
                name=func.__name__,
                warmup_iterations=warmup,
                benchmark_iterations=iterations,
                track_memory=track_memory
            )
            
            def test_func():
                return func(*args, **kwargs)
            
            result = benchmark.run(test_func)
            
            # Add result to global benchmark results if running under pytest
            if hasattr(pytest, 'benchmark_results'):
                pytest.benchmark_results.append(result)
            
            return result
        
        return wrapper
    return decorator