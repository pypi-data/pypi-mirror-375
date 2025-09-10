# Marketing Attribution Analysis Guide

This guide demonstrates how to use CausalLLM's Marketing Domain for comprehensive attribution analysis and campaign measurement.

## 🚀 Quick Start

### Basic Usage

```python
from causallm.domains.marketing import MarketingDomain

# Initialize marketing domain
marketing = MarketingDomain()

# Generate sample data
data = marketing.generate_marketing_data(n_customers=10000, n_touchpoints=30000)

# Run attribution analysis
result = marketing.analyze_attribution(
    data, 
    model='data_driven',
    conversion_column='conversion',
    customer_id_column='customer_id', 
    channel_column='channel',
    timestamp_column='timestamp'
)

# View results
print(f"Channel Attribution: {result.channel_attribution}")
print(f"Conversion Probability: {result.conversion_probability:.2%}")
```

### Available Attribution Models

1. **First Touch**: 100% credit to first interaction
2. **Last Touch**: 100% credit to last interaction  
3. **Linear**: Equal credit across all touchpoints
4. **Time Decay**: More credit to recent interactions
5. **Position Based**: More credit to first and last touches
6. **Data Driven**: Uses causal inference (recommended)
7. **Shapley**: Game theory based attribution

## 📊 Examples

### 1. Quick Start Example
**File**: `marketing_attribution_quickstart.py`

A simple 15-minute tutorial covering:
- Data generation
- Multi-touch attribution
- Model comparison
- Campaign ROI analysis

```bash
python marketing_attribution_quickstart.py
```

### 2. Comprehensive Demo
**File**: `comprehensive_marketing_attribution_demo.py`

Full-featured demonstration including:
- Large dataset processing (25K+ customers)
- All 7 attribution models
- Performance optimization features
- Advanced scenarios
- Business insights generation

```bash
python comprehensive_marketing_attribution_demo.py
```

## 🎯 Core Features

### Multi-Touch Attribution

```python
# Compare multiple attribution models
models = ['first_touch', 'last_touch', 'linear', 'time_decay', 'data_driven']
results = {}

for model in models:
    results[model] = marketing.analyze_attribution(data, model=model)

# Find consensus attribution
consensus = marketing.attribution_analyzer.compare_attribution_models(
    data, 
    models=models
)
```

### Campaign ROI Analysis

```python
# Generate campaign spend data
spend_data = marketing.data_generator.generate_campaign_spend_data(
    n_campaigns=30,
    date_range_days=90
)

# Analyze ROI by campaign
roi_results = marketing.attribution_analyzer.analyze_campaign_roi(
    data=touchpoint_data,
    spend_data=spend_data,
    campaign_column='campaign_id',
    spend_column='spend',
    revenue_column='revenue'
)

# View top performing campaigns
for campaign_id, metrics in roi_results.items():
    print(f"{campaign_id}: ROI {metrics.roi:.1f}x, CPA ${metrics.cost_per_acquisition:.2f}")
```

### Advanced Attribution Scenarios

```python
# Test specific attribution scenarios
scenarios = ['simple', 'complex_journey', 'display_assisted']

for scenario in scenarios:
    scenario_data, true_attribution = marketing.data_generator.generate_cross_channel_scenario(
        scenario_type=scenario,
        n_customers=5000
    )
    
    # Test attribution accuracy
    result = marketing.analyze_attribution(scenario_data, model='data_driven')
    
    # Compare predicted vs actual
    for channel in true_attribution:
        predicted = result.channel_attribution.get(channel, 0)
        actual = true_attribution[channel]
        accuracy = 1 - abs(predicted - actual) / actual
        print(f"{channel}: {accuracy:.1%} accuracy")
```

## 🔧 Advanced Features

### Performance Optimizations

```python
# Enable performance optimizations for large datasets
marketing = MarketingDomain(enable_performance_optimizations=True)

# Data chunking for memory efficiency
from causallm.core.data_processing import DataChunker
chunker = DataChunker()

for chunk_idx, chunk_data in chunker.chunk_dataframe(large_data, chunk_size=10000):
    chunk_result = marketing.analyze_attribution(chunk_data, model='linear')
    # Process chunk results
```

### Async Processing

```python
# Compare models asynchronously for faster processing
import asyncio

async def compare_models_async():
    models = ['first_touch', 'last_touch', 'linear', 'time_decay']
    results = await marketing.attribution_analyzer.compare_attribution_models_async(
        data, 
        models=models
    )
    return results

results = asyncio.run(compare_models_async())
```

### Caching for Repeated Analysis

```python
# Enable caching for faster repeated analysis
from causallm import EnhancedCausalLLM

causal_llm = EnhancedCausalLLM(
    cache_dir="./attribution_cache",
    enable_performance_optimizations=True
)

# First run: computed and cached
result1 = marketing.analyze_attribution(data, model='data_driven')

# Second run: retrieved from cache (much faster)
result2 = marketing.analyze_attribution(data, model='data_driven')
```

## 📈 Industry-Specific Analysis

### E-commerce Attribution

