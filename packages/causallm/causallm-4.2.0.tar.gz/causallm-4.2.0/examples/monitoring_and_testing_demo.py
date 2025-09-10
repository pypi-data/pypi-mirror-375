#!/usr/bin/env python3
"""
CausalLLM Enhanced Monitoring and Testing Demo

This script demonstrates the new monitoring, observability, and testing features
added to CausalLLM, including metrics collection, health checks, performance
profiling, property-based testing, benchmarking, and mutation testing.
"""

import sys
import os
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime

# Add the parent directory to the Python path to import causallm
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from causallm import CausalLLM
    from causallm.monitoring import MetricsCollector, HealthChecker, PerformanceProfiler
    from causallm.monitoring.metrics import get_global_collector, configure_metrics
    from causallm.monitoring.health import get_global_health_checker
    from causallm.monitoring.profiler import get_global_profiler, profile, profile_block
    from causallm.testing import (
        CausalDataStrategy, PropertyBasedTestCase, PerformanceBenchmark,
        BenchmarkSuite, MutationTestRunner, MutationTestConfig
    )
    print("✅ Successfully imported all CausalLLM monitoring and testing components")
except ImportError as e:
    print(f"❌ Error importing CausalLLM components: {e}")
    print("Make sure you've installed the testing dependencies:")
    print("pip install -e .[testing]")
    sys.exit(1)


def generate_sample_data(n_rows: int = 1000, n_vars: int = 5) -> pd.DataFrame:
    """Generate sample data for testing."""
    np.random.seed(42)
    data = {}
    
    # Generate data with some causal relationships
    data['X1'] = np.random.normal(0, 1, n_rows)
    data['X2'] = 2 * data['X1'] + np.random.normal(0, 0.5, n_rows)
    data['X3'] = np.random.normal(0, 1, n_rows)
    data['X4'] = data['X1'] + data['X3'] + np.random.normal(0, 0.3, n_rows)
    data['Y'] = data['X2'] + data['X4'] + np.random.normal(0, 0.2, n_rows)
    
    # Add additional variables if needed
    for i in range(5, n_vars):
        data[f'X{i+1}'] = np.random.normal(0, 1, n_rows)
    
    return pd.DataFrame(data)


@profile(name="causal_discovery_demo")
def run_causal_discovery_with_profiling(data: pd.DataFrame, variables: dict):
    """Example function to demonstrate profiling of causal discovery."""
    # Simulate causal discovery work
    import time
    time.sleep(0.1)  # Simulate computation time
    
    # Mock result
    return {
        'edges': [('X1', 'X2'), ('X1', 'X4'), ('X3', 'X4'), ('X2', 'Y'), ('X4', 'Y')],
        'variables': list(variables.keys()),
        'method': 'PC Algorithm'
    }


def demo_metrics_collection():
    """Demonstrate metrics collection capabilities."""
    print("\n🔍 METRICS COLLECTION DEMO")
    print("=" * 50)
    
    # Configure metrics collection
    collector = configure_metrics(enabled=True, collection_interval=1.0)
    
    # Simulate some operations
    print("Recording metrics for various operations...")
    
    # Record causal discovery metrics
    collector.record_causal_discovery(
        variables_count=5,
        duration=2.5,
        method='PC',
        success=True
    )
    
    # Record LLM request metrics
    collector.record_llm_request(
        model='gpt-4',
        tokens_used=150,
        duration=1.2,
        success=True,
        cost=0.003
    )
    
    # Record data processing metrics
    collector.record_data_processing(
        rows_processed=1000,
        columns_processed=5,
        duration=0.5,
        operation='preprocessing'
    )
    
    # Get metrics summary
    summary = collector.get_metrics_summary()
    print(f"✅ Collected metrics for {len(summary['metrics']['counters'])} counter types")
    print(f"✅ System metrics: {len(summary['metrics']['gauges'])} gauge types")
    print(f"✅ Performance histograms: {len(summary['metrics']['histograms'])} histogram types")
    
    return collector


async def demo_health_checks():
    """Demonstrate health checking capabilities."""
    print("\n🏥 HEALTH CHECKS DEMO")
    print("=" * 50)
    
    # Configure health checker
    health_checker = get_global_health_checker()
    
    print("Running health checks...")
    
    # Run all health checks
    results = await health_checker.run_all_health_checks()
    
    print(f"✅ Completed {len(results)} health checks")
    
    # Get overall health status
    overall_health = health_checker.get_overall_health()
    print(f"📊 Overall health status: {overall_health['status']}")
    print(f"📝 Message: {overall_health['message']}")
    
    # Show individual check results
    for name, result in results.items():
        status_emoji = "✅" if result.status.value == "healthy" else "⚠️" if result.status.value == "degraded" else "❌"
        print(f"  {status_emoji} {name}: {result.status.value} ({result.duration_ms:.1f}ms)")
    
    return health_checker


