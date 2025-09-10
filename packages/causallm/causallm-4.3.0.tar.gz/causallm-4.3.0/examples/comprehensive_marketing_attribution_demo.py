#!/usr/bin/env python3
"""
Comprehensive Marketing Attribution Analysis Demo

This example demonstrates the full capabilities of the CausalLLM Marketing Domain package
including multi-touch attribution modeling, campaign ROI analysis, and advanced measurement
techniques with performance optimizations.

Features Demonstrated:
- Multi-touch attribution with 7 different models
- Campaign effectiveness analysis
- Cross-channel attribution scenarios
- ROI optimization recommendations
- Performance-optimized analysis for large datasets
- Industry-specific best practices
- Attribution model comparison and validation

Run with: python comprehensive_marketing_attribution_demo.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import CausalLLM Marketing Domain
try:
    from causallm.domains.marketing import MarketingDomain
    from causallm import EnhancedCausalLLM
    print("✓ CausalLLM Marketing Domain imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please install causallm with: pip install causallm[full]")
    sys.exit(1)

class MarketingAttributionDemo:
    """
    Comprehensive demonstration of marketing attribution analysis capabilities.
    """
    
    def __init__(self):
        """Initialize the marketing attribution demo."""
        print("🚀 Initializing Marketing Attribution Analysis Demo")
        print("=" * 60)
        
        # Initialize marketing domain with performance optimizations
        self.marketing_domain = MarketingDomain(enable_performance_optimizations=True)
        self.causal_llm = EnhancedCausalLLM(enable_performance_optimizations=True)
        
        # Demo configuration
        self.demo_config = {
            'n_customers': 25000,      # Large dataset for performance demo
            'n_touchpoints': 75000,    # Average 3 touchpoints per customer
            'date_range_days': 90,
            'n_campaigns': 30
        }
        
        print(f"📊 Demo Configuration:")
        print(f"   • Customers: {self.demo_config['n_customers']:,}")
        print(f"   • Touchpoints: {self.demo_config['n_touchpoints']:,}")
        print(f"   • Time Period: {self.demo_config['date_range_days']} days")
        print(f"   • Campaigns: {self.demo_config['n_campaigns']}")
        print()
    
    def run_complete_demo(self):
        """Run the complete marketing attribution demo."""
        print("🎯 Starting Comprehensive Marketing Attribution Analysis")
        print("=" * 60)
        
        try:
            # Step 1: Generate realistic marketing data
            print("\n📈 STEP 1: Generating Realistic Marketing Data")
            print("-" * 50)
            customer_data, campaign_spend = self._generate_demo_data()
            
            # Step 2: Multi-touch attribution analysis
            print("\n🔍 STEP 2: Multi-Touch Attribution Analysis")
            print("-" * 50)
            attribution_results = self._run_attribution_analysis(customer_data)
            
            # Step 3: Campaign ROI analysis
            print("\n💰 STEP 3: Campaign ROI Analysis")
            print("-" * 50)
            roi_analysis = self._analyze_campaign_roi(customer_data, campaign_spend)
            
            # Step 4: Advanced attribution scenarios
            print("\n🌟 STEP 4: Advanced Attribution Scenarios")
            print("-" * 50)
            scenario_analysis = self._run_advanced_scenarios()
            
            # Step 5: Performance optimization demo
            print("\n⚡ STEP 5: Performance Optimization Demo")
            print("-" * 50)
            performance_demo = self._demonstrate_performance_features(customer_data)
            
            # Step 6: Business insights and recommendations
            print("\n📋 STEP 6: Business Insights & Recommendations")
            print("-" * 50)
            insights = self._generate_business_insights(
                attribution_results, roi_analysis, scenario_analysis
            )
            
            # Step 7: Summary report
            print("\n📊 STEP 7: Executive Summary")
            print("-" * 50)
            self._generate_executive_summary(attribution_results, roi_analysis, insights)
            
        except Exception as e:
            print(f"❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    def _generate_demo_data(self):
        """Generate realistic marketing data for the demo."""
        print("Generating customer journey data...")
        
        # Generate customer journey data
        customer_data = self.marketing_domain.generate_marketing_data(
            n_customers=self.demo_config['n_customers'],
            n_touchpoints=self.demo_config['n_touchpoints'],
            date_range_days=self.demo_config['date_range_days']
        )
        
        # Generate campaign spend data
        campaign_spend = self.marketing_domain.data_generator.generate_campaign_spend_data(
            n_campaigns=self.demo_config['n_campaigns'],
            date_range_days=self.demo_config['date_range_days']
        )
        
        print(f"✓ Generated {len(customer_data):,} touchpoints for {customer_data['customer_id'].nunique():,} customers")
        print(f"✓ Generated spend data for {len(campaign_spend):,} campaign-days")
        
        # Display data overview
        self._display_data_overview(customer_data, campaign_spend)
        
        return customer_data, campaign_spend
    
    def _display_data_overview(self, customer_data, campaign_spend):
        """Display overview of generated data."""
        print("\n📊 Data Overview:")
        
        # Customer journey metrics
        total_conversions = customer_data['conversion'].sum()
        total_revenue = customer_data['revenue'].sum()
        conversion_rate = customer_data['conversion'].mean()
        
        print(f"   Journey Metrics:")
        print(f"   • Total Conversions: {total_conversions:,}")
        print(f"   • Total Revenue: ${total_revenue:,.2f}")
        print(f"   • Conversion Rate: {conversion_rate:.2%}")
        print(f"   • Avg Revenue per Conversion: ${total_revenue/total_conversions:.2f}" if total_conversions > 0 else "")
        
        # Channel breakdown
        channel_summary = customer_data.groupby('channel').agg({
            'conversion': ['count', 'sum', 'mean'],
            'revenue': 'sum',
            'estimated_cost': 'sum'
        }).round(3)
        
        print(f"\n   Channel Breakdown:")
        for channel in channel_summary.index:
            touchpoints = channel_summary.loc[channel, ('conversion', 'count')]
            conversions = channel_summary.loc[channel, ('conversion', 'sum')]
            cr = channel_summary.loc[channel, ('conversion', 'mean')]
            revenue = channel_summary.loc[channel, ('revenue', 'sum')]
            cost = channel_summary.loc[channel, ('estimated_cost', 'sum')]
            roi = (revenue - cost) / cost if cost > 0 else 0
            
            print(f"   • {channel.title()}: {touchpoints:,} touches, {conversions} conv, {cr:.1%} CR, ROI: {roi:.1f}x")
    
    def _run_attribution_analysis(self, data):
        """Run comprehensive multi-touch attribution analysis."""
        print("Running multi-touch attribution models...")
        
        # Get available attribution models
        available_models = self.marketing_domain.get_attribution_models()
        print(f"✓ Available models: {', '.join(available_models)}")
        
        # Run individual attribution models
        attribution_results = {}
        
        # Test different attribution models
        models_to_test = ['first_touch', 'last_touch', 'linear', 'time_decay', 'position_based', 'data_driven']
        
        for model in models_to_test:
            try:
                print(f"   Analyzing with {model} model...")
                result = self.marketing_domain.analyze_attribution(
                    data,
                    model=model,
                    conversion_column='conversion',
                    customer_id_column='customer_id',
                    channel_column='channel',
                    timestamp_column='timestamp'
                )
                attribution_results[model] = result
                
                # Display top channels for this model
                top_channels = sorted(result.channel_attribution.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"     Top channels: {', '.join([f'{ch}: {weight:.1%}' for ch, weight in top_channels])}")
                
            except Exception as e:
                print(f"     ⚠️  {model} model failed: {e}")
        
        # Compare attribution models
        print(f"\n🔍 Attribution Model Comparison:")
        self._compare_attribution_models(attribution_results)
        
        return attribution_results
    
    def _compare_attribution_models(self, results):
        """Compare attribution models and show differences."""
        if not results:
            print("No attribution results to compare")
            return
        
        # Get all channels
        all_channels = set()
        for result in results.values():
            all_channels.update(result.channel_attribution.keys())
        
        print(f"   Model Attribution Comparison (Top 4 Channels):")
        print(f"   {'Model':<15} {'Channel 1':<12} {'Channel 2':<12} {'Channel 3':<12} {'Channel 4':<12}")
        print(f"   {'-'*15} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
        
        for model_name, result in results.items():
            attribution = result.channel_attribution
            top_4 = sorted(attribution.items(), key=lambda x: x[1], reverse=True)[:4]
            
            row = f"   {model_name:<15}"
            for i, (channel, weight) in enumerate(top_4):
                channel_display = f"{channel[:8]}:{weight:.1%}"
                row += f" {channel_display:<12}"
            
            print(row)
        
        # Calculate model consensus
        print(f"\n   Model Consensus Analysis:")
        channel_scores = {}
        for result in results.values():
            for channel, weight in result.channel_attribution.items():
                if channel not in channel_scores:
                    channel_scores[channel] = []
                channel_scores[channel].append(weight)
        
        consensus_attribution = {}
        for channel, scores in channel_scores.items():
            consensus_attribution[channel] = {
                'avg_attribution': np.mean(scores),
                'std_attribution': np.std(scores),
                'agreement_score': 1 - (np.std(scores) / np.mean(scores)) if np.mean(scores) > 0 else 0
            }
        
        # Display consensus results
        sorted_consensus = sorted(consensus_attribution.items(), 
                                key=lambda x: x[1]['avg_attribution'], reverse=True)
        
        for channel, metrics in sorted_consensus:
            avg_attr = metrics['avg_attribution']
            agreement = metrics['agreement_score']
            print(f"   • {channel.title()}: {avg_attr:.1%} attribution (agreement: {agreement:.1%})")
    
    def _analyze_campaign_roi(self, customer_data, campaign_spend):
        """Analyze campaign ROI and performance."""
        print("Analyzing campaign ROI and effectiveness...")
        
        # Aggregate spend data by campaign
        campaign_spend_agg = campaign_spend.groupby('campaign_id').agg({
            'spend': 'sum',
            'channel': 'first',
            'campaign_type': 'first'
        }).reset_index()
        
        # Analyze campaign ROI using attribution analyzer
        try:
            roi_results = self.marketing_domain.attribution_analyzer.analyze_campaign_roi(
                data=customer_data,
                spend_data=campaign_spend_agg,
                campaign_column='campaign_id',
                spend_column='spend',
                revenue_column='revenue'
            )
            
            print(f"✓ Analyzed ROI for {len(roi_results)} campaigns")
            
            # Display top performing campaigns
            sorted_campaigns = sorted(roi_results.items(), key=lambda x: x[1].roi, reverse=True)
            
            print(f"\n💰 Top 5 Campaigns by ROI:")
            print(f"   {'Campaign':<20} {'Spend':<12} {'Conv':<8} {'Revenue':<12} {'ROI':<8} {'CPA':<10}")
            print(f"   {'-'*20} {'-'*12} {'-'*8} {'-'*12} {'-'*8} {'-'*10}")
            
            for campaign_id, metrics in sorted_campaigns[:5]:
                print(f"   {campaign_id:<20} ${metrics.total_spend:<11,.0f} "
                      f"{metrics.total_conversions:<8} ${metrics.total_revenue:<11,.0f} "
                      f"{metrics.roi:<8.1f} ${metrics.cost_per_acquisition:<9.0f}")
            
            # Channel-level ROI analysis
            print(f"\n📊 ROI by Channel:")
            channel_roi = {}
            for campaign_id, metrics in roi_results.items():
                # Get channel from campaign name (simplified)
                channel = campaign_id.split('_')[0] if '_' in campaign_id else 'unknown'
                if channel not in channel_roi:
                    channel_roi[channel] = {'spend': 0, 'revenue': 0, 'conversions': 0}
                
                channel_roi[channel]['spend'] += metrics.total_spend
                channel_roi[channel]['revenue'] += metrics.total_revenue
                channel_roi[channel]['conversions'] += metrics.total_conversions
            
            for channel, metrics in channel_roi.items():
                roi = (metrics['revenue'] - metrics['spend']) / metrics['spend'] if metrics['spend'] > 0 else 0
                cpa = metrics['spend'] / metrics['conversions'] if metrics['conversions'] > 0 else 0
                print(f"   • {channel.title()}: ROI {roi:.1f}x, CPA ${cpa:.0f}")
            
            return roi_results
            
        except Exception as e:
            print(f"⚠️  ROI analysis failed: {e}")
            return {}
    
    def _run_advanced_scenarios(self):
        """Run advanced attribution scenario analysis."""
        print("Running advanced attribution scenarios...")
        
        scenario_results = {}
        
        # Test different attribution scenarios
        scenarios = ['simple', 'complex_journey', 'display_assisted']
        
        for scenario in scenarios:
            try:
                print(f"   Testing {scenario} scenario...")
                
                # Generate scenario data
                scenario_data, true_attribution = self.marketing_domain.data_generator.generate_cross_channel_scenario(
                    scenario_type=scenario,
                    n_customers=5000
                )
                
                # Run attribution analysis
                result = self.marketing_domain.analyze_attribution(
                    scenario_data,
                    model='data_driven'
                )
                
                scenario_results[scenario] = {
                    'predicted_attribution': result.channel_attribution,
                    'true_attribution': true_attribution,
                    'data_size': len(scenario_data)
                }
                
                # Compare predicted vs. true attribution
                print(f"     Data size: {len(scenario_data):,} touchpoints")
                if true_attribution:
                    print(f"     Attribution accuracy analysis:")
                    for channel in true_attribution:
                        predicted = result.channel_attribution.get(channel, 0)
                        actual = true_attribution[channel]
                        accuracy = 1 - abs(predicted - actual) / actual if actual > 0 else 0
                        print(f"       • {channel}: Predicted {predicted:.1%}, Actual {actual:.1%}, Accuracy {accuracy:.1%}")
                
            except Exception as e:
                print(f"     ⚠️  {scenario} scenario failed: {e}")
        
        return scenario_results
    
    def _demonstrate_performance_features(self, data):
        """Demonstrate performance optimization features."""
        print("Demonstrating performance optimization features...")
        
        performance_results = {}
        
        # 1. Data chunking demo
        print("   Testing data chunking for large datasets...")
        try:
            from causallm.core.data_processing import DataChunker
            
            chunker = DataChunker()
            chunk_count = 0
            
            for chunk_idx, chunk_data in chunker.chunk_dataframe(data, chunk_size=10000):
                chunk_count += 1
                if chunk_count <= 3:  # Process first 3 chunks as demo
                    chunk_result = self.marketing_domain.analyze_attribution(
                        chunk_data,
                        model='linear'
                    )
                    print(f"     Chunk {chunk_idx}: {len(chunk_data):,} rows, "
                          f"top channel: {max(chunk_result.channel_attribution.items(), key=lambda x: x[1])}")
            
            performance_results['chunking'] = f"Successfully processed {chunk_count} chunks"
            
        except Exception as e:
            print(f"     ⚠️  Chunking demo failed: {e}")
        
        # 2. Caching demo
        print("   Testing caching performance...")
        try:
            import time
            
            # First run (no cache)
            start_time = time.time()
            result1 = self.marketing_domain.analyze_attribution(data[:5000], model='time_decay')
            first_run_time = time.time() - start_time
            
            # Second run (with cache)
            start_time = time.time()
            result2 = self.marketing_domain.analyze_attribution(data[:5000], model='time_decay')
            second_run_time = time.time() - start_time
            
            speedup = first_run_time / second_run_time if second_run_time > 0 else 1
            print(f"     First run: {first_run_time:.2f}s, Second run: {second_run_time:.2f}s")
            print(f"     Speedup: {speedup:.1f}x")
            
            performance_results['caching'] = f"{speedup:.1f}x speedup"
            
        except Exception as e:
            print(f"     ⚠️  Caching demo failed: {e}")
        
        # 3. Async processing demo (if available)
        print("   Testing async processing...")
        try:
            # Compare multiple models asynchronously
            models_to_compare = ['first_touch', 'last_touch', 'linear']
            
            start_time = time.time()
            comparison_results = self.marketing_domain.attribution_analyzer.compare_attribution_models(
                data[:10000],
                models=models_to_compare
            )
            async_time = time.time() - start_time
            
            print(f"     Compared {len(models_to_compare)} models in {async_time:.2f}s")
            print(f"     Models completed: {list(comparison_results.keys())}")
            
            performance_results['async_processing'] = f"Processed {len(comparison_results)} models"
            
        except Exception as e:
            print(f"     ⚠️  Async processing demo failed: {e}")
        
        return performance_results
    
    def _generate_business_insights(self, attribution_results, roi_analysis, scenario_analysis):
        """Generate business insights and recommendations."""
        print("Generating business insights and recommendations...")
        
        insights = {
            'channel_recommendations': [],
            'budget_optimizations': [],
            'measurement_recommendations': [],
            'performance_insights': []
        }
        
        # Channel performance insights
        if attribution_results:
            # Find most consistent channel across models
            channel_consistency = {}
            for model_name, result in attribution_results.items():
                for channel, weight in result.channel_attribution.items():
                    if channel not in channel_consistency:
                        channel_consistency[channel] = []
                    channel_consistency[channel].append(weight)
            
            most_consistent_channels = []
            for channel, weights in channel_consistency.items():
                if len(weights) > 1:
                    consistency_score = 1 - (np.std(weights) / np.mean(weights))
                    if consistency_score > 0.7:  # High consistency
                        most_consistent_channels.append((channel, np.mean(weights), consistency_score))
            
            if most_consistent_channels:
                top_consistent = sorted(most_consistent_channels, key=lambda x: x[1], reverse=True)[0]
                insights['channel_recommendations'].append(
                    f"Invest more in {top_consistent[0]} - shows consistent {top_consistent[1]:.1%} attribution across models"
                )
        
        # ROI-based recommendations
        if roi_analysis:
            high_roi_campaigns = [campaign for campaign, metrics in roi_analysis.items() if metrics.roi > 3.0]
            low_roi_campaigns = [campaign for campaign, metrics in roi_analysis.items() if metrics.roi < 1.0]
            
            if high_roi_campaigns:
                insights['budget_optimizations'].append(
                    f"Scale budget for {len(high_roi_campaigns)} high-ROI campaigns (ROI > 3.0x)"
                )
            
            if low_roi_campaigns:
                insights['budget_optimizations'].append(
                    f"Review or pause {len(low_roi_campaigns)} low-ROI campaigns (ROI < 1.0x)"
                )
        
        # Measurement recommendations
        insights['measurement_recommendations'].extend([
            "Implement view-through attribution for display campaigns",
            "Set up incrementality testing for brand channels",
            "Use longer attribution windows for high-consideration products",
            "Consider data-driven attribution for complex customer journeys"
        ])
        
        # Performance insights
        total_touchpoints = sum(len(data) for data in [attribution_results.get('linear', {}).attribution_weights] if hasattr(attribution_results.get('linear', {}), 'attribution_weights'))
        if total_touchpoints:
            insights['performance_insights'].append(
                f"Analyzed {total_touchpoints:,} touchpoints with performance optimizations"
            )
        
        # Display insights
        print("✓ Generated business insights:")
        for category, recommendations in insights.items():
            if recommendations:
                print(f"\n   {category.replace('_', ' ').title()}:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"     {i}. {rec}")
        
        return insights
    
    def _generate_executive_summary(self, attribution_results, roi_analysis, insights):
        """Generate executive summary of the analysis."""
        print("📊 EXECUTIVE SUMMARY")
        print("=" * 60)
        
        # Key metrics summary
        total_models_tested = len(attribution_results)
        total_campaigns_analyzed = len(roi_analysis)
        
        print(f"Analysis Scope:")
        print(f"• Attribution Models Tested: {total_models_tested}")
        print(f"• Campaigns Analyzed: {total_campaigns_analyzed}")
        print(f"• Dataset Size: {self.demo_config['n_touchpoints']:,} touchpoints")
        print(f"• Time Period: {self.demo_config['date_range_days']} days")
        
        # Top findings
        print(f"\n🔍 Key Findings:")
        
        if attribution_results:
            # Find model with highest confidence
            best_model = max(attribution_results.items(), 
                           key=lambda x: x[1].model_performance.get('model_accuracy', 0))
            print(f"• Best Performing Model: {best_model[0]} (accuracy: {best_model[1].model_performance.get('model_accuracy', 0):.1%})")
            
            # Top attributed channel
            top_channel = max(best_model[1].channel_attribution.items(), key=lambda x: x[1])
            print(f"• Highest Attribution Channel: {top_channel[0]} ({top_channel[1]:.1%})")
        
        if roi_analysis:
            # ROI distribution
            roi_values = [metrics.roi for metrics in roi_analysis.values()]
            avg_roi = np.mean(roi_values)
            profitable_campaigns = sum(1 for roi in roi_values if roi > 1.0)
            print(f"• Average Campaign ROI: {avg_roi:.1f}x")
            print(f"• Profitable Campaigns: {profitable_campaigns}/{len(roi_analysis)} ({profitable_campaigns/len(roi_analysis):.1%})")
        
        # Recommendations summary
        print(f"\n💡 Top Recommendations:")
        all_recommendations = []
        for category, recs in insights.items():
            all_recommendations.extend(recs[:2])  # Top 2 from each category
        
        for i, rec in enumerate(all_recommendations[:5], 1):  # Top 5 overall
            print(f"{i}. {rec}")
        
        print(f"\n✅ Analysis completed successfully with performance optimizations enabled!")
        print("=" * 60)


def main():
    """Main function to run the marketing attribution demo."""
    try:
        # Create and run the demo
        demo = MarketingAttributionDemo()
        demo.run_complete_demo()
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext Steps:")
        print("1. Try with your own marketing data")
        print("2. Experiment with different attribution models")
        print("3. Set up automated attribution reporting")
        print("4. Implement incrementality testing")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()