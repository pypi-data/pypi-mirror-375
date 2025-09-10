"""
Campaign Analysis Template

Provides pre-built analysis templates for marketing campaign effectiveness,
ROI measurement, and performance optimization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class CampaignAnalysisResult:
    """Results from campaign analysis."""
    analysis_type: str
    campaign_performance: Dict[str, Any]
    recommendations: List[str]
    key_metrics: Dict[str, float]
    channel_breakdown: Dict[str, Dict[str, float]]
    statistical_significance: Dict[str, float]

class CampaignAnalysisTemplate:
    """
    Pre-built templates for common campaign analysis scenarios.
    
    Available Templates:
    - campaign_effectiveness: Overall campaign performance analysis
    - roi_optimization: ROI-focused analysis with budget recommendations
    - channel_comparison: Cross-channel performance comparison
    - seasonal_analysis: Time-based performance analysis
    - audience_segmentation: Performance by audience segments
    """
    
    def __init__(self):
        """Initialize campaign analysis templates."""
        self.templates = {
            'campaign_effectiveness': self._analyze_campaign_effectiveness,
            'roi_optimization': self._analyze_roi_optimization,
            'channel_comparison': self._analyze_channel_comparison,
            'seasonal_analysis': self._analyze_seasonal_patterns,
            'audience_segmentation': self._analyze_audience_segments
        }
    
    def get_available_templates(self) -> List[str]:
        """Get list of available analysis templates."""
        return list(self.templates.keys())
    
    def run_analysis(
        self,
        template_name: str,
        data: pd.DataFrame,
        **kwargs
    ) -> CampaignAnalysisResult:
        """
        Run specified campaign analysis template.
        
        Args:
            template_name: Name of analysis template
            data: Campaign data DataFrame
            **kwargs: Template-specific parameters
            
        Returns:
            CampaignAnalysisResult with analysis findings
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {self.get_available_templates()}")
        
        return self.templates[template_name](data, **kwargs)
    
    def _analyze_campaign_effectiveness(
        self,
        data: pd.DataFrame,
        campaign_column: str = 'campaign_id',
        conversion_column: str = 'conversion',
        revenue_column: str = 'revenue',
        cost_column: str = 'estimated_cost',
        **kwargs
    ) -> CampaignAnalysisResult:
        """Analyze overall campaign effectiveness."""
        
        # Calculate campaign-level metrics
        campaign_metrics = data.groupby(campaign_column).agg({
            conversion_column: ['sum', 'count', 'mean'],
            revenue_column: 'sum',
            cost_column: 'sum'
        }).round(3)
        
        campaign_metrics.columns = ['conversions', 'impressions', 'conversion_rate', 'revenue', 'cost']
        
        # Calculate derived metrics
        campaign_metrics['roi'] = (campaign_metrics['revenue'] - campaign_metrics['cost']) / campaign_metrics['cost']
        campaign_metrics['cpa'] = campaign_metrics['cost'] / campaign_metrics['conversions'].replace(0, np.inf)
        campaign_metrics['roas'] = campaign_metrics['revenue'] / campaign_metrics['cost']
        
        # Identify top performers
        top_campaigns_by_roi = campaign_metrics.nlargest(5, 'roi')
        top_campaigns_by_conversions = campaign_metrics.nlargest(5, 'conversions')
        
        # Generate recommendations
        recommendations = self._generate_effectiveness_recommendations(campaign_metrics)
        
        # Key overall metrics
        key_metrics = {
            'total_campaigns': len(campaign_metrics),
            'total_spend': campaign_metrics['cost'].sum(),
            'total_conversions': campaign_metrics['conversions'].sum(),
            'total_revenue': campaign_metrics['revenue'].sum(),
            'overall_roi': (campaign_metrics['revenue'].sum() - campaign_metrics['cost'].sum()) / campaign_metrics['cost'].sum(),
            'avg_conversion_rate': campaign_metrics['conversion_rate'].mean(),
            'profitable_campaigns_pct': (campaign_metrics['roi'] > 0).mean() * 100
        }
        
        # Channel breakdown if available
        channel_breakdown = {}
        if 'channel' in data.columns:
            channel_breakdown = self._calculate_channel_breakdown(data, campaign_column)
        
        # Statistical significance tests
        significance_tests = self._calculate_statistical_significance(campaign_metrics)
        
        return CampaignAnalysisResult(
            analysis_type='campaign_effectiveness',
            campaign_performance={
                'all_campaigns': campaign_metrics.to_dict('index'),
                'top_roi_campaigns': top_campaigns_by_roi.to_dict('index'),
                'top_conversion_campaigns': top_campaigns_by_conversions.to_dict('index')
            },
            recommendations=recommendations,
            key_metrics=key_metrics,
            channel_breakdown=channel_breakdown,
            statistical_significance=significance_tests
        )
    
    def _analyze_roi_optimization(
        self,
        data: pd.DataFrame,
        spend_data: Optional[pd.DataFrame] = None,
        target_roi: float = 2.0,
        **kwargs
    ) -> CampaignAnalysisResult:
        """Analyze ROI and provide optimization recommendations."""
        
        campaign_column = kwargs.get('campaign_column', 'campaign_id')
        
        # Calculate current ROI performance
        campaign_metrics = data.groupby(campaign_column).agg({
            'conversion': 'sum',
            'revenue': 'sum',
            'estimated_cost': 'sum'
        })
        
        campaign_metrics['current_roi'] = (
            campaign_metrics['revenue'] - campaign_metrics['estimated_cost']
        ) / campaign_metrics['estimated_cost']
        
        # Identify optimization opportunities
        underperforming = campaign_metrics[campaign_metrics['current_roi'] < target_roi]
        high_performers = campaign_metrics[campaign_metrics['current_roi'] >= target_roi * 1.5]
        
        # Budget reallocation recommendations
        budget_recommendations = self._generate_budget_recommendations(
            campaign_metrics, target_roi
        )
        
        recommendations = [
            f"Pause {len(underperforming)} campaigns with ROI below {target_roi}",
            f"Increase budget for {len(high_performers)} high-performing campaigns",
            "Reallocate budget from underperforming to high-performing campaigns"
        ] + budget_recommendations
        
        key_metrics = {
            'campaigns_meeting_target': (campaign_metrics['current_roi'] >= target_roi).sum(),
            'campaigns_below_target': (campaign_metrics['current_roi'] < target_roi).sum(),
            'potential_savings': underperforming['estimated_cost'].sum(),
            'avg_roi_gap': target_roi - campaign_metrics[campaign_metrics['current_roi'] < target_roi]['current_roi'].mean()
        }
        
        return CampaignAnalysisResult(
            analysis_type='roi_optimization',
            campaign_performance={
                'underperforming_campaigns': underperforming.to_dict('index'),
                'high_performing_campaigns': high_performers.to_dict('index')
            },
            recommendations=recommendations,
            key_metrics=key_metrics,
            channel_breakdown={},
            statistical_significance={}
        )
    
    def _analyze_channel_comparison(
        self,
        data: pd.DataFrame,
        channel_column: str = 'channel',
        **kwargs
    ) -> CampaignAnalysisResult:
        """Compare performance across marketing channels."""
        
        # Channel-level performance
        channel_metrics = data.groupby(channel_column).agg({
            'conversion': ['sum', 'count', 'mean'],
            'revenue': 'sum',
            'estimated_cost': 'sum',
            'time_on_site': 'mean',
            'pages_viewed': 'mean'
        }).round(3)
        
        channel_metrics.columns = [
            'conversions', 'touchpoints', 'conversion_rate',
            'revenue', 'cost', 'avg_time_on_site', 'avg_pages_viewed'
        ]
        
        # Calculate efficiency metrics
        channel_metrics['roi'] = (channel_metrics['revenue'] - channel_metrics['cost']) / channel_metrics['cost']
        channel_metrics['cpc'] = channel_metrics['cost'] / channel_metrics['touchpoints']
        channel_metrics['cpa'] = channel_metrics['cost'] / channel_metrics['conversions'].replace(0, np.inf)
        channel_metrics['revenue_per_touchpoint'] = channel_metrics['revenue'] / channel_metrics['touchpoints']
        
        # Rank channels by different metrics
        rankings = {
            'roi_rank': channel_metrics['roi'].rank(ascending=False),
            'conversion_rate_rank': channel_metrics['conversion_rate'].rank(ascending=False),
            'volume_rank': channel_metrics['touchpoints'].rank(ascending=False),
            'efficiency_rank': channel_metrics['revenue_per_touchpoint'].rank(ascending=False)
        }
        
        # Generate channel-specific recommendations
        recommendations = self._generate_channel_recommendations(channel_metrics)
        
        # Overall channel insights
        best_roi_channel = channel_metrics['roi'].idxmax()
        best_volume_channel = channel_metrics['touchpoints'].idxmax()
        most_efficient_channel = channel_metrics['revenue_per_touchpoint'].idxmax()
        
        key_metrics = {
            'total_channels': len(channel_metrics),
            'best_roi_channel': best_roi_channel,
            'best_roi_value': channel_metrics.loc[best_roi_channel, 'roi'],
            'highest_volume_channel': best_volume_channel,
            'most_efficient_channel': most_efficient_channel,
            'channel_diversity_score': self._calculate_channel_diversity(channel_metrics)
        }
        
        return CampaignAnalysisResult(
            analysis_type='channel_comparison',
            campaign_performance={
                'channel_metrics': channel_metrics.to_dict('index'),
                'channel_rankings': pd.DataFrame(rankings).to_dict('index')
            },
            recommendations=recommendations,
            key_metrics=key_metrics,
            channel_breakdown=channel_metrics.to_dict('index'),
            statistical_significance=self._test_channel_significance(data, channel_column)
        )
    
    def _analyze_seasonal_patterns(
        self,
        data: pd.DataFrame,
        timestamp_column: str = 'timestamp',
        **kwargs
    ) -> CampaignAnalysisResult:
        """Analyze seasonal and temporal patterns in campaign performance."""
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(data[timestamp_column]):
            data[timestamp_column] = pd.to_datetime(data[timestamp_column])
        
        # Add time-based features
        data_temporal = data.copy()
        data_temporal['day_of_week'] = data_temporal[timestamp_column].dt.day_name()
        data_temporal['hour'] = data_temporal[timestamp_column].dt.hour
        data_temporal['month'] = data_temporal[timestamp_column].dt.month
        data_temporal['week'] = data_temporal[timestamp_column].dt.isocalendar().week
        
        # Analyze patterns by different time periods
        patterns = {}
        
        # Day of week patterns
        dow_patterns = data_temporal.groupby('day_of_week').agg({
            'conversion': ['sum', 'mean'],
            'revenue': 'sum',
            'estimated_cost': 'sum'
        }).round(3)
        patterns['day_of_week'] = dow_patterns
        
        # Hourly patterns
        hourly_patterns = data_temporal.groupby('hour').agg({
            'conversion': ['sum', 'mean'],
            'revenue': 'sum'
        }).round(3)
        patterns['hourly'] = hourly_patterns
        
        # Weekly trends
        weekly_patterns = data_temporal.groupby('week').agg({
            'conversion': ['sum', 'mean'],
            'revenue': 'sum',
            'estimated_cost': 'sum'
        }).round(3)
        patterns['weekly'] = weekly_patterns
        
        # Generate temporal insights
        recommendations = self._generate_temporal_recommendations(patterns)
        
        # Key insights
        best_day = dow_patterns[('conversion', 'mean')].idxmax()
        best_hour = hourly_patterns[('conversion', 'mean')].idxmax()
        
        key_metrics = {
            'best_performing_day': best_day,
            'best_performing_hour': int(best_hour),
            'weekday_vs_weekend_uplift': self._calculate_weekday_weekend_uplift(data_temporal),
            'peak_hour_conversion_rate': float(hourly_patterns.loc[best_hour, ('conversion', 'mean')]),
            'seasonal_variance': float(weekly_patterns[('conversion', 'mean')].std())
        }
        
        return CampaignAnalysisResult(
            analysis_type='seasonal_analysis',
            campaign_performance={
                'temporal_patterns': {k: v.to_dict('index') for k, v in patterns.items()}
            },
            recommendations=recommendations,
            key_metrics=key_metrics,
            channel_breakdown={},
            statistical_significance={}
        )
    
    def _analyze_audience_segments(
        self,
        data: pd.DataFrame,
        segment_column: str = 'customer_segment',
        **kwargs
    ) -> CampaignAnalysisResult:
        """Analyze performance by audience segments."""
        
        if segment_column not in data.columns:
            # Create basic segments based on engagement
            data = data.copy()
            data['engagement_score'] = (
                data.get('time_on_site', 0) * 0.3 +
                data.get('pages_viewed', 0) * 0.7
            )
            data[segment_column] = pd.qcut(
                data['engagement_score'], 
                q=3, 
                labels=['low_engagement', 'medium_engagement', 'high_engagement']
            )
        
        # Segment performance analysis
        segment_metrics = data.groupby(segment_column).agg({
            'conversion': ['sum', 'count', 'mean'],
            'revenue': 'sum',
            'estimated_cost': 'sum'
        }).round(3)
        
        segment_metrics.columns = ['conversions', 'touchpoints', 'conversion_rate', 'revenue', 'cost']
        segment_metrics['roi'] = (segment_metrics['revenue'] - segment_metrics['cost']) / segment_metrics['cost']
        segment_metrics['ltv'] = segment_metrics['revenue'] / segment_metrics['conversions'].replace(0, np.inf)
        
        # Segment recommendations
        recommendations = self._generate_segment_recommendations(segment_metrics)
        
        # Best performing segment
        best_segment = segment_metrics['roi'].idxmax()
        
        key_metrics = {
            'total_segments': len(segment_metrics),
            'best_performing_segment': best_segment,
            'segment_roi_range': segment_metrics['roi'].max() - segment_metrics['roi'].min(),
            'high_value_segment_share': segment_metrics.loc[best_segment, 'touchpoints'] / segment_metrics['touchpoints'].sum()
        }
        
        return CampaignAnalysisResult(
            analysis_type='audience_segmentation',
            campaign_performance={
                'segment_metrics': segment_metrics.to_dict('index')
            },
            recommendations=recommendations,
            key_metrics=key_metrics,
            channel_breakdown={},
            statistical_significance={}
        )
    
    def _generate_effectiveness_recommendations(self, metrics: pd.DataFrame) -> List[str]:
        """Generate recommendations based on campaign effectiveness analysis."""
        recommendations = []
        
        # ROI-based recommendations
        if (metrics['roi'] < 0).any():
            unprofitable_count = (metrics['roi'] < 0).sum()
            recommendations.append(f"Consider pausing {unprofitable_count} unprofitable campaigns")
        
        # Conversion rate recommendations
        low_cr_campaigns = metrics[metrics['conversion_rate'] < metrics['conversion_rate'].quantile(0.25)]
        if not low_cr_campaigns.empty:
            recommendations.append(f"Optimize creative/landing pages for {len(low_cr_campaigns)} low-converting campaigns")
        
        # Budget recommendations
        high_roi_campaigns = metrics[metrics['roi'] > metrics['roi'].quantile(0.75)]
        if not high_roi_campaigns.empty:
            recommendations.append(f"Increase budget for {len(high_roi_campaigns)} high-ROI campaigns")
        
        return recommendations
    
    def _generate_budget_recommendations(self, metrics: pd.DataFrame, target_roi: float) -> List[str]:
        """Generate specific budget reallocation recommendations."""
        recommendations = []
        
        total_budget = metrics['estimated_cost'].sum()
        high_performers = metrics[metrics['current_roi'] >= target_roi * 1.2]
        
        if not high_performers.empty:
            suggested_increase = min(0.3, len(high_performers) * 0.1)
            recommendations.append(
                f"Increase budget by {suggested_increase*100:.0f}% for top {len(high_performers)} campaigns"
            )
        
        return recommendations
    
    def _generate_channel_recommendations(self, metrics: pd.DataFrame) -> List[str]:
        """Generate channel-specific recommendations."""
        recommendations = []
        
        # High ROI, low volume channels
        high_roi_low_volume = metrics[
            (metrics['roi'] > metrics['roi'].median()) & 
            (metrics['touchpoints'] < metrics['touchpoints'].median())
        ]
        
        for channel in high_roi_low_volume.index:
            recommendations.append(f"Scale up {channel} - high ROI but low volume")
        
        # Low efficiency channels
        low_efficiency = metrics[metrics['revenue_per_touchpoint'] < metrics['revenue_per_touchpoint'].quantile(0.3)]
        for channel in low_efficiency.index:
            recommendations.append(f"Optimize {channel} - low revenue per touchpoint")
        
        return recommendations
    
    def _generate_temporal_recommendations(self, patterns: Dict[str, pd.DataFrame]) -> List[str]:
        """Generate time-based optimization recommendations."""
        recommendations = []
        
        # Day of week insights
        if 'day_of_week' in patterns:
            dow_data = patterns['day_of_week']
            best_day = dow_data[('conversion', 'mean')].idxmax()
            worst_day = dow_data[('conversion', 'mean')].idxmin()
            
            recommendations.append(f"Focus ad spend on {best_day} (highest conversion rate)")
            recommendations.append(f"Consider reducing spend on {worst_day} (lowest conversion rate)")
        
        # Hourly insights
        if 'hourly' in patterns:
            hourly_data = patterns['hourly']
            peak_hours = hourly_data[('conversion', 'mean')].nlargest(3).index.tolist()
            recommendations.append(f"Optimize for peak hours: {', '.join(map(str, peak_hours))}")
        
        return recommendations
    
    def _generate_segment_recommendations(self, metrics: pd.DataFrame) -> List[str]:
        """Generate audience segment recommendations."""
        recommendations = []
        
        best_segment = metrics['roi'].idxmax()
        worst_segment = metrics['roi'].idxmin()
        
        recommendations.extend([
            f"Increase targeting for {best_segment} segment (highest ROI)",
            f"Reduce or optimize {worst_segment} segment campaigns",
            "Create lookalike audiences based on high-performing segments"
        ])
        
        return recommendations
    
    def _calculate_channel_breakdown(self, data: pd.DataFrame, campaign_column: str) -> Dict[str, Dict[str, float]]:
        """Calculate performance breakdown by channel."""
        if 'channel' not in data.columns:
            return {}
        
        breakdown = data.groupby('channel').agg({
            'conversion': 'sum',
            'revenue': 'sum',
            'estimated_cost': 'sum'
        })
        
        return breakdown.to_dict('index')
    
    def _calculate_statistical_significance(self, metrics: pd.DataFrame) -> Dict[str, float]:
        """Calculate statistical significance of performance differences."""
        # Simplified significance testing
        significance = {}
        
        if len(metrics) > 1:
            # Test if conversion rates are significantly different
            conversion_rates = metrics['conversion_rate']
            significance['conversion_rate_variance'] = float(conversion_rates.var())
            significance['roi_correlation'] = float(metrics['roi'].corr(metrics['conversion_rate']))
        
        return significance
    
    def _test_channel_significance(self, data: pd.DataFrame, channel_column: str) -> Dict[str, float]:
        """Test statistical significance between channels."""
        # Simplified channel comparison
        significance = {}
        
        channels = data[channel_column].unique()
        if len(channels) > 1:
            channel_conversion_rates = data.groupby(channel_column)['conversion'].mean()
            significance['channel_variance'] = float(channel_conversion_rates.var())
        
        return significance
    
    def _calculate_channel_diversity(self, metrics: pd.DataFrame) -> float:
        """Calculate channel diversity score (0-1, higher = more diverse)."""
        touchpoint_shares = metrics['touchpoints'] / metrics['touchpoints'].sum()
        # Use inverse Herfindahl index for diversity
        hhi = (touchpoint_shares ** 2).sum()
        diversity_score = (1 - hhi) / (1 - 1/len(metrics)) if len(metrics) > 1 else 0
        return float(diversity_score)
    
    def _calculate_weekday_weekend_uplift(self, data: pd.DataFrame) -> float:
        """Calculate conversion rate uplift for weekdays vs weekends."""
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        weekends = ['Saturday', 'Sunday']
        
        weekday_rate = data[data['day_of_week'].isin(weekdays)]['conversion'].mean()
        weekend_rate = data[data['day_of_week'].isin(weekends)]['conversion'].mean()
        
        if weekend_rate > 0:
            uplift = (weekday_rate - weekend_rate) / weekend_rate
            return float(uplift)
        return 0.0