def demo_performance_profiling():
    """Demonstrate performance profiling capabilities."""
    print("\n⚡ PERFORMANCE PROFILING DEMO")
    print("=" * 50)
    
    # Configure profiler
    profiler = get_global_profiler()
    
    # Generate test data
    data = generate_sample_data(1000, 5)
    variables = {f'X{i}': 'continuous' for i in range(1, 6)}
    variables['Y'] = 'continuous'
    
    print("Running profiled causal discovery...")
    
    # Run profiled function
    with profile_block("causal_discovery_full"):
        result = run_causal_discovery_with_profiling(data, variables)
    
    # Get profiling results
    summary = profiler.get_performance_summary()
    print(f"✅ Profiled {summary['summary']['total_calls']} function calls")
    print(f"📊 Average duration: {summary['summary']['avg_duration_ms']:.2f}ms")
    print(f"💾 Peak memory usage: {summary['summary']['max_memory_peak_mb']:.2f}MB")
    
    # Show function statistics
    print("\nFunction performance breakdown:")
    function_stats = profiler.get_function_stats()
    for func_name, stats in function_stats.items():
        print(f"  📋 {func_name}:")
        print(f"     Calls: {stats['total_calls']}")
        print(f"     Avg time: {stats['avg_time']*1000:.2f}ms")
        print(f"     Total time: {stats['total_time']*1000:.2f}ms")
    
    return profiler


def demo_property_based_testing():
    """Demonstrate property-based testing capabilities."""
    print("\n🧪 PROPERTY-BASED TESTING DEMO")
    print("=" * 50)
    
    from causallm.testing.property_based import CausalTestRunner
    
    # Mock conditional independence test function
    def mock_ci_test(data, x, y, conditioning_set):
        """Mock conditional independence test."""
        import numpy as np
        # Simple correlation-based test (not actually CI)
        corr = abs(data[x].corr(data[y]))
        p_value = max(0.01, 1 - corr)  # Mock p-value
        return corr < 0.1, p_value  # Independent if correlation is low
    
    # Mock causal discovery function
    def mock_causal_discovery(data):
        """Mock causal discovery function."""
        variables = list(data.columns)
        # Return some edges based on correlations
        edges = []
        for i, var1 in enumerate(variables):
            for var2 in variables[i+1:]:
                if abs(data[var1].corr(data[var2])) > 0.3:
                    edges.append((var1, var2))
        return edges[:3]  # Limit to 3 edges
    
    # Mock do-calculus function
    def mock_do_operator(data, treatment, outcome):
        """Mock do-calculus implementation."""
        # Simple difference in means (not actual causal effect)
        treatment_vals = data[treatment]
        outcome_vals = data[outcome]
        effect = outcome_vals.corr(treatment_vals) * outcome_vals.std()
        return {'effect': effect}
    
    # Create test runner
    test_runner = CausalTestRunner(max_examples=10, deadline=30000)
    
    print("Running property-based tests...")
    
    # Test conditional independence properties
    try:
        ci_results = test_runner.run_independence_tests(mock_ci_test)
        print(f"✅ CI test properties: {ci_results}")
    except Exception as e:
        print(f"⚠️ CI tests encountered issues: {e}")
    
    # Test causal discovery properties
    try:
        discovery_results = test_runner.run_discovery_tests(mock_causal_discovery)
        print(f"✅ Discovery test properties: {discovery_results}")
    except Exception as e:
        print(f"⚠️ Discovery tests encountered issues: {e}")
    
    # Test do-calculus properties
    try:
        do_results = test_runner.run_do_calculus_tests(mock_do_operator)
        print(f"✅ Do-calculus test properties: {do_results}")
    except Exception as e:
        print(f"⚠️ Do-calculus tests encountered issues: {e}")
    
    # Get test summary
    summary = test_runner.get_test_summary()
    print(f"📊 Property-based test summary:")
    print(f"   Total tests: {summary['total_tests']}")
    print(f"   Passed: {summary['passed_tests']}")
    print(f"   Pass rate: {summary['pass_rate']:.2%}")
    
    return test_runner


