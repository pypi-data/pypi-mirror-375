#!/usr/bin/env python3
"""
Marketing Attribution Quick Start Guide

A simple example showing how to use CausalLLM for marketing attribution analysis.
This example covers the essential features for getting started quickly.

Features:
- Generate sample marketing data
- Run multi-touch attribution
- Compare attribution models
- Analyze campaign ROI

Run with: python marketing_attribution_quickstart.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import CausalLLM Marketing Domain
try:
    from causallm.domains.marketing import MarketingDomain
    print("✓ CausalLLM Marketing Domain loaded successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please install causallm with: pip install causallm")
    sys.exit(1)


def main():
    """Quick start example for marketing attribution."""
    print("🚀 Marketing Attribution Quick Start")
    print("=" * 40)
    
    # 1. Initialize Marketing Domain
    print("\n1️⃣ Initializing Marketing Domain...")
    marketing = MarketingDomain()
    print("✓ Marketing domain initialized")
    
    # 2. Generate Sample Data
    print("\n2️⃣ Generating Sample Marketing Data...")
    customer_data = marketing.generate_marketing_data(
        n_customers=5000,
        n_touchpoints=15000
    )
    print(f"✓ Generated {len(customer_data):,} touchpoints for {customer_data['customer_id'].nunique():,} customers")
    
    # Show data sample
    print("\nData sample:")
    print(customer_data[['customer_id', 'channel', 'conversion', 'revenue']].head())
    
    # 3. Run Multi-Touch Attribution
    print("\n3️⃣ Running Multi-Touch Attribution...")
    
    # Compare different attribution models
    models_to_test = ['first_touch', 'last_touch', 'linear', 'time_decay']
    results = {}
    
    for model in models_to_test:
        print(f"   Running {model} model...")
        result = marketing.analyze_attribution(
            customer_data,
            model=model,
            conversion_column='conversion',
            customer_id_column='customer_id',
            channel_column='channel',
            timestamp_column='timestamp'
        )
        results[model] = result
        
        # Show top 3 channels for this model
        top_channels = sorted(result.channel_attribution.items(), 
                            key=lambda x: x[1], reverse=True)[:3]
        channel_text = ", ".join([f"{ch}: {wt:.1%}" for ch, wt in top_channels])
        print(f"     Top channels: {channel_text}")
    
    # 4. Compare Attribution Models
    print("\n4️⃣ Attribution Model Comparison:")
    print(f"{'Model':<12} {'Top Channel':<15} {'Attribution':<12} {'Confidence':<12}")
    print("-" * 60)
    
    for model_name, result in results.items():
        top_channel = max(result.channel_attribution.items(), key=lambda x: x[1])
        confidence = result.model_performance.get('model_accuracy', 0)
        
        print(f"{model_name:<12} {top_channel[0]:<15} {top_channel[1]:<12.1%} {confidence:<12.1%}")
    
    # 5. Campaign ROI Analysis
    print("\n5️⃣ Campaign ROI Analysis...")
    
    # Generate campaign spend data
    campaign_spend = marketing.data_generator.generate_campaign_spend_data(
        n_campaigns=20,
        date_range_days=90
    )
    
    # Aggregate spend by campaign
    campaign_spend_agg = campaign_spend.groupby('campaign_id').agg({
        'spend': 'sum',
        'channel': 'first'
    }).reset_index()
    
    # Analyze ROI
    try:
        roi_results = marketing.attribution_analyzer.analyze_campaign_roi(
            data=customer_data,
            spend_data=campaign_spend_agg,
            campaign_column='campaign_id',
            spend_column='spend',
            revenue_column='revenue'
        )
        
        print(f"✓ Analyzed ROI for {len(roi_results)} campaigns")
        
        # Show top 5 campaigns by ROI
        sorted_campaigns = sorted(roi_results.items(), key=lambda x: x[1].roi, reverse=True)
        
        print(f"\nTop 5 Campaigns by ROI:")
        print(f"{'Campaign':<20} {'Spend':<10} {'Revenue':<10} {'ROI':<8}")
        print("-" * 50)
        
        for campaign_id, metrics in sorted_campaigns[:5]:
            print(f"{campaign_id:<20} ${metrics.total_spend:<9,.0f} "
                  f"${metrics.total_revenue:<9,.0f} {metrics.roi:<8.1f}x")
        
    except Exception as e:
        print(f"⚠️  ROI analysis failed: {e}")
    
    # 6. Business Recommendations
    print("\n6️⃣ Key Insights & Recommendations:")
    
    # Find most consistent channel across models
    channel_scores = {}
    for result in results.values():
        for channel, weight in result.channel_attribution.items():
            if channel not in channel_scores:
                channel_scores[channel] = []
            channel_scores[channel].append(weight)
    
    # Calculate average attribution per channel
    avg_attribution = {ch: np.mean(scores) for ch, scores in channel_scores.items()}
    top_channel = max(avg_attribution.items(), key=lambda x: x[1])
    
    print(f"• Primary recommendation: Focus investment on {top_channel[0]}")
    print(f"  (Average {top_channel[1]:.1%} attribution across all models)")
    
    # Check for high-converting channels
    channel_performance = customer_data.groupby('channel').agg({
        'conversion': ['mean', 'sum'],
        'revenue': 'sum'
    })
    
    best_converting_channel = channel_performance[('conversion', 'mean')].idxmax()
    best_cr = channel_performance.loc[best_converting_channel, ('conversion', 'mean')]
    
    print(f"• Highest converting channel: {best_converting_channel} ({best_cr:.1%} conversion rate)")
    
    # Revenue insights
    total_revenue = customer_data['revenue'].sum()
    total_conversions = customer_data['conversion'].sum()
    avg_order_value = total_revenue / total_conversions if total_conversions > 0 else 0
    
    print(f"• Total attributed revenue: ${total_revenue:,.2f}")
    print(f"• Average order value: ${avg_order_value:.2f}")
    
    print("\n✅ Quick start analysis completed!")
    
    # Next Steps
    print("\n📚 Next Steps:")
    print("1. Try with your own marketing data")
    print("2. Experiment with different attribution windows")
    print("3. Run the comprehensive demo: python comprehensive_marketing_attribution_demo.py")
    print("4. Explore advanced features like cross-device attribution")


if __name__ == "__main__":
    main()