"""
Marketing Domain Package for CausalLLM

Provides specialized tools for marketing attribution analysis, campaign effectiveness measurement,
and customer journey analytics with performance optimizations.
"""

from .attribution_analyzer import MarketingAttributionAnalyzer
from .generators.marketing_data import MarketingDataGenerator
from .templates.campaign_analysis import CampaignAnalysisTemplate
from .templates.attribution_template import AttributionAnalysisTemplate
from .knowledge.marketing_knowledge import MarketingKnowledge

class MarketingDomain:
    """
    Comprehensive marketing domain for attribution analysis and campaign effectiveness.
    
    Features:
    - Multi-touch attribution modeling
    - Campaign ROI analysis
    - Customer lifetime value measurement
    - Cross-channel attribution
    - Performance-optimized for large datasets
    """
    
    def __init__(self, enable_performance_optimizations=True):
        """Initialize marketing domain with optimization settings."""
        self.enable_optimizations = enable_performance_optimizations
        
        # Initialize components
        self.attribution_analyzer = MarketingAttributionAnalyzer(
            enable_optimizations=enable_performance_optimizations
        )
        self.data_generator = MarketingDataGenerator()
        self.campaign_template = CampaignAnalysisTemplate()
        self.attribution_template = AttributionAnalysisTemplate()
        self.knowledge = MarketingKnowledge()
    
    def analyze_attribution(self, data, conversion_column='conversion', **kwargs):
        """Perform multi-touch attribution analysis."""
        return self.attribution_analyzer.analyze_attribution(
            data, conversion_column, **kwargs
        )
    
    def analyze_campaign_effectiveness(self, data, campaign_column='campaign_id', **kwargs):
        """Analyze campaign effectiveness and ROI."""
        return self.campaign_template.run_analysis(
            'campaign_effectiveness', data, campaign_column=campaign_column, **kwargs
        )
    
    def generate_marketing_data(self, n_customers=10000, n_touchpoints=50000, **kwargs):
        """Generate synthetic marketing data for testing and demos."""
        return self.data_generator.generate_customer_journey_data(
            n_customers, n_touchpoints, **kwargs
        )
    
    def get_attribution_models(self):
        """Get available attribution models."""
        return self.attribution_analyzer.get_available_models()

__all__ = [
    'MarketingDomain',
    'MarketingAttributionAnalyzer',
    'MarketingDataGenerator', 
    'CampaignAnalysisTemplate',
    'AttributionAnalysisTemplate',
    'MarketingKnowledge'
]