def demo_performance_benchmarks():
    """Demonstrate performance benchmarking capabilities."""
    print("\n🏁 PERFORMANCE BENCHMARKS DEMO")
    print("=" * 50)
    
    # Create benchmark suite
    benchmark_suite = BenchmarkSuite()
    
    # Mock algorithms for benchmarking
    def mock_pc_algorithm(data, variables):
        """Mock PC algorithm."""
        import time
        time.sleep(0.01 * len(variables))  # Simulate O(n) complexity
        return {'edges': [('X1', 'X2')], 'method': 'PC'}
    
    def mock_ges_algorithm(data, variables):
        """Mock GES algorithm."""
        import time
        time.sleep(0.02 * len(variables))  # Simulate O(n) complexity
        return {'edges': [('X1', 'X2'), ('X2', 'Y')], 'method': 'GES'}
    
    def mock_independence_test(data, x, y, z):
        """Mock independence test."""
        import time
        time.sleep(0.001 * len(data))  # Simulate O(n) complexity
        return True, 0.05
    
    # Define algorithms to benchmark
    algorithms = {
        'pc_discovery': mock_pc_algorithm,
        'ges_discovery': mock_ges_algorithm,
        'independence_test': mock_independence_test
    }
    
    print("Running performance benchmarks...")
    
    try:
        # Run causal benchmarks
        results = benchmark_suite.run_causal_benchmarks(algorithms)
        
        print("✅ Benchmark results:")
        for alg_name, result in results.items():
            if isinstance(result, dict) and 'error' not in result:
                if 'performance_stats' in result:
                    duration_stats = result['performance_stats']['duration']
                    print(f"  📊 {alg_name}:")
                    print(f"     Avg duration: {duration_stats['mean']:.4f}s")
                    print(f"     Min duration: {duration_stats['min']:.4f}s")
                    print(f"     Max duration: {duration_stats['max']:.4f}s")
                else:
                    print(f"  📊 {alg_name}: {result}")
            else:
                print(f"  ❌ {alg_name}: {result.get('error', 'Unknown error')}")
        
        # Show comparisons if available
        if 'comparisons' in results:
            print("\n🔍 Algorithm comparisons:")
            for comparison_name, comparison in results['comparisons'].items():
                if '_summary' in comparison:
                    summary = comparison['_summary']
                    print(f"  {comparison_name}:")
                    print(f"    Fastest: {summary['fastest_algorithm']} ({summary['fastest_avg_duration']:.4f}s)")
                    print(f"    Most memory efficient: {summary['most_memory_efficient']}")
    
    except Exception as e:
        print(f"⚠️ Benchmarking encountered issues: {e}")
    
    return benchmark_suite


def demo_mutation_testing():
    """Demonstrate mutation testing capabilities (simplified demo)."""
    print("\n🧬 MUTATION TESTING DEMO")
    print("=" * 50)
    
    print("Mutation testing demo - creating sample test scenario...")
    
    # Create a simple example file for mutation testing
    sample_code = '''
def simple_causal_function(x, y):
    """Simple function for mutation testing demo."""
    if x > 0:
        return x + y
    else:
        return x - y

def conditional_logic(a, b, c):
    """Function with conditional logic."""
    if a > b and b > c:
        return True
    elif a == b or b == c:
        return None
    else:
        return False
'''
    
    # Write sample file
    sample_file = '/tmp/sample_causal_code.py'
    with open(sample_file, 'w') as f:
        f.write(sample_code)
    
    # Create mutation test configuration
    config = MutationTestConfig(
        target_files=[sample_file],
        test_command="echo 'Mock test passed'",  # Mock test command
        timeout=10,
        max_mutations_per_file=5
    )
    
    print(f"✅ Created mutation test configuration for {len(config.target_files)} files")
    print(f"📝 Test command: {config.test_command}")
    print(f"⏱️ Timeout: {config.timeout} seconds")
    print(f"🔢 Max mutations per file: {config.max_mutations_per_file}")
    
    try:
        # Create mutation test runner
        runner = MutationTestRunner(config)
        
        print("\nNote: Full mutation testing requires a proper test suite.")
        print("This demo shows the configuration and structure.")
        
        print(f"✅ Mutation test runner configured with {len(runner.mutators)} mutator types:")
        for mutator in runner.mutators:
            print(f"   - {mutator.name}")
        
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)
            
    except Exception as e:
        print(f"⚠️ Mutation testing setup encountered issues: {e}")
    
    return config


async def main():
    """Run the complete monitoring and testing demo."""
    print("🚀 CausalLLM Enhanced Monitoring & Testing Demo")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Metrics Collection Demo
        metrics_collector = demo_metrics_collection()
        
        # Health Checks Demo
        health_checker = await demo_health_checks()
        
        # Performance Profiling Demo
        profiler = demo_performance_profiling()
        
        # Property-Based Testing Demo
        property_tester = demo_property_based_testing()
        
        # Performance Benchmarks Demo
        benchmark_suite = demo_performance_benchmarks()
        
        # Mutation Testing Demo
        mutation_config = demo_mutation_testing()
        
        print("\n✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nSummary of new features demonstrated:")
        print("🔍 Metrics Collection - Track performance and usage patterns")
        print("🏥 Health Checks - Monitor system and component health")
        print("⚡ Performance Profiling - Detailed performance analysis")
        print("🧪 Property-Based Testing - Automated property verification")
        print("🏁 Performance Benchmarks - Algorithm performance comparison")
        print("🧬 Mutation Testing - Test suite quality assessment")
        
        print("\n💡 Next steps:")
        print("1. Install testing dependencies: pip install -e .[testing]")
        print("2. Run property-based tests on your causal inference code")
        print("3. Set up monitoring in production environments")
        print("4. Use benchmarks to compare algorithm performance")
        print("5. Apply mutation testing to improve test coverage")
        
    except Exception as e:
        print(f"\n❌ Demo encountered an error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\n📅 Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())