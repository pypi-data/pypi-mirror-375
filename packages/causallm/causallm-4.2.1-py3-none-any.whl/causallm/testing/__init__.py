"""
Extended Testing Infrastructure for CausalLLM

This module provides property-based testing, performance benchmarks,
and mutation testing capabilities for comprehensive test coverage.
"""

from .property_based import (
    CausalDataStrategy,
    CausalGraphStrategy,
    PropertyBasedTestCase,
    causal_hypothesis_test
)
from .benchmarks import (
    PerformanceBenchmark,
    BenchmarkSuite,
    benchmark_test
)
from .mutation import (
    MutationTestRunner,
    MutationTestConfig
)

__all__ = [
    'CausalDataStrategy',
    'CausalGraphStrategy', 
    'PropertyBasedTestCase',
    'causal_hypothesis_test',
    'PerformanceBenchmark',
    'BenchmarkSuite',
    'benchmark_test',
    'MutationTestRunner',
    'MutationTestConfig'
]