"""
Marketing Knowledge Base

Domain-specific knowledge for marketing attribution analysis including
industry benchmarks, best practices, and expert insights.
"""

from typing import Dict, List, Any, Optional
import pandas as pd

class MarketingKnowledge:
    """
    Marketing domain knowledge base with industry benchmarks,
    attribution best practices, and channel characteristics.
    """
    
    def __init__(self):
        """Initialize marketing knowledge base."""
        self.channel_characteristics = self._initialize_channel_characteristics()
        self.industry_benchmarks = self._initialize_industry_benchmarks()
        self.attribution_best_practices = self._initialize_attribution_best_practices()
        self.measurement_frameworks = self._initialize_measurement_frameworks()
    
    def get_channel_characteristics(self, channel: str) -> Dict[str, Any]:
        """Get characteristics for a specific marketing channel."""
        return self.channel_characteristics.get(channel, {})
    
    def get_industry_benchmarks(self, industry: str = 'general') -> Dict[str, float]:
        """Get industry benchmarks for key metrics."""
        return self.industry_benchmarks.get(industry, self.industry_benchmarks['general'])
    
    def get_attribution_recommendations(self, scenario: str) -> Dict[str, Any]:
        """Get attribution model recommendations for specific scenarios."""
        return self.attribution_best_practices.get(scenario, {})
    
    def get_measurement_framework(self, framework_name: str) -> Dict[str, Any]:
        """Get specific measurement framework details."""
        return self.measurement_frameworks.get(framework_name, {})
    
    def _initialize_channel_characteristics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize channel characteristics database."""
        return {
            'paid_search': {
                'type': 'performance',
                'intent_level': 'high',
                'typical_position': 'bottom_funnel',
                'attribution_strength': 'direct',
                'avg_cpc_range': (1.0, 4.0),
                'avg_conversion_rate': 0.03,
                'click_to_conversion_window': '1-7 days',
                'audience_targeting': 'keyword_based',
                'measurement_considerations': [
                    'Strong last-click attribution',
                    'Easy to measure direct impact',
                    'May undervalue assist role'
                ],
                'optimization_kpis': ['CPC', 'conversion_rate', 'ROAS', 'quality_score']
            },
            'display': {
                'type': 'brand_awareness',
                'intent_level': 'low',
                'typical_position': 'top_funnel',
                'attribution_strength': 'assist',
                'avg_cpc_range': (0.5, 2.0),
                'avg_conversion_rate': 0.008,
                'click_to_conversion_window': '1-30 days',
                'audience_targeting': 'demographic_behavioral',
                'measurement_considerations': [
                    'Strong assist role',
                    'View-through attribution important',
                    'Brand lift measurement needed'
                ],
                'optimization_kpis': ['CPM', 'viewability', 'brand_lift', 'assist_rate']
            },
            'social_media': {
                'type': 'engagement',
                'intent_level': 'medium',
                'typical_position': 'mid_funnel',
                'attribution_strength': 'assist',
                'avg_cpc_range': (0.8, 3.0),
                'avg_conversion_rate': 0.015,
                'click_to_conversion_window': '1-14 days',
                'audience_targeting': 'interest_lookalike',
                'measurement_considerations': [
                    'Strong engagement metrics',
                    'Social proof effects',
                    'Cross-platform attribution challenges'
                ],
                'optimization_kpis': ['engagement_rate', 'social_share', 'CTR', 'video_completion']
            },
            'email': {
                'type': 'retention',
                'intent_level': 'high',
                'typical_position': 'bottom_funnel',
                'attribution_strength': 'direct',
                'avg_cpc_range': (0.05, 0.20),
                'avg_conversion_rate': 0.05,
                'click_to_conversion_window': '1-3 days',
                'audience_targeting': 'owned_audience',
                'measurement_considerations': [
                    'High conversion rates',
                    'Strong last-click attribution',
                    'Lifetime value impact'
                ],
                'optimization_kpis': ['open_rate', 'click_rate', 'unsubscribe_rate', 'revenue_per_email']
            },
            'direct': {
                'type': 'brand',
                'intent_level': 'very_high',
                'typical_position': 'bottom_funnel',
                'attribution_strength': 'direct',
                'avg_cpc_range': (0.0, 0.0),
                'avg_conversion_rate': 0.08,
                'click_to_conversion_window': 'immediate',
                'audience_targeting': 'brand_familiar',
                'measurement_considerations': [
                    'Often influenced by other channels',
                    'Strong conversion rates',
                    'Brand equity indicator'
                ],
                'optimization_kpis': ['conversion_rate', 'brand_search_volume', 'repeat_visitor_rate']
            },
            'organic_search': {
                'type': 'content',
                'intent_level': 'high',
                'typical_position': 'mid_to_bottom_funnel',
                'attribution_strength': 'direct',
                'avg_cpc_range': (0.0, 0.0),
                'avg_conversion_rate': 0.04,
                'click_to_conversion_window': '1-7 days',
                'audience_targeting': 'intent_based',
                'measurement_considerations': [
                    'Long-term brand building',
                    'Content quality impact',
                    'SEO attribution challenges'
                ],
                'optimization_kpis': ['organic_traffic', 'keyword_rankings', 'click_through_rate']
            },
            'affiliate': {
                'type': 'performance',
                'intent_level': 'high',
                'typical_position': 'bottom_funnel',
                'attribution_strength': 'direct',
                'avg_cpc_range': (0.0, 0.0),  # Commission-based
                'avg_conversion_rate': 0.06,
                'click_to_conversion_window': '1-30 days',
                'audience_targeting': 'publisher_audience',
                'measurement_considerations': [
                    'Commission-based model',
                    'Attribution window importance',
                    'Partner quality variation'
                ],
                'optimization_kpis': ['conversion_rate', 'commission_rate', 'partner_quality', 'incremental_sales']
            }
        }
    
    def _initialize_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Initialize industry benchmark data."""
        return {
            'general': {
                'avg_conversion_rate': 0.025,
                'avg_cpc': 2.0,
                'avg_ctr': 0.02,
                'avg_roas': 4.0,
                'brand_awareness_lift': 0.15,
                'assisted_conversion_rate': 0.35
            },
            'ecommerce': {
                'avg_conversion_rate': 0.027,
                'avg_cpc': 1.8,
                'avg_ctr': 0.025,
                'avg_roas': 4.5,
                'cart_abandonment_rate': 0.70,
                'repeat_purchase_rate': 0.30,
                'avg_order_value': 85.0
            },
            'saas': {
                'avg_conversion_rate': 0.015,
                'avg_cpc': 3.5,
                'avg_ctr': 0.018,
                'avg_roas': 6.0,
                'trial_to_paid_rate': 0.15,
                'customer_lifetime_value': 2400.0,
                'churn_rate': 0.05
            },
            'finance': {
                'avg_conversion_rate': 0.012,
                'avg_cpc': 5.0,
                'avg_ctr': 0.015,
                'avg_roas': 8.0,
                'lead_to_customer_rate': 0.08,
                'avg_customer_value': 1500.0
            },
            'healthcare': {
                'avg_conversion_rate': 0.018,
                'avg_cpc': 4.2,
                'avg_ctr': 0.020,
                'avg_roas': 5.5,
                'appointment_show_rate': 0.75,
                'patient_lifetime_value': 3200.0
            },
            'education': {
                'avg_conversion_rate': 0.022,
                'avg_cpc': 2.8,
                'avg_ctr': 0.024,
                'avg_roas': 3.5,
                'enrollment_rate': 0.12,
                'completion_rate': 0.68
            }
        }
    
    def _initialize_attribution_best_practices(self) -> Dict[str, Dict[str, Any]]:
        """Initialize attribution best practices by scenario."""
        return {
            'ecommerce_short_cycle': {
                'recommended_models': ['last_touch', 'time_decay'],
                'attribution_window': '7-14 days',
                'key_considerations': [
                    'Short purchase consideration period',
                    'Focus on direct response channels',
                    'Strong last-touch attribution'
                ],
                'measurement_priorities': ['conversion_rate', 'ROAS', 'customer_acquisition_cost'],
                'model_weights': {
                    'last_touch': 0.4,
                    'time_decay': 0.35,
                    'data_driven': 0.25
                }
            },
            'ecommerce_long_cycle': {
                'recommended_models': ['position_based', 'data_driven', 'linear'],
                'attribution_window': '30-90 days',
                'key_considerations': [
                    'Extended research and consideration phase',
                    'Multiple touchpoints across funnel',
                    'Brand awareness important'
                ],
                'measurement_priorities': ['assisted_conversions', 'path_length', 'time_to_conversion'],
                'model_weights': {
                    'position_based': 0.35,
                    'data_driven': 0.4,
                    'linear': 0.25
                }
            },
            'b2b_lead_generation': {
                'recommended_models': ['time_decay', 'data_driven', 'position_based'],
                'attribution_window': '90-180 days',
                'key_considerations': [
                    'Long sales cycles',
                    'Multiple decision makers',
                    'Content marketing importance'
                ],
                'measurement_priorities': ['lead_quality', 'sales_qualified_leads', 'pipeline_velocity'],
                'model_weights': {
                    'time_decay': 0.3,
                    'data_driven': 0.45,
                    'position_based': 0.25
                }
            },
            'brand_awareness': {
                'recommended_models': ['view_through', 'linear', 'position_based'],
                'attribution_window': '30-60 days',
                'key_considerations': [
                    'Upper funnel impact measurement',
                    'View-through attribution critical',
                    'Brand lift studies needed'
                ],
                'measurement_priorities': ['brand_awareness_lift', 'assisted_conversions', 'reach'],
                'model_weights': {
                    'view_through': 0.4,
                    'linear': 0.3,
                    'position_based': 0.3
                }
            },
            'mobile_app': {
                'recommended_models': ['first_touch', 'time_decay'],
                'attribution_window': '1-7 days',
                'key_considerations': [
                    'Install vs. engagement attribution',
                    'Cross-device considerations',
                    'In-app event tracking'
                ],
                'measurement_priorities': ['install_rate', 'retention_rate', 'in_app_purchases'],
                'model_weights': {
                    'first_touch': 0.5,
                    'time_decay': 0.3,
                    'data_driven': 0.2
                }
            }
        }
    
    def _initialize_measurement_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize measurement frameworks."""
        return {
            'marketing_mix_modeling': {
                'description': 'Top-down statistical approach to measure marketing effectiveness',
                'best_for': ['Brand measurement', 'Media mix optimization', 'Budget allocation'],
                'requirements': ['2+ years of data', 'Varied spend levels', 'External factors data'],
                'advantages': [
                    'Measures all marketing activities',
                    'Accounts for external factors', 
                    'Good for budget optimization'
                ],
                'limitations': [
                    'Requires significant data',
                    'Less granular insights',
                    'Difficult to measure digital precisely'
                ],
                'typical_attribution_windows': '1-52 weeks'
            },
            'multi_touch_attribution': {
                'description': 'Bottom-up approach tracking individual customer journeys',
                'best_for': ['Digital marketing', 'Customer journey analysis', 'Channel optimization'],
                'requirements': ['User-level data', 'Cross-channel tracking', 'Conversion tracking'],
                'advantages': [
                    'Granular customer insights',
                    'Real-time optimization',
                    'Channel-specific ROI'
                ],
                'limitations': [
                    'Limited to trackable channels',
                    'Privacy restrictions',
                    'Attribution bias potential'
                ],
                'typical_attribution_windows': '1-90 days'
            },
            'incrementality_testing': {
                'description': 'Experimental approach using test/control groups',
                'best_for': ['Causal measurement', 'New channel testing', 'Budget decisions'],
                'requirements': ['Ability to run tests', 'Statistical significance', 'Control groups'],
                'advantages': [
                    'Measures true causality',
                    'Eliminates attribution bias',
                    'Scientific approach'
                ],
                'limitations': [
                    'Requires testing capability',
                    'Time-intensive',
                    'May impact performance'
                ],
                'typical_test_duration': '2-8 weeks'
            },
            'unified_measurement': {
                'description': 'Combined approach using multiple measurement methods',
                'best_for': ['Comprehensive measurement', 'Large advertisers', 'Complex attribution'],
                'requirements': ['Multiple data sources', 'Advanced analytics', 'Measurement expertise'],
                'advantages': [
                    'Most complete picture',
                    'Validates findings across methods',
                    'Reduces measurement bias'
                ],
                'limitations': [
                    'Complex to implement',
                    'Resource intensive',
                    'Requires expertise'
                ],
                'typical_implementation_time': '6-12 months'
            }
        }
    
    def get_attribution_window_recommendation(
        self,
        industry: str,
        business_model: str,
        avg_consideration_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get attribution window recommendations based on business characteristics.
        
        Args:
            industry: Business industry
            business_model: Business model (ecommerce, saas, b2b, etc.)
            avg_consideration_time: Average consideration time in days
            
        Returns:
            Dictionary with attribution window recommendations
        """
        # Base recommendations by business model
        base_recommendations = {
            'ecommerce': {'min_window': 7, 'max_window': 30, 'recommended': 14},
            'saas': {'min_window': 30, 'max_window': 90, 'recommended': 60},
            'b2b': {'min_window': 60, 'max_window': 180, 'recommended': 90},
            'marketplace': {'min_window': 7, 'max_window': 30, 'recommended': 21},
            'subscription': {'min_window': 14, 'max_window': 60, 'recommended': 30}
        }
        
        base_rec = base_recommendations.get(business_model, base_recommendations['ecommerce'])
        
        # Adjust for industry
        industry_multipliers = {
            'fashion': 1.2,
            'electronics': 1.5,
            'automotive': 2.0,
            'finance': 1.8,
            'healthcare': 1.3,
            'travel': 0.8
        }
        
        multiplier = industry_multipliers.get(industry, 1.0)
        
        # Apply multiplier
        adjusted_rec = {
            'min_window': int(base_rec['min_window'] * multiplier),
            'max_window': int(base_rec['max_window'] * multiplier),
            'recommended': int(base_rec['recommended'] * multiplier)
        }
        
        # Further adjust if actual consideration time is provided
        if avg_consideration_time:
            adjusted_rec['recommended'] = max(
                adjusted_rec['min_window'],
                min(adjusted_rec['max_window'], avg_consideration_time * 2)
            )
        
        return {
            'attribution_windows': adjusted_rec,
            'reasoning': f"Based on {business_model} model in {industry} industry",
            'considerations': [
                f"Minimum window: {adjusted_rec['min_window']} days for immediate conversions",
                f"Maximum window: {adjusted_rec['max_window']} days to capture full journey",
                f"Recommended: {adjusted_rec['recommended']} days for optimal balance"
            ]
        }
    
    def get_model_recommendations(
        self,
        business_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get attribution model recommendations based on business characteristics.
        
        Args:
            business_characteristics: Dict with business info
            
        Returns:
            Dictionary with model recommendations
        """
        business_type = business_characteristics.get('type', 'ecommerce')
        customer_journey_length = business_characteristics.get('avg_journey_length', 3)
        sales_cycle_days = business_characteristics.get('sales_cycle_days', 14)
        
        recommendations = []
        model_scores = {}
        
        # Score different models based on characteristics
        if sales_cycle_days <= 7:
            # Short cycle - favor recency
            model_scores.update({
                'last_touch': 0.8,
                'time_decay': 0.7,
                'first_touch': 0.4,
                'linear': 0.3,
                'position_based': 0.5
            })
            recommendations.append("Short sales cycle detected - recency-based models recommended")
        elif sales_cycle_days >= 30:
            # Long cycle - favor journey understanding
            model_scores.update({
                'position_based': 0.9,
                'data_driven': 0.8,
                'linear': 0.7,
                'time_decay': 0.6,
                'last_touch': 0.4
            })
            recommendations.append("Long sales cycle - position-based and data-driven models recommended")
        else:
            # Medium cycle - balanced approach
            model_scores.update({
                'time_decay': 0.8,
                'data_driven': 0.7,
                'position_based': 0.6,
                'linear': 0.5,
                'last_touch': 0.6
            })
            recommendations.append("Medium sales cycle - time decay model recommended")
        
        # Adjust for journey complexity
        if customer_journey_length >= 5:
            model_scores['data_driven'] += 0.2
            model_scores['shapley'] = model_scores.get('shapley', 0.6) + 0.1
            recommendations.append("Complex customer journey - consider advanced models")
        
        # Business type adjustments
        if business_type == 'b2b':
            model_scores['position_based'] += 0.1
            model_scores['time_decay'] += 0.1
        elif business_type == 'brand':
            model_scores['linear'] += 0.2
            model_scores['position_based'] += 0.1
        
        # Get top 3 recommended models
        top_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'primary_recommendation': top_models[0][0],
            'top_3_models': [model for model, score in top_models],
            'model_scores': model_scores,
            'recommendations': recommendations,
            'reasoning': f"Based on {business_type} business with {sales_cycle_days} day sales cycle"
        }
    
    def get_channel_interaction_insights(
        self,
        channel_data: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Get insights about channel interactions and synergies.
        
        Args:
            channel_data: Dictionary with channel performance data
            
        Returns:
            Dictionary with interaction insights
        """
        insights = {
            'channel_synergies': {},
            'optimization_opportunities': [],
            'interaction_patterns': {}
        }
        
        # Identify potential synergies based on channel characteristics
        channels = list(channel_data.keys())
        
        for i, channel1 in enumerate(channels):
            char1 = self.get_channel_characteristics(channel1)
            
            for channel2 in channels[i+1:]:
                char2 = self.get_channel_characteristics(channel2)
                
                # Check for complementary positioning
                if (char1.get('typical_position') == 'top_funnel' and 
                    char2.get('typical_position') == 'bottom_funnel'):
                    insights['channel_synergies'][f"{channel1}_{channel2}"] = {
                        'type': 'funnel_complementary',
                        'description': f"{channel1} drives awareness, {channel2} converts",
                        'optimization': 'Optimize budget allocation between awareness and conversion'
                    }
                
                # Check for similar audiences but different intents
                if (char1.get('intent_level') == 'low' and 
                    char2.get('intent_level') == 'high' and
                    char1.get('type') != char2.get('type')):
                    insights['channel_synergies'][f"{channel1}_{channel2}"] = {
                        'type': 'intent_progression',
                        'description': f"{channel1} builds interest, {channel2} captures demand",
                        'optimization': 'Sequence campaigns for journey progression'
                    }
        
        # Generate optimization recommendations
        for channel, data in channel_data.items():
            char = self.get_channel_characteristics(channel)
            
            if char.get('type') == 'brand_awareness' and data.get('conversion_rate', 0) > char.get('avg_conversion_rate', 0) * 1.5:
                insights['optimization_opportunities'].append({
                    'channel': channel,
                    'opportunity': 'scale_high_performing_brand_channel',
                    'description': f"{channel} showing high conversion rates - consider scaling"
                })
            
            if char.get('type') == 'performance' and data.get('cost', 0) > char.get('avg_cpc_range', [0, 0])[1]:
                insights['optimization_opportunities'].append({
                    'channel': channel,
                    'opportunity': 'optimize_high_cost_performance',
                    'description': f"{channel} has high costs - optimize targeting or creative"
                })
        
        return insights
    
    def validate_attribution_setup(
        self,
        setup_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate attribution measurement setup and provide recommendations.
        
        Args:
            setup_config: Configuration dictionary with setup details
            
        Returns:
            Dictionary with validation results and recommendations
        """
        validation_results = {
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'score': 100
        }
        
        # Check attribution window
        attribution_window = setup_config.get('attribution_window_days', 30)
        business_type = setup_config.get('business_type', 'ecommerce')
        
        recommended_window = self.get_attribution_window_recommendation(
            'general', business_type
        )['attribution_windows']['recommended']
        
        if abs(attribution_window - recommended_window) > recommended_window * 0.5:
            validation_results['warnings'].append({
                'type': 'attribution_window',
                'message': f"Attribution window ({attribution_window} days) differs significantly from recommended ({recommended_window} days)",
                'impact': 'medium'
            })
            validation_results['score'] -= 10
        
        # Check model selection
        selected_models = setup_config.get('attribution_models', [])
        if not selected_models:
            validation_results['issues'].append({
                'type': 'no_models',
                'message': "No attribution models selected",
                'impact': 'high'
            })
            validation_results['score'] -= 30
        
        # Check data requirements
        tracking_setup = setup_config.get('tracking_setup', {})
        
        if not tracking_setup.get('cross_channel_tracking'):
            validation_results['warnings'].append({
                'type': 'tracking',
                'message': "Cross-channel tracking not configured",
                'impact': 'high'
            })
            validation_results['score'] -= 20
        
        if not tracking_setup.get('conversion_tracking'):
            validation_results['issues'].append({
                'type': 'conversion_tracking',
                'message': "Conversion tracking not properly configured",
                'impact': 'critical'
            })
            validation_results['score'] -= 40
        
        # Generate recommendations
        if validation_results['score'] >= 80:
            validation_results['recommendations'].append("Setup looks good - consider testing additional models")
        elif validation_results['score'] >= 60:
            validation_results['recommendations'].append("Address warnings to improve attribution accuracy")
        else:
            validation_results['recommendations'].append("Critical issues found - fix before relying on attribution data")
        
        validation_results['overall_rating'] = (
            'excellent' if validation_results['score'] >= 90 else
            'good' if validation_results['score'] >= 80 else
            'fair' if validation_results['score'] >= 60 else
            'poor'
        )
        
        return validation_results