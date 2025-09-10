# CausalLLM: High-Performance Causal Inference Library

[![Custom License](https://img.shields.io/badge/License-Custom-red.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/causallm.svg)](https://badge.fury.io/py/causallm)
[![GitHub stars](https://img.shields.io/github/stars/rdmurugan/causallm.svg)](https://github.com/rdmurugan/causallm/stargazers)
[![Downloads](https://img.shields.io/pypi/dm/causallm.svg)](https://pypi.org/project/causallm/)

**CausalLLM** is a powerful Python library that combines statistical causal inference methods with advanced language models to discover causal relationships and estimate treatment effects. It provides enterprise-grade performance with 10x faster computations and 80% memory reduction while maintaining statistical rigor.

## 🆕 **New in v4.2.0: Enterprise-Grade Monitoring & Testing!**

**Production-Ready Causal Inference!** CausalLLM now includes comprehensive monitoring, observability, and advanced testing capabilities:

### 🔍 **Monitoring & Observability**
- **📊 Metrics Collection**: Track performance, usage patterns, and system health
- **🏥 Health Checks**: Monitor components, dependencies, and operational status  
- **⚡ Performance Profiling**: Detailed memory usage and execution timing analysis

### 🧪 **Extended Testing Framework**
- **🎲 Property-Based Testing**: Automated property verification with Hypothesis
- **🏁 Performance Benchmarks**: Algorithm comparison and scaling analysis
- **🧬 Mutation Testing**: Assess test suite quality and coverage gaps

### 🚀 **Legacy Features (v4.1.0)**
- 🖥️ **Command Line Interface**: Run causal analysis directly from your terminal
- 🌐 **Interactive Web Interface**: Point-and-click analysis with Streamlit
- 🐍 **Python Library**: Full programmatic control (as before)

---

## 🚀 Performance Highlights

- **10x Faster Computations**: Vectorized algorithms with Numba JIT compilation
- **80% Memory Reduction**: Intelligent data chunking and lazy evaluation  
- **Unlimited Scale**: Handle datasets with millions of rows through streaming processing
- **Smart Caching**: 80%+ cache hit rates for repeated analyses
- **Parallel Processing**: Async computations with automatic resource management
- **Zero Configuration**: Performance optimizations work automatically

---

## 📋 Table of Contents

1. [Quick Start - CLI & Web](#-quick-start---cli--web) ⭐ **New**
2. [Quick Start - Python](#-quick-start---python)
3. [Installation](#-installation)
4. [Key Features](#-key-features)
5. [Domain Examples](#-domain-examples)
6. [Core Components](#-core-components)
7. [Performance](#-performance)
8. [API Documentation](#-api-documentation)
9. [Advanced Features](#-advanced-features)
10. [Support & Community](#-support--community)

---

## 🚀 Quick Start - CLI & Web

### 🖥️ Command Line Interface

**Perfect for data scientists and analysts who prefer terminal-based workflows:**

```bash
# Install CausalLLM
pip install causallm

# Discover causal relationships
causallm discover --data healthcare_data.csv \
                  --variables "age,treatment,outcome" \
                  --domain healthcare \
                  --output results.json

# Estimate treatment effects
causallm effect --data experiment.csv \
                --treatment drug \
                --outcome recovery \
                --confounders "age,gender" \
                --output effects.json

# Generate counterfactual scenarios
causallm counterfactual --data patient_data.csv \
                       --intervention "treatment=1" \
                       --samples 200 \
                       --output scenarios.json

# Get help and examples
causallm info --examples
```

**CLI Features:**
- 🔍 **Causal Discovery**: Find relationships in your data automatically
- ⚡ **Effect Estimation**: Quantify treatment impacts with confidence intervals
- 🔮 **Counterfactual Analysis**: Generate "what-if" scenarios
- 📊 **Multiple Formats**: Support for CSV, JSON input/output
- 🏥 **Domain Context**: Healthcare, marketing, education, insurance
- 📖 **Built-in Help**: Examples and documentation at your fingertips

### 🌐 Interactive Web Interface

**Perfect for business users, researchers, and anyone who prefers point-and-click analysis:**

```bash
# Install with web interface
pip install "causallm[ui]"

# Launch interactive web interface
causallm web --port 8080

# Open browser to http://localhost:8080
```

**Web Interface Features:**
- 📁 **Drag & Drop Data**: Upload CSV/JSON files or use sample datasets
- 🎯 **Visual Analysis**: Interactive graphs and visualizations
- 📊 **Real-time Results**: See analysis results as you configure parameters
- 🧭 **Guided Workflow**: Step-by-step tabs for discovery, effects, and counterfactuals
- 📖 **Built-in Documentation**: Examples and guides integrated in the interface
- 🔄 **Export Results**: Download analysis results and visualizations

**Sample Web Analysis Workflow:**
1. **Upload Data** → CSV/JSON files or choose from healthcare/marketing samples
2. **Discover Relationships** → Select variables, choose domain context, view causal graph
3. **Estimate Effects** → Pick treatment/outcome, control for confounders, see confidence intervals
4. **Explore Counterfactuals** → Set interventions, generate scenarios, understand impacts
5. **Export & Share** → Download results, graphs, and analysis reports

### 📱 Installation Options

```bash
# Basic installation (CLI + Python library)
pip install causallm

# With web interface (adds Streamlit, Dash, Gradio)
pip install "causallm[ui]"

# With plugin support (LangChain, transformers)
pip install "causallm[plugins]"

# Full installation (everything)
pip install "causallm[full]"
```

---

## 🚀 Quick Start - Python

### Basic High-Performance Analysis with Configuration

```python
from causallm import EnhancedCausalLLM
import pandas as pd

# Initialize with automatic configuration (uses environment variables and defaults)
causal_llm = EnhancedCausalLLM()

# OR initialize with specific configuration overrides
causal_llm = EnhancedCausalLLM(
    llm_provider='openai',                  # LLM provider
    use_async=True,                        # Enable async processing
    cache_dir='./cache'                    # Enable persistent caching
)

# Load your data (supports very large datasets)
data = pd.read_csv("your_large_data.csv")  # Can handle millions of rows

# Comprehensive analysis with standardized parameter names
results = causal_llm.comprehensive_analysis(
    data=data,                             # Standardized: 'data' (not 'df')
    treatment_variable='treatment_col',     # Standardized: 'treatment_variable' 
    outcome_variable='outcome_col',        # Standardized: 'outcome_variable'
    domain_context='healthcare'           # Standardized: 'domain_context'
)

print(f"Effect estimate: {results.inference_results}")
print(f"Confidence: {results.confidence_score}")
```

### Configuration-Based Setup

```python
from causallm.config import CausalLLMConfig

# Create custom configuration
config = CausalLLMConfig()
config.llm.provider = 'openai'
config.performance.use_async = True
config.performance.chunk_size = 50000
config.statistical.significance_level = 0.01

# Initialize with configuration
causal_llm = EnhancedCausalLLM(config=config)

# Or use configuration file
causal_llm = EnhancedCausalLLM(config_file='my_config.json')
```

### Environment Variable Configuration

```bash
# Set environment variables for automatic configuration
export CAUSALLM_LLM_PROVIDER=openai
export CAUSALLM_USE_ASYNC=true
export CAUSALLM_CHUNK_SIZE=10000
export CAUSALLM_CACHE_DIR=./cache
export OPENAI_API_KEY=your-api-key

# No configuration needed - automatically uses environment variables
python -c "
from causallm import EnhancedCausalLLM
causal_llm = EnhancedCausalLLM()  # Automatically configured
"
```

### Memory-Efficient Processing for Large Datasets

```python
from causallm.core.data_processing import DataChunker, StreamingDataProcessor

# Process datasets that don't fit in memory
processor = StreamingDataProcessor()

def analyze_chunk(chunk_data):
    return chunk_data.corr()

# Stream and process large CSV files
results = processor.process_streaming(
    "very_large_data.csv",
    analyze_chunk,
    aggregation_func=lambda results: pd.concat(results).mean()
)
```

---

## 📦 Installation

**Choose the installation that fits your workflow:**

```bash
# Basic installation (CLI + Python library)
pip install causallm

# With monitoring and testing features (recommended for development)
pip install "causallm[testing]"

# With web interface (recommended for most users)
pip install "causallm[ui]"

# With plugin support (LangChain, transformers, etc.)
pip install "causallm[plugins]"

# Full installation (everything - web, plugins, dev tools)
pip install "causallm[full]"

# Development installation
pip install "causallm[dev]"
```

**After Installation:**
```bash
# Test CLI
causallm --help

# Launch web interface (if installed with [ui])
causallm web

# Use in Python
python -c "from causallm import CausalLLM; print('Ready!')"
```

---

## ✨ Key Features

### 🔍 **Monitoring & Observability** ⭐ *New in v4.2.0*
- **Comprehensive Metrics Collection**: Track performance, usage patterns, and system health with thread-safe collectors
- **Advanced Health Checks**: Monitor system resources, database connectivity, LLM provider APIs, and custom components
- **Performance Profiling**: Detailed memory usage tracking, execution timing, and statistical analysis
- **Real-time Monitoring**: Background monitoring with configurable intervals and alerting
- **Export & Integration**: JSON export for external monitoring systems (Prometheus, Grafana, etc.)

### 🧪 **Extended Testing Framework** ⭐ *New in v4.2.0*
- **Property-Based Testing**: Automated property verification using Hypothesis with causal-specific strategies
- **Performance Benchmarks**: Algorithm comparison, scaling analysis, and statistical performance evaluation
- **Mutation Testing**: Assess test suite quality with AST-based code mutations and survival analysis
- **Causal Test Strategies**: Generate realistic datasets with known causal structures for robust testing
- **Comprehensive Test Runner**: Unified test execution with detailed reporting and analysis

### 🖥️ **CLI & Web Interfaces** ⭐ *New in v4.1.0*
- **Command Line Tool**: `causallm` command for terminal-based analysis
- **Interactive Web Interface**: Streamlit-based GUI for point-and-click analysis  
- **No Python Required**: Full causal inference without programming
- **Multiple Input Formats**: CSV, JSON data support with sample datasets
- **Export Capabilities**: Download results, graphs, and analysis reports

### 🎯 **Standardized Interfaces** ⭐ *New*
- **Consistent Parameter Names**: Same parameter names across all components (`data`, `treatment_variable`, `outcome_variable`)
- **Unified Async Support**: All methods support both sync and async with identical interfaces  
- **Protocol-Based Design**: Type-safe interfaces ensuring consistency
- **Rich Metadata**: Comprehensive analysis metadata with execution tracking

### ⚙️ **Centralized Configuration** ⭐ *New*  
- **Environment Variable Support**: Automatic configuration from environment variables
- **Configuration Files**: JSON-based configuration with validation
- **Multiple Environments**: Development, testing, and production configurations
- **Dynamic Updates**: Runtime configuration updates with validation

### 🧠 Statistical Causal Inference
- **Multiple Methods**: Linear regression, propensity score matching, instrumental variables, doubly robust estimation
- **Assumption Testing**: Automated validation of causal inference assumptions
- **Robustness Checks**: Cross-validation across multiple statistical approaches
- **Performance Optimized**: Vectorized algorithms for large-scale analysis

### 🔍 Causal Structure Discovery  
- **PC Algorithm**: Implementation for discovering relationships from data
- **Parallel Processing**: Async independence testing for faster discovery
- **LLM Enhancement**: Optional integration with language models for domain expertise
- **Scalable**: Chunked processing for very large variable sets

### 🏭 Domain-Specific Packages
- **[Healthcare](#healthcare-domain)**: Clinical trial analysis, treatment effectiveness, patient outcomes
- **[Insurance](#insurance-domain)**: Risk assessment, premium optimization, claims analysis  
- **[Marketing](#marketing-domain)**: Campaign attribution, ROI optimization, customer analytics
- **Education**: Student outcomes, intervention analysis, policy evaluation
- **Experimentation**: A/B testing, experimental design validation

### 🔧 Advanced Performance Features
- **Data Chunking**: Automatic memory-efficient processing of large datasets
- **Intelligent Caching**: Multi-tier caching (memory + disk) with smart invalidation
- **Vectorized Algorithms**: Numba-optimized statistical computations
- **Async Processing**: Parallel execution of independent computations
- **Lazy Evaluation**: Deferred computation until results are needed
- **Resource Monitoring**: Automatic memory and CPU usage optimization

### 🌐 LLM Integrations
- **Multiple Providers**: OpenAI, Anthropic, LLaMA, local models
- **Optional Usage**: Library works fully without API keys using statistical methods
- **MCP Support**: Model Context Protocol for advanced integrations

---

## 🔍 Monitoring & Testing Examples

### Quick Start: Monitoring in Production

```python
from causallm.monitoring import configure_metrics, get_global_health_checker
from causallm.monitoring.profiler import profile, profile_block

# Configure comprehensive monitoring
collector = configure_metrics(enabled=True, collection_interval=30)
health_checker = get_global_health_checker()

# Profile your causal inference functions
@profile(name="causal_discovery", track_memory=True)
async def run_causal_analysis(data):
    # Your causal inference code
    results = await causal_llm.discover_causal_relationships(data, variables)
    
    # Manual metrics recording
    collector.record_causal_discovery(
        variables_count=len(variables),
        duration=time.time() - start_time,
        method='PC',
        success=True
    )
    return results

# Monitor system health
health_status = await health_checker.run_all_health_checks()
print(f"System status: {health_status}")
```

### Property-Based Testing for Causal Methods

```python
from causallm.testing import CausalDataStrategy, causal_hypothesis_test
from hypothesis import given

class TestCausalInference:
    @given(CausalDataStrategy.numeric_data(['X', 'Y', 'Z'], min_rows=100))
    @causal_hypothesis_test(
        strategy=CausalDataStrategy.numeric_data(['X', 'Y', 'Z']),
        property_func=lambda result, data: result is not None
    )
    def test_causal_discovery_properties(self, data):
        """Test that causal discovery returns valid results."""
        result = my_causal_discovery_function(data)
        
        # Property: Results should be deterministic for same data
        result2 = my_causal_discovery_function(data)
        assert result == result2
        
        # Property: Number of edges should be reasonable
        assert len(result.edges) <= len(data.columns) ** 2
        
        return result
```

### Performance Benchmarking

```python
from causallm.testing import BenchmarkSuite, CausalBenchmarkSuite

# Compare different causal discovery algorithms
algorithms = {
    'pc_algorithm': my_pc_implementation,
    'ges_algorithm': my_ges_implementation,
    'direct_lingam': my_lingam_implementation
}

benchmark_suite = CausalBenchmarkSuite(
    data_sizes=[100, 500, 1000, 5000],
    variable_counts=[5, 10, 15, 20]
)

# Run comprehensive benchmarks
results = {}
for name, algorithm in algorithms.items():
    results[name] = benchmark_suite.benchmark_causal_discovery(algorithm, name)

# Compare performance
comparison = benchmark_suite.compare_algorithms(
    {name: benchmark_suite.results[name] for name in algorithms.keys()}
)

print(f"Fastest algorithm: {comparison['_summary']['fastest_algorithm']}")
print(f"Most memory efficient: {comparison['_summary']['most_memory_efficient']}")
```

### Mutation Testing for Test Quality

```python
from causallm.testing import MutationTestRunner, MutationTestConfig

# Configure mutation testing
config = MutationTestConfig(
    target_files=['causallm/core/causal_discovery.py'],
    test_command='pytest tests/test_causal_discovery.py -v',
    mutation_score_threshold=0.8,
    max_mutations_per_file=50
)

# Run mutation tests
runner = MutationTestRunner(config)
results = runner.run_mutation_tests()

print(f"Mutation Score: {results['mutation_score']:.2%}")
print(f"Test Quality: {'Good' if results['passed_threshold'] else 'Needs Improvement'}")

# Analyze weak spots
if not results['passed_threshold']:
    print("Files needing better tests:")
    for file_path, stats in results['results_by_file'].items():
        if stats['mutation_score'] < 0.7:
            print(f"  {file_path}: {stats['mutation_score']:.2%}")
```

### Complete Monitoring Dashboard

```python
import asyncio
from causallm.monitoring import MetricsCollector, HealthChecker, PerformanceProfiler

class CausalLLMMonitor:
    def __init__(self):
        self.metrics = MetricsCollector(enabled=True)
        self.health_checker = HealthChecker(enabled=True)
        self.profiler = PerformanceProfiler(enabled=True)
    
    async def get_system_status(self):
        """Get comprehensive system status."""
        # Health checks
        health_results = await self.health_checker.run_all_health_checks()
        overall_health = self.health_checker.get_overall_health()
        
        # Performance metrics
        metrics_summary = self.metrics.get_metrics_summary()
        performance_summary = self.profiler.get_performance_summary()
        
        return {
            'health': overall_health,
            'metrics': metrics_summary,
            'performance': performance_summary,
            'timestamp': datetime.now().isoformat()
        }
    
    async def monitor_continuously(self, interval=60):
        """Continuous monitoring loop."""
        await self.health_checker.start_background_monitoring(interval)
        
        while True:
            status = await self.get_system_status()
            
            # Alert on issues
            if status['health']['status'] != 'healthy':
                await self.send_alert(status)
            
            await asyncio.sleep(interval)

# Usage
monitor = CausalLLMMonitor()
status = await monitor.get_system_status()
```

---

## 🏥 Domain Examples

### Healthcare Domain

Transform clinical data analysis with domain-specific expertise:

```python
from causallm import HealthcareDomain, EnhancedCausalLLM

# Initialize with healthcare configuration
causal_llm = EnhancedCausalLLM(
    config_file='healthcare_config.json',  # Domain-specific configuration
    domain_context='healthcare'
)

healthcare = HealthcareDomain()

# Generate realistic clinical trial data (scalable)
clinical_data = healthcare.generate_clinical_trial_data(
    n_patients=100000,  # Large dataset support
    treatment_arms=['control', 'treatment_a', 'treatment_b']
)

# Treatment effectiveness analysis with standardized interface
results = causal_llm.estimate_causal_effect(
    data=clinical_data,                    # Standardized parameter
    treatment_variable='treatment_group',   # Standardized parameter
    outcome_variable='recovery_time',      # Standardized parameter  
    covariate_variables=['age', 'baseline_severity', 'comorbidities']
)

print(f"Treatment effect: {results.primary_effect.estimate:.2f} days")
print(f"Confidence interval: {results.primary_effect.confidence_interval}")
print(f"Clinical significance: {results.interpretation}")
```

**Healthcare Features:**
- Clinical trial data generation with proper randomization
- Treatment effectiveness analysis with medical context
- Safety analysis and adverse event evaluation
- Patient outcome prediction with clinical insights

### Insurance Domain

Optimize risk assessment and premium pricing:

```python
from causallm import InsuranceDomain, EnhancedCausalLLM

# Initialize with insurance-optimized configuration
causal_llm = EnhancedCausalLLM(
    config_file='insurance_config.json',
    use_async=True,                    # Handle large policy datasets
    chunk_size=50000                   # Optimize for policy data
)

insurance = InsuranceDomain()

# Generate large-scale policy data
policy_data = insurance.generate_stop_loss_data(n_policies=500000)

# Risk factor analysis with standardized interface
risk_results = causal_llm.estimate_causal_effect(
    data=policy_data,                     # Standardized parameter
    treatment_variable='industry_type',   # Standardized parameter
    outcome_variable='total_claim_amount', # Standardized parameter
    covariate_variables=['company_size', 'policy_limit', 'geographic_region']
)

print(f"Industry risk effect: ${risk_results.primary_effect.estimate:,.0f}")
print(f"Statistical significance: p = {risk_results.primary_effect.p_value:.6f}")
print(f"Confidence level: {risk_results.confidence_level}")
```

**Insurance Features:**
- Stop loss insurance data simulation
- Risk factor analysis with actuarial insights
- Premium optimization recommendations
- Claims prediction and underwriting support

### Marketing Domain

Master campaign attribution and ROI optimization:

```python
from causallm.domains.marketing import MarketingDomain
from causallm import EnhancedCausalLLM

# Initialize with marketing-optimized configuration
causal_llm = EnhancedCausalLLM(
    config_file='marketing_config.json',
    llm_provider='openai',             # For enhanced attribution insights
    use_async=True                     # Handle large touchpoint datasets
)

marketing = MarketingDomain(enable_performance_optimizations=True)

# Generate sample marketing data
marketing_data = marketing.generate_marketing_data(
    n_customers=10000,
    n_touchpoints=30000
)

# Comprehensive attribution analysis with standardized interface
attribution_result = causal_llm.comprehensive_analysis(
    data=marketing_data,               # Standardized parameter
    treatment_variable='channel_spend', # Standardized parameter
    outcome_variable='conversion_value', # Standardized parameter
    covariate_variables=['customer_segment', 'touchpoint_sequence'],
    domain_context='marketing'         # Standardized parameter
)

print(f"Overall attribution confidence: {attribution_result.confidence_score:.2f}")
for insight in attribution_result.actionable_insights[:3]:
    print(f"• {insight}")
```

**Marketing Features:**
- Multi-touch attribution modeling (first-touch, last-touch, data-driven, Shapley)
- Campaign ROI analysis and optimization
- Cross-device and cross-channel attribution
- Customer lifetime value modeling

**Quick Reference - Attribution Models:**
| Model | Best For | Description |
|-------|----------|-------------|
| `data_driven` | **Recommended** | Uses causal inference for attribution |
| `first_touch` | Brand awareness | 100% credit to first interaction |
| `last_touch` | Direct response | 100% credit to last interaction |
| `linear` | Balanced view | Equal credit across touchpoints |
| `shapley` | Advanced | Game theory based attribution |

---

## 🏗️ Core Components

### EnhancedCausalLLM
High-performance main class with **standardized interfaces** and **centralized configuration management**.

```python
from causallm import EnhancedCausalLLM
from causallm.config import CausalLLMConfig

# Configuration-driven initialization (recommended)
causal_llm = EnhancedCausalLLM(config_file='my_config.json')

# OR with parameter overrides
causal_llm = EnhancedCausalLLM(
    config_file='base_config.json',
    llm_provider='openai',          # Override configuration  
    use_async=True,                 # Enable async processing
    cache_dir='./cache'             # Custom cache location
)

# OR programmatic configuration
config = CausalLLMConfig()
config.llm.provider = 'openai'
config.llm.model = 'gpt-4'
config.performance.use_async = True
config.statistical.significance_level = 0.01
causal_llm = EnhancedCausalLLM(config=config)

# OR automatic configuration from environment variables
causal_llm = EnhancedCausalLLM()  # Uses env vars + defaults
```

#### **New Configuration Features:**
- **Environment Variable Support**: Automatic configuration from `CAUSALLM_*` environment variables
- **Configuration Files**: JSON-based configuration with validation and inheritance
- **Dynamic Updates**: Runtime configuration changes with `update_configuration()`
- **Performance Metrics**: Built-in execution tracking with `get_performance_metrics()`

### Statistical Methods (Performance Optimized)
- **Vectorized Linear Regression**: NumPy/Numba optimized for large datasets
- **Fast Propensity Score Matching**: Efficient matching algorithms with parallel processing  
- **Optimized Instrumental Variables**: Matrix operations optimized for speed
- **Parallel PC Algorithm**: Concurrent independence testing for causal discovery

### Domain Packages (Scalable)
Pre-configured, performance-optimized components for specific industries with built-in expertise and realistic data generators.

---

## ⚡ Performance

### Dataset Size Support
- **Small Datasets** (< 10K rows): Instant analysis with full feature set
- **Medium Datasets** (10K - 100K rows): Automatic optimization, ~2-5x speedup
- **Large Datasets** (100K - 1M rows): Chunked processing, async operations
- **Very Large Datasets** (> 1M rows): Streaming analysis, distributed computing

### Speed Improvements
- **Correlation Analysis**: 10x faster with Numba vectorization
- **Causal Discovery**: 5x faster with parallel independence testing  
- **Effect Estimation**: 3x faster with optimized matching algorithms
- **Repeated Analysis**: 20x+ faster with intelligent caching

### Memory Efficiency  
- **Data Chunking**: Process datasets 10x larger than available RAM
- **Lazy Evaluation**: 60-80% memory reduction through deferred computation
- **Smart Caching**: Configurable memory vs. disk trade-offs

### Performance Configuration Examples

```python
# Small datasets (< 10K rows)
causal_llm = EnhancedCausalLLM(
    enable_performance_optimizations=False  # Overhead not worth it
)

# Large datasets (100K+ rows)
causal_llm = EnhancedCausalLLM(
    enable_performance_optimizations=True,
    chunk_size=50000,
    use_async=True,
    cache_dir="./cache",
    max_memory_usage_gb=8
)
```

---

## 📚 API Documentation

### Core Methods

#### `comprehensive_analysis()`
Complete end-to-end causal analysis combining discovery and inference.

```python
analysis = causal_llm.comprehensive_analysis(
    data=df,                     # Required: Your dataset
    treatment='campaign',        # Optional: Specific treatment
    outcome='revenue',          # Optional: Specific outcome  
    domain='marketing',         # Optional: Domain context
    covariates=['age', 'income'] # Optional: Control variables
)
```

**Returns:** `ComprehensiveCausalAnalysis` with:
- `discovery_results`: Causal structure findings
- `inference_results`: Detailed effect estimates
- `domain_recommendations`: Domain-specific advice
- `actionable_insights`: List of actionable findings
- `confidence_score`: Overall analysis confidence (0-1)

#### `discover_causal_relationships()`
Automatically discover causal relationships in your data.

```python
discovery = causal_llm.discover_causal_relationships(
    data=df,
    variables=['age', 'treatment', 'outcome'],
    domain='healthcare'
)
```

**Returns:** `CausalDiscoveryResult` with discovered edges, confounders, and domain insights.

#### `estimate_causal_effect()`
Estimate the causal effect of a treatment on an outcome.

```python
effect = causal_llm.estimate_causal_effect(
    data=df,
    treatment='new_drug',
    outcome='recovery_rate',
    covariates=['age', 'severity'],
    method='comprehensive'  # 'regression', 'matching', 'iv'
)
```

**Returns:** `CausalInferenceResult` with effect estimates, confidence intervals, and robustness checks.

### Statistical Methods

Available through `StatisticalCausalInference`:

- `CausalMethod.LINEAR_REGRESSION`: Standard regression with covariates
- `CausalMethod.MATCHING`: Propensity score matching
- `CausalMethod.INSTRUMENTAL_VARIABLES`: Two-stage least squares
- `CausalMethod.REGRESSION_DISCONTINUITY`: RDD (if applicable)
- `CausalMethod.DIFFERENCE_IN_DIFFERENCES`: DiD (if applicable)

### Domain Packages API

Each domain package provides:
- **Data Generators**: Realistic synthetic data with proper causal structure
- **Domain Knowledge**: Expert knowledge about relationships and confounders
- **Analysis Templates**: Pre-configured workflows with domain-specific interpretation

---

## 🔧 Advanced Features

### Cached Analysis for Faster Iterations

```python
from causallm.core.caching import StatisticalComputationCache

# Enable persistent caching across sessions
causal_llm = EnhancedCausalLLM(cache_dir="./causallm_cache")

# First run computes and caches
result1 = causal_llm.estimate_causal_effect(data, 'treatment', 'outcome')

# Second run uses cached results (10x+ faster)  
result2 = causal_llm.estimate_causal_effect(data, 'treatment', 'outcome')
```

### Async Processing for Maximum Performance

```python
import asyncio
from causallm.core.async_processing import AsyncCausalAnalysis

async def parallel_analysis():
    async_causal = AsyncCausalAnalysis()
    
    # Parallel correlation analysis
    corr_matrix = await async_causal.parallel_correlation_analysis(
        large_data, chunk_size=5000
    )
    
    # Parallel bootstrap analysis  
    bootstrap_results = await async_causal.parallel_bootstrap_analysis(
        large_data, analysis_func=my_analysis, n_bootstrap=1000
    )
    
    return corr_matrix, bootstrap_results

# Run async analysis
results = asyncio.run(parallel_analysis())
```

### MCP Server Integration

CausalLLM provides Model Context Protocol (MCP) server capabilities for integration with Claude Desktop, VS Code, and other MCP-enabled applications:

```bash
# Start MCP server for integration with Claude Desktop, VS Code, etc.
python -m causallm.mcp.server --port 8000
```

**Available MCP tools:**
- `simulate_counterfactual`: Generate counterfactual scenarios
- `analyze_treatment_effect`: High-performance treatment analysis  
- `extract_causal_edges`: Parallel causal relationship extraction
- `generate_reasoning_prompt`: LLM-enhanced causal reasoning

### Statistical Rigor with Performance

- **Assumption Validation**: Automated testing with parallel processing
- **Robustness Checks**: Cross-validation across multiple optimized methods
- **Confidence Intervals**: Uncertainty quantification with bootstrap parallelization  
- **Effect Size Interpretation**: Statistical and practical significance assessment
- **Performance Monitoring**: Automatic benchmarking and optimization suggestions

---

## 📋 Requirements

### Core Dependencies
- Python 3.9+
- pandas >= 1.3.0
- numpy >= 1.21.0  
- scikit-learn >= 1.0.0
- scipy >= 1.7.0

### Performance Dependencies (Automatically Installed)
- numba >= 0.56.0 (JIT compilation)
- dask >= 2022.1.0 (distributed computing)
- psutil >= 5.8.0 (resource monitoring)

### Optional Dependencies
- openai >= 1.0.0 (LLM features)
- anthropic (Claude integration)
- aiofiles (async file operations)

---

## 🤝 Support & Community

### Getting Help

- **GitHub Issues**: [Report bugs & request features](https://github.com/rdmurugan/causallm/issues)
- **GitHub Discussions**: [Community support & questions](https://github.com/rdmurugan/causallm/discussions)
- **Performance Issues**: Tag with 'performance' label
- **Email Support**: durai@infinidatum.net
- **LinkedIn**: [Durai Rajamanickam](https://www.linkedin.com/in/durai-rajamanickam)

### 📚 Documentation

- **📋 [Documentation Index](docs/DOCUMENTATION_INDEX.md)**: Complete documentation guide and navigation
- **🔧 [API Reference](docs/API_REFERENCE.md)**: Complete API documentation with all classes and methods
- **📖 [Complete User Guide](docs/COMPLETE_USER_GUIDE.md)**: Comprehensive guide with examples and best practices
- **⚡ [Performance Guide](docs/PERFORMANCE_GUIDE.md)**: Optimization tips and benchmarks  
- **🏭 [Domain Packages Guide](docs/DOMAIN_PACKAGES.md)**: Industry-specific components and examples
- **🔗 [MCP Usage Guide](docs/MCP_USAGE.md)**: Model Context Protocol integration
- **📚 [Usage Examples](docs/USAGE_EXAMPLES.md)**: Real-world use cases across domains
- **📈 [Marketing Quick Reference](docs/MARKETING_QUICK_REFERENCE.md)**: Marketing attribution guide
- **💡 [Examples Directory](examples/)**: Runnable code examples and tutorials

### Contributing

We welcome contributions! Areas where help is needed:
- Additional domain packages (finance, retail, manufacturing)
- New statistical methods with performance optimization
- Advanced caching strategies
- Distributed computing enhancements

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for guidelines.

### Performance Support & Benchmarking

```python
# Built-in performance demo
from causallm.performance_demo import PerformanceBenchmark

benchmark = PerformanceBenchmark()
results = benchmark.run_comprehensive_benchmark([10000, 50000, 100000])
print(benchmark.generate_performance_report())
```

---

## 📄 License

CausalLM Custom License - see [LICENSE](LICENSE) file for details.

**Note**: Commercial use requires written permission. Contact durai@infinidatum.net for commercial licensing inquiries.

---

## 📖 Citation

If you use CausalLLM in your research:

```bibtex
@software{causallm2024,
  title={CausalLLM: High-Performance Causal Inference Library},
  author={Durai Rajamanickam},
  year={2024},
  url={https://github.com/rdmurugan/causallm},
  note={Performance-optimized causal inference with statistical rigor}
}
```

---

## 🏢 About

CausalLLM is developed and maintained by **Durai Rajamanickam**, with contributions from the open source community. The library aims to make causal inference more accessible while maintaining statistical rigor and providing enterprise-grade performance for production use cases.

---

**✨ Ready to discover causal insights in your data? Start with `pip install causallm` and explore the [examples](examples/) directory!**