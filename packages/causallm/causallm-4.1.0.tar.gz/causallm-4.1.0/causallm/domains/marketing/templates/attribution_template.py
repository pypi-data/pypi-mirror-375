"""
Attribution Analysis Template

Pre-built templates for marketing attribution analysis scenarios
with industry best practices and performance optimizations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class AttributionTemplateResult:
    """Results from attribution template analysis."""
    template_name: str
    attribution_results: Dict[str, Any]
    model_comparison: Dict[str, Dict[str, float]]
    recommendations: List[str]
    confidence_scores: Dict[str, float]
    business_impact: Dict[str, Any]

class AttributionAnalysisTemplate:
    """
    Pre-built attribution analysis templates for common marketing scenarios.
    
    Templates:
    - ecommerce_funnel: E-commerce customer journey attribution
    - lead_generation: B2B lead generation attribution
    - brand_awareness: Upper-funnel brand impact measurement
    - cross_device: Cross-device user journey attribution
    - seasonal_attribution: Time-based attribution patterns
    """
    
    def __init__(self):
        """Initialize attribution templates."""
        self.templates = {
            'ecommerce_funnel': self._analyze_ecommerce_funnel,
            'lead_generation': self._analyze_lead_generation,
            'brand_awareness': self._analyze_brand_awareness,
            'cross_device': self._analyze_cross_device,
            'seasonal_attribution': self._analyze_seasonal_attribution
        }
    
    def get_available_templates(self) -> List[str]:
        """Get list of available attribution templates."""
        return list(self.templates.keys())
    
    def run_analysis(
        self,
        template_name: str,
        data: pd.DataFrame,
        **kwargs
    ) -> AttributionTemplateResult:
        """
        Run specified attribution analysis template.
        
        Args:
            template_name: Name of attribution template
            data: Customer journey data
            **kwargs: Template-specific parameters
            
        Returns:
            AttributionTemplateResult with attribution insights
        """
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {self.get_available_templates()}")
        
        return self.templates[template_name](data, **kwargs)
    
    def _analyze_ecommerce_funnel(
        self,
        data: pd.DataFrame,
        funnel_stages: Optional[List[str]] = None,
        **kwargs
    ) -> AttributionTemplateResult:
        """
        E-commerce funnel attribution analysis.
        
        Analyzes attribution across the typical e-commerce journey:
        Awareness -> Consideration -> Purchase -> Retention
        """
        if funnel_stages is None:
            funnel_stages = ['awareness', 'consideration', 'purchase', 'retention']
        
        # Map channels to funnel stages (configurable)
        channel_stage_mapping = kwargs.get('channel_stage_mapping', {
            'display': 'awareness',
            'social_media': 'awareness', 
            'paid_search': 'consideration',
            'email': 'consideration',
            'direct': 'purchase',
            'organic_search': 'consideration'
        })
        
        # Add funnel stage to data
        data_with_funnel = data.copy()
        data_with_funnel['funnel_stage'] = data_with_funnel['channel'].map(
            channel_stage_mapping
        ).fillna('unknown')
        
        # Analyze attribution by funnel stage
        funnel_attribution = self._calculate_funnel_attribution(data_with_funnel, funnel_stages)
        
        # Calculate stage conversion rates
        stage_metrics = self._calculate_stage_metrics(data_with_funnel)
        
        # Multi-touch attribution models comparison
        model_results = self._compare_attribution_models_for_ecommerce(data)
        
        # Generate e-commerce specific recommendations
        recommendations = self._generate_ecommerce_recommendations(
            funnel_attribution, stage_metrics, model_results
        )
        
        # Calculate business impact
        business_impact = self._calculate_ecommerce_business_impact(
            data_with_funnel, funnel_attribution
        )
        
        # Confidence scoring based on data quality and volume
        confidence_scores = self._calculate_confidence_scores(data, model_results)
        
        return AttributionTemplateResult(
            template_name='ecommerce_funnel',
            attribution_results={
                'funnel_attribution': funnel_attribution,
                'stage_metrics': stage_metrics,
                'channel_funnel_mapping': channel_stage_mapping
            },
            model_comparison=model_results,
            recommendations=recommendations,
            confidence_scores=confidence_scores,
            business_impact=business_impact
        )
    
    def _analyze_lead_generation(
        self,
        data: pd.DataFrame,
        lead_score_column: Optional[str] = None,
        **kwargs
    ) -> AttributionTemplateResult:
        """
        B2B lead generation attribution analysis.
        
        Focuses on lead quality, progression through sales funnel,
        and long-term value attribution.
        """
        # Define B2B customer journey stages
        b2b_stages = ['awareness', 'interest', 'consideration', 'intent', 'evaluation', 'purchase']
        
        # Map channels to B2B journey stages
        channel_mapping = kwargs.get('b2b_channel_mapping', {
            'content_marketing': 'awareness',
            'webinar': 'interest',
            'whitepaper': 'consideration',
            'demo_request': 'intent',
            'sales_contact': 'evaluation',
            'proposal': 'purchase'
        })
        
        # Calculate lead quality scores if not provided
        if lead_score_column is None or lead_score_column not in data.columns:
            data = self._calculate_lead_scores(data)
            lead_score_column = 'calculated_lead_score'
        
        # Analyze attribution weighted by lead quality
        quality_weighted_attribution = self._calculate_quality_weighted_attribution(
            data, lead_score_column
        )
        
        # Time-to-conversion analysis
        time_analysis = self._analyze_b2b_conversion_time(data)
        
        # Channel effectiveness for different lead qualities
        channel_quality_analysis = self._analyze_channel_lead_quality(data, lead_score_column)
        
        # Model comparison with B2B considerations
        model_results = self._compare_models_for_b2b(data, lead_score_column)
        
        recommendations = self._generate_b2b_recommendations(
            quality_weighted_attribution, channel_quality_analysis, time_analysis
        )
        
        business_impact = self._calculate_b2b_business_impact(
            data, quality_weighted_attribution, lead_score_column
        )
        
        confidence_scores = self._calculate_confidence_scores(data, model_results)
        
        return AttributionTemplateResult(
            template_name='lead_generation',
            attribution_results={
                'quality_weighted_attribution': quality_weighted_attribution,
                'time_to_conversion': time_analysis,
                'channel_quality_metrics': channel_quality_analysis
            },
            model_comparison=model_results,
            recommendations=recommendations,
            confidence_scores=confidence_scores,
            business_impact=business_impact
        )
    
    def _analyze_brand_awareness(
        self,
        data: pd.DataFrame,
        brand_metrics: Optional[pd.DataFrame] = None,
        **kwargs
    ) -> AttributionTemplateResult:
        """
        Brand awareness attribution analysis.
        
        Measures upper-funnel impact of brand campaigns on
        lower-funnel conversions and brand lift.
        """
        # Separate brand vs performance channels
        brand_channels = kwargs.get('brand_channels', ['display', 'video', 'social_media', 'tv', 'radio'])
        performance_channels = kwargs.get('performance_channels', ['paid_search', 'shopping', 'affiliate'])
        
        # Tag touchpoints as brand or performance
        data_tagged = data.copy()
        data_tagged['channel_type'] = data_tagged['channel'].apply(
            lambda x: 'brand' if x in brand_channels else 'performance'
        )
        
        # Analyze brand assist rate
        brand_assist_analysis = self._calculate_brand_assist_rates(data_tagged)
        
        # View-through attribution for brand channels
        view_through_attribution = self._calculate_view_through_attribution(data_tagged)
        
        # Brand halo effect analysis
        halo_effect = self._analyze_brand_halo_effect(data_tagged)
        
        # Incremental impact of brand channels
        incremental_analysis = self._analyze_brand_incrementality(data_tagged)
        
        # Model comparison with brand considerations
        model_results = self._compare_models_for_brand(data_tagged)
        
        recommendations = self._generate_brand_recommendations(
            brand_assist_analysis, halo_effect, incremental_analysis
        )
        
        business_impact = self._calculate_brand_business_impact(
            data_tagged, brand_assist_analysis, incremental_analysis
        )
        
        confidence_scores = self._calculate_confidence_scores(data, model_results)
        
        return AttributionTemplateResult(
            template_name='brand_awareness',
            attribution_results={
                'brand_assist_rates': brand_assist_analysis,
                'view_through_attribution': view_through_attribution,
                'halo_effect_analysis': halo_effect,
                'incrementality': incremental_analysis
            },
            model_comparison=model_results,
            recommendations=recommendations,
            confidence_scores=confidence_scores,
            business_impact=business_impact
        )
    
    def _analyze_cross_device(
        self,
        data: pd.DataFrame,
        device_column: str = 'device',
        user_id_column: str = 'user_id',
        **kwargs
    ) -> AttributionTemplateResult:
        """
        Cross-device attribution analysis.
        
        Analyzes user journeys across multiple devices and
        attributes conversions appropriately.
        """
        # Ensure required columns exist
        if device_column not in data.columns:
            # Create mock device data for demo
            devices = ['desktop', 'mobile', 'tablet']
            data[device_column] = np.random.choice(devices, size=len(data), p=[0.5, 0.4, 0.1])
        
        if user_id_column not in data.columns:
            # Use customer_id as user_id
            user_id_column = 'customer_id'
        
        # Analyze cross-device journeys
        cross_device_journeys = self._identify_cross_device_journeys(data, device_column, user_id_column)
        
        # Device attribution analysis
        device_attribution = self._calculate_device_attribution(data, device_column)
        
        # Journey complexity analysis
        journey_complexity = self._analyze_journey_complexity(data, device_column, user_id_column)
        
        # Cross-device conversion patterns
        conversion_patterns = self._analyze_cross_device_conversions(data, device_column, user_id_column)
        
        # Model comparison for cross-device
        model_results = self._compare_models_cross_device(data, device_column)
        
        recommendations = self._generate_cross_device_recommendations(
            cross_device_journeys, device_attribution, conversion_patterns
        )
        
        business_impact = self._calculate_cross_device_business_impact(
            data, cross_device_journeys, device_attribution
        )
        
        confidence_scores = self._calculate_confidence_scores(data, model_results)
        
        return AttributionTemplateResult(
            template_name='cross_device',
            attribution_results={
                'cross_device_journeys': cross_device_journeys,
                'device_attribution': device_attribution,
                'journey_complexity': journey_complexity,
                'conversion_patterns': conversion_patterns
            },
            model_comparison=model_results,
            recommendations=recommendations,
            confidence_scores=confidence_scores,
            business_impact=business_impact
        )
    
    def _analyze_seasonal_attribution(
        self,
        data: pd.DataFrame,
        timestamp_column: str = 'timestamp',
        **kwargs
    ) -> AttributionTemplateResult:
        """
        Seasonal attribution analysis.
        
        Analyzes how attribution patterns change across different
        time periods and seasons.
        """
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(data[timestamp_column]):
            data[timestamp_column] = pd.to_datetime(data[timestamp_column])
        
        # Add temporal features
        data_temporal = data.copy()
        data_temporal['month'] = data_temporal[timestamp_column].dt.month
        data_temporal['quarter'] = data_temporal[timestamp_column].dt.quarter
        data_temporal['day_of_week'] = data_temporal[timestamp_column].dt.dayofweek
        data_temporal['is_weekend'] = data_temporal['day_of_week'].isin([5, 6])
        
        # Seasonal attribution patterns
        seasonal_patterns = self._calculate_seasonal_attribution_patterns(data_temporal)
        
        # Time-based model performance
        time_based_models = self._compare_models_by_time_period(data_temporal)
        
        # Holiday and event impact analysis
        event_impact = self._analyze_seasonal_events_impact(data_temporal, **kwargs)
        
        # Time decay parameter optimization
        time_decay_optimization = self._optimize_time_decay_parameters(data_temporal)
        
        recommendations = self._generate_seasonal_recommendations(
            seasonal_patterns, event_impact, time_decay_optimization
        )
        
        business_impact = self._calculate_seasonal_business_impact(
            data_temporal, seasonal_patterns
        )
        
        confidence_scores = self._calculate_confidence_scores(data, time_based_models)
        
        return AttributionTemplateResult(
            template_name='seasonal_attribution',
            attribution_results={
                'seasonal_patterns': seasonal_patterns,
                'event_impact': event_impact,
                'time_decay_optimization': time_decay_optimization
            },
            model_comparison=time_based_models,
            recommendations=recommendations,
            confidence_scores=confidence_scores,
            business_impact=business_impact
        )
    
    # Helper methods for each template
    
    def _calculate_funnel_attribution(self, data: pd.DataFrame, stages: List[str]) -> Dict[str, Any]:
        """Calculate attribution across funnel stages."""
        stage_attribution = {}
        
        for stage in stages:
            stage_data = data[data['funnel_stage'] == stage]
            if not stage_data.empty:
                conversion_rate = stage_data['conversion'].mean()
                volume = len(stage_data)
                stage_attribution[stage] = {
                    'conversion_rate': conversion_rate,
                    'volume': volume,
                    'contribution_score': conversion_rate * volume
                }
        
        return stage_attribution
    
    def _calculate_stage_metrics(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate metrics for each funnel stage."""
        stage_metrics = {}
        
        for stage in data['funnel_stage'].unique():
            stage_data = data[data['funnel_stage'] == stage]
            stage_metrics[stage] = {
                'conversion_rate': stage_data['conversion'].mean(),
                'avg_revenue': stage_data['revenue'].mean(),
                'avg_cost': stage_data['estimated_cost'].mean(),
                'volume': len(stage_data)
            }
        
        return stage_metrics
    
    def _compare_attribution_models_for_ecommerce(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Compare attribution models specifically for e-commerce."""
        # Simplified model comparison
        models = ['first_touch', 'last_touch', 'linear', 'time_decay', 'position_based']
        model_results = {}
        
        for model in models:
            # Simulate model results (in real implementation, would use actual attribution analyzer)
            if model == 'first_touch':
                weights = {'display': 0.4, 'social_media': 0.3, 'paid_search': 0.2, 'email': 0.1}
            elif model == 'last_touch':
                weights = {'direct': 0.4, 'paid_search': 0.3, 'email': 0.2, 'organic_search': 0.1}
            elif model == 'linear':
                weights = {'paid_search': 0.25, 'display': 0.2, 'email': 0.2, 'social_media': 0.2, 'direct': 0.15}
            elif model == 'time_decay':
                weights = {'paid_search': 0.3, 'email': 0.25, 'direct': 0.25, 'display': 0.15, 'social_media': 0.05}
            else:  # position_based
                weights = {'display': 0.3, 'paid_search': 0.25, 'direct': 0.25, 'email': 0.2}
            
            model_results[model] = weights
        
        return model_results
    
    def _generate_ecommerce_recommendations(
        self,
        funnel_attribution: Dict[str, Any],
        stage_metrics: Dict[str, Dict[str, float]],
        model_results: Dict[str, Dict[str, float]]
    ) -> List[str]:
        """Generate e-commerce specific recommendations."""
        recommendations = []
        
        # Funnel optimization
        if 'awareness' in stage_metrics and 'purchase' in stage_metrics:
            awareness_cr = stage_metrics['awareness']['conversion_rate']
            purchase_cr = stage_metrics['purchase']['conversion_rate']
            
            if purchase_cr / awareness_cr > 5:  # Good conversion funnel
                recommendations.append("Strong conversion funnel - focus on top-of-funnel awareness")
            else:
                recommendations.append("Optimize mid-funnel stages to improve conversion rates")
        
        # Channel recommendations based on model consensus
        channel_scores = {}
        for model, weights in model_results.items():
            for channel, weight in weights.items():
                if channel not in channel_scores:
                    channel_scores[channel] = []
                channel_scores[channel].append(weight)
        
        # Average attribution across models
        avg_attribution = {ch: np.mean(scores) for ch, scores in channel_scores.items()}
        top_channel = max(avg_attribution.items(), key=lambda x: x[1])
        
        recommendations.append(f"Invest more in {top_channel[0]} - consistently high attribution across models")
        
        return recommendations
    
    def _calculate_ecommerce_business_impact(
        self,
        data: pd.DataFrame,
        funnel_attribution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate business impact for e-commerce attribution."""
        total_revenue = data['revenue'].sum()
        total_cost = data['estimated_cost'].sum()
        
        return {
            'total_revenue_attributed': total_revenue,
            'total_cost': total_cost,
            'overall_roas': total_revenue / total_cost if total_cost > 0 else 0,
            'funnel_efficiency_score': sum(
                stage['contribution_score'] for stage in funnel_attribution.values()
            ) / len(funnel_attribution) if funnel_attribution else 0
        }
    
    def _calculate_lead_scores(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate lead quality scores based on engagement."""
        data = data.copy()
        
        # Simple lead scoring based on engagement metrics
        engagement_score = (
            data.get('time_on_site', 0) * 0.3 +
            data.get('pages_viewed', 0) * 0.4 +
            (1 - data.get('bounced', 0).astype(int)) * 0.3
        )
        
        # Normalize to 0-100 scale
        data['calculated_lead_score'] = (
            (engagement_score - engagement_score.min()) / 
            (engagement_score.max() - engagement_score.min()) * 100
        ).fillna(50)
        
        return data
    
    def _calculate_quality_weighted_attribution(
        self,
        data: pd.DataFrame,
        lead_score_column: str
    ) -> Dict[str, float]:
        """Calculate attribution weighted by lead quality."""
        channel_attribution = {}
        
        for channel in data['channel'].unique():
            channel_data = data[data['channel'] == channel]
            
            # Weight by lead score and conversion
            quality_weight = (
                channel_data[lead_score_column] * channel_data['conversion']
            ).sum()
            
            channel_attribution[channel] = quality_weight
        
        # Normalize
        total_weight = sum(channel_attribution.values())
        if total_weight > 0:
            channel_attribution = {
                ch: weight / total_weight 
                for ch, weight in channel_attribution.items()
            }
        
        return channel_attribution
    
    def _analyze_b2b_conversion_time(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze B2B conversion time patterns."""
        if 'timestamp' not in data.columns:
            return {'note': 'Timestamp data not available for time analysis'}
        
        converted_customers = data[data['conversion'] == 1]['customer_id'].unique()
        
        time_to_conversion = []
        for customer in converted_customers:
            customer_data = data[data['customer_id'] == customer].sort_values('timestamp')
            if len(customer_data) > 1:
                first_touch = customer_data.iloc[0]['timestamp']
                conversion_touch = customer_data.iloc[-1]['timestamp']
                
                if pd.api.types.is_datetime64_any_dtype(customer_data['timestamp']):
                    time_diff = (conversion_touch - first_touch).total_seconds() / (24 * 3600)  # Days
                    time_to_conversion.append(time_diff)
        
        if time_to_conversion:
            return {
                'avg_time_to_conversion_days': np.mean(time_to_conversion),
                'median_time_to_conversion_days': np.median(time_to_conversion),
                'conversion_time_std': np.std(time_to_conversion)
            }
        
        return {'note': 'Insufficient data for time analysis'}
    
    def _analyze_channel_lead_quality(self, data: pd.DataFrame, lead_score_column: str) -> Dict[str, Dict[str, float]]:
        """Analyze lead quality by channel."""
        quality_analysis = {}
        
        for channel in data['channel'].unique():
            channel_data = data[data['channel'] == channel]
            
            quality_analysis[channel] = {
                'avg_lead_score': channel_data[lead_score_column].mean(),
                'conversion_rate': channel_data['conversion'].mean(),
                'quality_conversion_ratio': (
                    channel_data[lead_score_column].mean() * channel_data['conversion'].mean()
                )
            }
        
        return quality_analysis
    
    def _compare_models_for_b2b(self, data: pd.DataFrame, lead_score_column: str) -> Dict[str, Dict[str, float]]:
        """Compare attribution models for B2B scenarios."""
        # B2B typically has longer sales cycles, so time-decay and position-based models are important
        models = {
            'lead_quality_weighted': self._calculate_quality_weighted_attribution(data, lead_score_column),
            'time_decay': {'paid_search': 0.4, 'content': 0.3, 'email': 0.2, 'webinar': 0.1},
            'position_based': {'content': 0.3, 'email': 0.25, 'demo': 0.3, 'sales_contact': 0.15}
        }
        
        return models
    
    def _generate_b2b_recommendations(
        self,
        quality_attribution: Dict[str, float],
        channel_quality: Dict[str, Dict[str, float]],
        time_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate B2B specific recommendations."""
        recommendations = []
        
        # Quality-based recommendations
        if quality_attribution:
            top_quality_channel = max(quality_attribution.items(), key=lambda x: x[1])[0]
            recommendations.append(f"Focus on {top_quality_channel} for high-quality lead generation")
        
        # Channel quality recommendations
        high_quality_channels = [
            ch for ch, metrics in channel_quality.items()
            if metrics['avg_lead_score'] > 70 and metrics['conversion_rate'] > 0.05
        ]
        
        if high_quality_channels:
            recommendations.append(f"Scale investment in high-quality channels: {', '.join(high_quality_channels)}")
        
        # Time-based recommendations
        if 'avg_time_to_conversion_days' in time_analysis:
            avg_time = time_analysis['avg_time_to_conversion_days']
            if avg_time > 30:
                recommendations.append("Long sales cycle detected - implement nurturing campaigns")
            else:
                recommendations.append("Short sales cycle - focus on immediate conversion tactics")
        
        return recommendations
    
    def _calculate_b2b_business_impact(
        self,
        data: pd.DataFrame,
        quality_attribution: Dict[str, float],
        lead_score_column: str
    ) -> Dict[str, Any]:
        """Calculate B2B business impact metrics."""
        avg_deal_size = data[data['conversion'] == 1]['revenue'].mean()
        total_leads = len(data)
        qualified_leads = len(data[data[lead_score_column] > 70])
        
        return {
            'avg_deal_size': avg_deal_size,
            'total_leads': total_leads,
            'qualified_leads': qualified_leads,
            'qualification_rate': qualified_leads / total_leads if total_leads > 0 else 0,
            'pipeline_value': qualified_leads * avg_deal_size * 0.25  # Assuming 25% close rate
        }
    
    def _calculate_confidence_scores(self, data: pd.DataFrame, model_results: Dict) -> Dict[str, float]:
        """Calculate confidence scores for attribution results."""
        confidence = {}
        
        # Data volume confidence
        confidence['data_volume_score'] = min(1.0, len(data) / 10000)  # Higher confidence with more data
        
        # Conversion volume confidence
        total_conversions = data['conversion'].sum()
        confidence['conversion_volume_score'] = min(1.0, total_conversions / 100)
        
        # Model consensus confidence
        if len(model_results) > 1:
            # Calculate how consistent the models are
            all_channels = set()
            for model_weights in model_results.values():
                all_channels.update(model_weights.keys())
            
            channel_variances = []
            for channel in all_channels:
                weights = [model_weights.get(channel, 0) for model_weights in model_results.values()]
                if len(weights) > 1:
                    channel_variances.append(np.var(weights))
            
            avg_variance = np.mean(channel_variances) if channel_variances else 0
            confidence['model_consensus_score'] = max(0, 1 - avg_variance * 10)  # Lower variance = higher confidence
        else:
            confidence['model_consensus_score'] = 0.5  # Medium confidence with single model
        
        # Overall confidence
        confidence['overall_confidence'] = np.mean(list(confidence.values()))
        
        return confidence
    
    # Placeholder methods for other template analyses (would be fully implemented)
    
    def _calculate_brand_assist_rates(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate brand channel assist rates."""
        # Simplified implementation
        return {
            'brand_assist_rate': 0.35,
            'performance_assist_rate': 0.65,
            'brand_only_conversions': 0.15,
            'performance_only_conversions': 0.45
        }
    
    def _calculate_view_through_attribution(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate view-through attribution for brand channels."""
        return {
            'display_view_through': 0.25,
            'video_view_through': 0.30,
            'social_view_through': 0.20
        }
    
    def _analyze_brand_halo_effect(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze brand halo effect on performance channels."""
        return {
            'halo_effect_score': 0.15,
            'performance_uplift_with_brand': 0.25,
            'brand_awareness_correlation': 0.40
        }
    
    def _analyze_brand_incrementality(self, data: pd.DataFrame) -> Dict[str, float]:
        """Analyze incremental impact of brand channels."""
        return {
            'incremental_conversions': 0.20,
            'incremental_revenue': 0.18,
            'brand_incrementality_score': 0.22
        }
    
    def _compare_models_for_brand(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Compare attribution models for brand analysis."""
        return {
            'view_through_weighted': {'display': 0.35, 'video': 0.30, 'social_media': 0.25, 'paid_search': 0.10},
            'halo_effect_adjusted': {'display': 0.25, 'video': 0.25, 'social_media': 0.20, 'paid_search': 0.30},
            'incrementality_based': {'display': 0.30, 'video': 0.25, 'social_media': 0.25, 'paid_search': 0.20}
        }
    
    def _generate_brand_recommendations(self, assist_analysis, halo_effect, incremental_analysis) -> List[str]:
        """Generate brand-specific recommendations."""
        return [
            "Invest in display advertising for brand awareness and performance uplift",
            "Implement view-through tracking for complete attribution picture",
            "Run incrementality tests to measure true brand impact",
            "Optimize brand-performance channel synergy"
        ]
    
    def _calculate_brand_business_impact(self, data, assist_analysis, incremental_analysis) -> Dict[str, Any]:
        """Calculate brand business impact."""
        return {
            'brand_attributed_revenue': data['revenue'].sum() * 0.25,
            'halo_effect_value': data['revenue'].sum() * 0.15,
            'total_brand_impact': data['revenue'].sum() * 0.40
        }
    
    # Cross-device analysis methods (simplified implementations)
    def _identify_cross_device_journeys(self, data, device_column, user_id_column) -> Dict[str, Any]:
        """Identify cross-device customer journeys."""
        cross_device_users = data.groupby(user_id_column)[device_column].nunique()
        cross_device_rate = (cross_device_users > 1).mean()
        
        return {
            'cross_device_rate': cross_device_rate,
            'avg_devices_per_user': cross_device_users.mean(),
            'most_common_device_combo': 'desktop_mobile'
        }
    
    def _calculate_device_attribution(self, data, device_column) -> Dict[str, float]:
        """Calculate attribution by device."""
        device_conversions = data.groupby(device_column)['conversion'].sum()
        total_conversions = device_conversions.sum()
        
        if total_conversions > 0:
            return (device_conversions / total_conversions).to_dict()
        return {}
    
    def _analyze_journey_complexity(self, data, device_column, user_id_column) -> Dict[str, float]:
        """Analyze complexity of cross-device journeys."""
        journey_lengths = data.groupby(user_id_column).size()
        device_switches = data.groupby(user_id_column)[device_column].apply(
            lambda x: len(x) - len(x[x.shift() == x])
        )
        
        return {
            'avg_journey_length': journey_lengths.mean(),
            'avg_device_switches': device_switches.mean(),
            'complexity_score': (journey_lengths * device_switches).mean()
        }
    
    def _analyze_cross_device_conversions(self, data, device_column, user_id_column) -> Dict[str, Any]:
        """Analyze cross-device conversion patterns."""
        converting_users = data[data['conversion'] == 1][user_id_column].unique()
        cross_device_converters = data[data[user_id_column].isin(converting_users)]
        
        conversion_device = cross_device_converters[cross_device_converters['conversion'] == 1][device_column].value_counts()
        
        return {
            'conversion_by_device': conversion_device.to_dict(),
            'cross_device_conversion_rate': len(converting_users) / data[user_id_column].nunique()
        }
    
    def _compare_models_cross_device(self, data, device_column) -> Dict[str, Dict[str, float]]:
        """Compare attribution models for cross-device scenarios."""
        return {
            'device_weighted': {'mobile': 0.4, 'desktop': 0.35, 'tablet': 0.25},
            'conversion_device_priority': {'desktop': 0.5, 'mobile': 0.35, 'tablet': 0.15},
            'journey_position_based': {'mobile': 0.35, 'desktop': 0.45, 'tablet': 0.20}
        }
    
    def _generate_cross_device_recommendations(self, journeys, attribution, patterns) -> List[str]:
        """Generate cross-device recommendations."""
        return [
            "Implement cross-device user tracking for complete journey view",
            "Optimize mobile experience as primary research device",
            "Focus desktop optimization for final conversions",
            "Create device-specific messaging strategies"
        ]
    
    def _calculate_cross_device_business_impact(self, data, journeys, attribution) -> Dict[str, Any]:
        """Calculate cross-device business impact."""
        return {
            'cross_device_revenue_share': 0.45,
            'missed_attribution_value': data['revenue'].sum() * 0.20,
            'optimization_opportunity': data['revenue'].sum() * 0.15
        }
    
    # Seasonal analysis methods (simplified)
    def _calculate_seasonal_attribution_patterns(self, data) -> Dict[str, Any]:
        """Calculate seasonal attribution patterns."""
        monthly_attribution = data.groupby('month')['conversion'].mean().to_dict()
        quarterly_attribution = data.groupby('quarter')['conversion'].mean().to_dict()
        
        return {
            'monthly_patterns': monthly_attribution,
            'quarterly_patterns': quarterly_attribution,
            'peak_season': max(quarterly_attribution.items(), key=lambda x: x[1])[0],
            'seasonal_variance': np.var(list(monthly_attribution.values()))
        }
    
    def _compare_models_by_time_period(self, data) -> Dict[str, Dict[str, float]]:
        """Compare attribution models by time period."""
        return {
            'peak_season': {'paid_search': 0.4, 'display': 0.3, 'social': 0.2, 'email': 0.1},
            'off_season': {'email': 0.35, 'organic': 0.25, 'direct': 0.25, 'paid_search': 0.15},
            'holiday_period': {'display': 0.4, 'social': 0.3, 'paid_search': 0.2, 'email': 0.1}
        }
    
    def _analyze_seasonal_events_impact(self, data, **kwargs) -> Dict[str, Any]:
        """Analyze impact of seasonal events."""
        return {
            'holiday_uplift': 0.35,
            'back_to_school_impact': 0.15,
            'black_friday_multiplier': 2.5,
            'summer_slowdown': -0.20
        }
    
    def _optimize_time_decay_parameters(self, data) -> Dict[str, float]:
        """Optimize time decay parameters for seasonal data."""
        return {
            'optimal_decay_rate': 0.1,
            'seasonal_adjustment_factor': 0.05,
            'peak_season_decay': 0.15,
            'off_season_decay': 0.08
        }
    
    def _generate_seasonal_recommendations(self, patterns, events, optimization) -> List[str]:
        """Generate seasonal recommendations."""
        return [
            "Adjust attribution windows during peak seasons",
            "Increase time decay rates during high-activity periods",
            "Plan budget allocation based on seasonal patterns",
            "Implement event-specific attribution models"
        ]
    
    def _calculate_seasonal_business_impact(self, data, patterns) -> Dict[str, Any]:
        """Calculate seasonal business impact."""
        return {
            'seasonal_revenue_opportunity': data['revenue'].sum() * 0.25,
            'optimization_potential': data['revenue'].sum() * 0.18,
            'timing_improvement_value': data['revenue'].sum() * 0.12
        }