```python
# E-commerce funnel analysis
from causallm.domains.marketing.templates.attribution_template import AttributionAnalysisTemplate

template = AttributionAnalysisTemplate()
ecommerce_result = template.run_analysis(
    'ecommerce_funnel',
    data,
    funnel_stages=['awareness', 'consideration', 'purchase', 'retention']
)

print("Funnel Attribution:", ecommerce_result.attribution_results['funnel_attribution'])
```

### B2B Lead Generation

```python
# B2B lead generation analysis
b2b_result = template.run_analysis(
    'lead_generation',
    data,
    lead_score_column='lead_score'
)

print("Quality-weighted Attribution:", b2b_result.attribution_results['quality_weighted_attribution'])
```

### Brand Awareness Measurement

```python
# Brand awareness impact analysis
brand_result = template.run_analysis(
    'brand_awareness',
    data,
    brand_channels=['display', 'video', 'social_media'],
    performance_channels=['paid_search', 'shopping']
)

print("Brand Assist Rate:", brand_result.attribution_results['brand_assist_rates'])
```

## 📊 Campaign Analysis Templates

### Campaign Effectiveness

```python
from causallm.domains.marketing.templates.campaign_analysis import CampaignAnalysisTemplate

campaign_template = CampaignAnalysisTemplate()

# Overall campaign effectiveness
effectiveness_result = campaign_template.run_analysis(
    'campaign_effectiveness',
    data,
    campaign_column='campaign_id',
    conversion_column='conversion',
    revenue_column='revenue'
)

print("Top Campaigns:", effectiveness_result.campaign_performance['top_roi_campaigns'])
```

### ROI Optimization

```python
# ROI optimization analysis
roi_optimization = campaign_template.run_analysis(
    'roi_optimization',
    data,
    target_roi=2.0
)

print("Budget Recommendations:", roi_optimization.recommendations)
```

### Channel Comparison

```python
# Cross-channel performance comparison
channel_comparison = campaign_template.run_analysis(
    'channel_comparison',
    data,
    channel_column='channel'
)

print("Channel Rankings:", channel_comparison.campaign_performance['channel_rankings'])
```

## 🧠 Domain Knowledge Integration

### Industry Benchmarks

```python
from causallm.domains.marketing.knowledge.marketing_knowledge import MarketingKnowledge

knowledge = MarketingKnowledge()

# Get industry benchmarks
benchmarks = knowledge.get_industry_benchmarks('ecommerce')
print(f"Industry avg conversion rate: {benchmarks['avg_conversion_rate']:.2%}")

# Get channel characteristics
channel_info = knowledge.get_channel_characteristics('paid_search')
print(f"Paid search typical position: {channel_info['typical_position']}")
```

### Attribution Recommendations

```python
# Get model recommendations based on business characteristics
business_info = {
    'type': 'ecommerce',
    'sales_cycle_days': 14,
    'avg_journey_length': 4
}

recommendations = knowledge.get_model_recommendations(business_info)
print(f"Recommended model: {recommendations['primary_recommendation']}")
print(f"Top 3 models: {recommendations['top_3_models']}")
```

## 📋 Best Practices

### 1. Attribution Window Selection

```python
# Get attribution window recommendations
window_rec = knowledge.get_attribution_window_recommendation(
    industry='ecommerce',
    business_model='ecommerce',
    avg_consideration_time=7
)

print(f"Recommended window: {window_rec['attribution_windows']['recommended']} days")
```

### 2. Model Selection Guidelines

- **E-commerce (short cycle)**: Last-touch or Time-decay
- **E-commerce (long cycle)**: Position-based or Data-driven
- **B2B**: Time-decay or Data-driven
- **Brand awareness**: Linear or Position-based
- **Mobile apps**: First-touch or Time-decay

### 3. Data Requirements

- **Minimum touchpoints**: 10,000+ for reliable results
- **Minimum conversions**: 100+ for statistical significance
- **Attribution window**: Match to typical customer journey length
- **Channel coverage**: Include all major marketing channels

### 4. Validation Approaches

```python
# Validate attribution setup
validation = knowledge.validate_attribution_setup({
    'attribution_window_days': 30,
    'business_type': 'ecommerce',
    'attribution_models': ['first_touch', 'last_touch', 'data_driven'],
    'tracking_setup': {
        'cross_channel_tracking': True,
        'conversion_tracking': True
    }
})

print(f"Setup score: {validation['score']}/100")
print(f"Rating: {validation['overall_rating']}")
```

## 🚀 Performance Tips

1. **Enable optimizations** for datasets > 10K touchpoints
2. **Use caching** for repeated analysis
3. **Chunk data** for memory efficiency with very large datasets
4. **Run models in parallel** when comparing multiple approaches
5. **Use appropriate attribution windows** based on business model

## 📚 Additional Resources

- **Performance Guide**: See `PERFORMANCE_GUIDE.md` for optimization details
- **API Reference**: Complete documentation in `COMPLETE_USER_GUIDE.md`
- **Domain Packages**: More industry-specific examples in `DOMAIN_PACKAGES.md`

## 🤝 Contributing

Found a bug or want to add features? Please contribute to the [CausalLLM repository](https://github.com/rdmurugan/causallm).

---

For support, please visit the [GitHub Issues](https://github.com/rdmurugan/causallm/issues) or [Discussions](https://github.com/rdmurugan/causallm/discussions).