"""
Marketing Attribution Analyzer

Advanced multi-touch attribution modeling with performance optimizations for large-scale
marketing data analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import asyncio
from datetime import datetime, timedelta

# Import performance optimization modules
try:
    from ...core.optimized_algorithms import vectorized_stats, causal_inference
    from ...core.async_processing import AsyncTaskManager
    from ...core.data_processing import DataChunker
    from ...utils.logging import get_logger
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

@dataclass
class AttributionResult:
    """Results from attribution analysis."""
    model_name: str
    channel_attribution: Dict[str, float]
    conversion_probability: float
    attribution_weights: pd.DataFrame
    model_performance: Dict[str, float]
    confidence_intervals: Optional[Dict[str, Tuple[float, float]]] = None

@dataclass
class CampaignROI:
    """Campaign ROI analysis results."""
    campaign_id: str
    total_spend: float
    total_conversions: int
    total_revenue: float
    roi: float
    cost_per_acquisition: float
    conversion_rate: float
    attribution_score: float

class MarketingAttributionAnalyzer:
    """
    Advanced marketing attribution analyzer with multiple attribution models.
    
    Supports:
    - First-touch attribution
    - Last-touch attribution
    - Linear attribution
    - Time-decay attribution
    - Position-based attribution
    - Data-driven attribution (using causal inference)
    - Shapley value attribution
    """
    
    def __init__(self, enable_optimizations=True):
        """Initialize the attribution analyzer."""
        self.enable_optimizations = enable_optimizations and PERFORMANCE_AVAILABLE
        self.logger = get_logger("causallm.marketing.attribution", level="INFO") if PERFORMANCE_AVAILABLE else None
        
        if self.enable_optimizations:
            self.async_manager = AsyncTaskManager()
            self.data_chunker = DataChunker()
        
        self.attribution_models = {
            'first_touch': self._first_touch_attribution,
            'last_touch': self._last_touch_attribution, 
            'linear': self._linear_attribution,
            'time_decay': self._time_decay_attribution,
            'position_based': self._position_based_attribution,
            'data_driven': self._data_driven_attribution,
            'shapley': self._shapley_attribution
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available attribution models."""
        return list(self.attribution_models.keys())
    
    def analyze_attribution(
        self,
        data: pd.DataFrame,
        conversion_column: str = 'conversion',
        customer_id_column: str = 'customer_id',
        channel_column: str = 'channel',
        timestamp_column: str = 'timestamp',
        model: str = 'data_driven',
        **kwargs
    ) -> AttributionResult:
        """
        Perform attribution analysis using specified model.
        
        Args:
            data: Customer touchpoint data
            conversion_column: Name of conversion indicator column
            customer_id_column: Name of customer ID column
            channel_column: Name of marketing channel column
            timestamp_column: Name of timestamp column
            model: Attribution model to use
            **kwargs: Additional model-specific parameters
            
        Returns:
            AttributionResult with attribution weights and performance metrics
        """
        if self.logger:
            self.logger.info(f"Starting attribution analysis with {model} model on {len(data):,} touchpoints")
        
        # Validate inputs
        required_columns = [conversion_column, customer_id_column, channel_column, timestamp_column]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Prepare data
        processed_data = self._prepare_attribution_data(
            data, conversion_column, customer_id_column, 
            channel_column, timestamp_column
        )
        
        # Apply selected attribution model
        if model not in self.attribution_models:
            raise ValueError(f"Unknown attribution model: {model}. Available: {self.get_available_models()}")
        
        attribution_func = self.attribution_models[model]
        result = attribution_func(processed_data, **kwargs)
        
        if self.logger:
            self.logger.info(f"Attribution analysis completed. Top channels: {dict(list(result.channel_attribution.items())[:3])}")
        
        return result
    
    def compare_attribution_models(
        self,
        data: pd.DataFrame,
        models: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, AttributionResult]:
        """
        Compare multiple attribution models on the same data.
        
        Args:
            data: Customer touchpoint data
            models: List of models to compare (default: all models)
            **kwargs: Parameters for attribution analysis
            
        Returns:
            Dictionary mapping model names to AttributionResults
        """
        if models is None:
            models = self.get_available_models()
        
        if self.enable_optimizations and len(models) > 1:
            # Run models in parallel using async processing
            return asyncio.run(self._compare_models_async(data, models, **kwargs))
        else:
            # Run models sequentially
            results = {}
            for model in models:
                results[model] = self.analyze_attribution(data, model=model, **kwargs)
            return results
    
    async def _compare_models_async(
        self,
        data: pd.DataFrame,
        models: List[str],
        **kwargs
    ) -> Dict[str, AttributionResult]:
        """Compare attribution models asynchronously."""
        tasks = []
        for model in models:
            task = self._run_attribution_async(data, model, **kwargs)
            tasks.append((model, task))
        
        results = {}
        completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for i, (model, _) in enumerate(tasks):
            if isinstance(completed_tasks[i], Exception):
                if self.logger:
                    self.logger.error(f"Error in {model} model: {completed_tasks[i]}")
                continue
            results[model] = completed_tasks[i]
        
        return results
    
    async def _run_attribution_async(self, data: pd.DataFrame, model: str, **kwargs) -> AttributionResult:
        """Run attribution analysis asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.analyze_attribution, data, model, **kwargs
        )
    
    def analyze_campaign_roi(
        self,
        data: pd.DataFrame,
        spend_data: pd.DataFrame,
        campaign_column: str = 'campaign_id',
        spend_column: str = 'spend',
        revenue_column: str = 'revenue',
        **kwargs
    ) -> Dict[str, CampaignROI]:
        """
        Analyze ROI for marketing campaigns using attribution results.
        
        Args:
            data: Customer touchpoint data with conversions
            spend_data: Campaign spend data
            campaign_column: Name of campaign ID column
            spend_column: Name of spend column
            revenue_column: Name of revenue column
            
        Returns:
            Dictionary mapping campaign IDs to CampaignROI objects
        """
        if self.logger:
            self.logger.info(f"Analyzing ROI for {data[campaign_column].nunique()} campaigns")
        
        # Get attribution results for campaigns
        attribution_results = self.analyze_attribution(
            data, channel_column=campaign_column, **kwargs
        )
        
        # Merge with spend data
        campaign_data = data.groupby(campaign_column).agg({
            'conversion': ['sum', 'count'],
            revenue_column: 'sum' if revenue_column in data.columns else lambda x: 0
        }).round(2)
        
        campaign_data.columns = ['conversions', 'touchpoints', 'revenue']
        campaign_data = campaign_data.merge(
            spend_data.set_index(campaign_column)[spend_column], 
            left_index=True, right_index=True
        )
        
        # Calculate ROI metrics
        roi_results = {}
        for campaign_id in campaign_data.index:
            row = campaign_data.loc[campaign_id]
            attribution_score = attribution_results.channel_attribution.get(campaign_id, 0)
            
            roi = (row['revenue'] - row[spend_column]) / row[spend_column] if row[spend_column] > 0 else 0
            cpa = row[spend_column] / row['conversions'] if row['conversions'] > 0 else float('inf')
            conversion_rate = row['conversions'] / row['touchpoints'] if row['touchpoints'] > 0 else 0
            
            roi_results[campaign_id] = CampaignROI(
                campaign_id=campaign_id,
                total_spend=row[spend_column],
                total_conversions=int(row['conversions']),
                total_revenue=row['revenue'],
                roi=roi,
                cost_per_acquisition=cpa,
                conversion_rate=conversion_rate,
                attribution_score=attribution_score
            )
        
        return roi_results
    
    def _prepare_attribution_data(
        self,
        data: pd.DataFrame,
        conversion_column: str,
        customer_id_column: str,
        channel_column: str,
        timestamp_column: str
    ) -> pd.DataFrame:
        """Prepare data for attribution analysis."""
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(data[timestamp_column]):
            data[timestamp_column] = pd.to_datetime(data[timestamp_column])
        
        # Sort by customer and timestamp
        data_sorted = data.sort_values([customer_id_column, timestamp_column]).copy()
        
        # Add path position for each customer
        data_sorted['path_position'] = data_sorted.groupby(customer_id_column).cumcount() + 1
        data_sorted['path_length'] = data_sorted.groupby(customer_id_column)[customer_id_column].transform('count')
        
        # Add time since first touch
        data_sorted['first_touch_time'] = data_sorted.groupby(customer_id_column)[timestamp_column].transform('min')
        data_sorted['time_since_first_touch'] = (
            data_sorted[timestamp_column] - data_sorted['first_touch_time']
        ).dt.total_seconds() / 3600  # Hours
        
        return data_sorted
    
    def _first_touch_attribution(self, data: pd.DataFrame, **kwargs) -> AttributionResult:
        """First-touch attribution model."""
        # Attribute 100% credit to first touchpoint
        first_touch = data[data['path_position'] == 1]
        converted_customers = data[data['conversion'] == 1]['customer_id'].unique()
        first_touch_converted = first_touch[first_touch['customer_id'].isin(converted_customers)]
        
        channel_attribution = (
            first_touch_converted['channel'].value_counts(normalize=True).to_dict()
        )
        
        # Calculate conversion probability
        conversion_prob = len(converted_customers) / data['customer_id'].nunique()
        
        # Create attribution weights DataFrame
        weights_df = first_touch.copy()
        weights_df['attribution_weight'] = weights_df['customer_id'].isin(converted_customers).astype(int)
        
        # Model performance metrics
        performance = {
            'model_accuracy': self._calculate_model_accuracy(weights_df),
            'total_conversions': len(converted_customers),
            'attributed_conversions': len(converted_customers)
        }
        
        return AttributionResult(
            model_name='first_touch',
            channel_attribution=channel_attribution,
            conversion_probability=conversion_prob,
            attribution_weights=weights_df,
            model_performance=performance
        )
    
    def _last_touch_attribution(self, data: pd.DataFrame, **kwargs) -> AttributionResult:
        """Last-touch attribution model."""
        # Attribute 100% credit to last touchpoint before conversion
        converted_customers = data[data['conversion'] == 1]['customer_id'].unique()
        last_touch = data.loc[data.groupby('customer_id')['path_position'].idxmax()]
        last_touch_converted = last_touch[last_touch['customer_id'].isin(converted_customers)]
        
        channel_attribution = (
            last_touch_converted['channel'].value_counts(normalize=True).to_dict()
        )
        
        conversion_prob = len(converted_customers) / data['customer_id'].nunique()
        
        weights_df = last_touch.copy()
        weights_df['attribution_weight'] = weights_df['customer_id'].isin(converted_customers).astype(int)
        
        performance = {
            'model_accuracy': self._calculate_model_accuracy(weights_df),
            'total_conversions': len(converted_customers),
            'attributed_conversions': len(converted_customers)
        }
        
        return AttributionResult(
            model_name='last_touch',
            channel_attribution=channel_attribution,
            conversion_probability=conversion_prob,
            attribution_weights=weights_df,
            model_performance=performance
        )
    
    def _linear_attribution(self, data: pd.DataFrame, **kwargs) -> AttributionResult:
        """Linear attribution model - equal credit to all touchpoints."""
        converted_customers = data[data['conversion'] == 1]['customer_id'].unique()
        customer_paths = data[data['customer_id'].isin(converted_customers)].copy()
        
        # Equal weight to all touchpoints in path
        customer_paths['attribution_weight'] = 1.0 / customer_paths['path_length']
        
        # Calculate channel attribution
        channel_attribution = (
            customer_paths.groupby('channel')['attribution_weight']
            .sum().div(customer_paths.groupby('channel')['attribution_weight'].sum().sum())
            .to_dict()
        )
        
        conversion_prob = len(converted_customers) / data['customer_id'].nunique()
        
        performance = {
            'model_accuracy': self._calculate_model_accuracy(customer_paths),
            'total_conversions': len(converted_customers),
            'attributed_conversions': len(converted_customers)
        }
        
        return AttributionResult(
            model_name='linear',
            channel_attribution=channel_attribution,
            conversion_probability=conversion_prob,
            attribution_weights=customer_paths,
            model_performance=performance
        )
    
    def _time_decay_attribution(self, data: pd.DataFrame, decay_factor: float = 0.1, **kwargs) -> AttributionResult:
        """Time-decay attribution model - more credit to recent touchpoints."""
        converted_customers = data[data['conversion'] == 1]['customer_id'].unique()
        customer_paths = data[data['customer_id'].isin(converted_customers)].copy()
        
        # Calculate time decay weights
        customer_paths['hours_to_conversion'] = (
            customer_paths.groupby('customer_id')['time_since_first_touch'].transform('max') - 
            customer_paths['time_since_first_touch']
        )
        
        # Exponential decay based on time to conversion
        customer_paths['time_weight'] = np.exp(-decay_factor * customer_paths['hours_to_conversion'])
        
        # Normalize weights within each customer path
        customer_paths['attribution_weight'] = (
            customer_paths['time_weight'] / 
            customer_paths.groupby('customer_id')['time_weight'].transform('sum')
        )
        
        # Calculate channel attribution
        channel_attribution = (
            customer_paths.groupby('channel')['attribution_weight']
            .sum().div(customer_paths.groupby('channel')['attribution_weight'].sum().sum())
            .to_dict()
        )
        
        conversion_prob = len(converted_customers) / data['customer_id'].nunique()
        
        performance = {
            'model_accuracy': self._calculate_model_accuracy(customer_paths),
            'total_conversions': len(converted_customers),
            'attributed_conversions': len(converted_customers),
            'decay_factor': decay_factor
        }
        
        return AttributionResult(
            model_name='time_decay',
            channel_attribution=channel_attribution,
            conversion_probability=conversion_prob,
            attribution_weights=customer_paths,
            model_performance=performance
        )
    
    def _position_based_attribution(
        self, 
        data: pd.DataFrame, 
        first_touch_weight: float = 0.4,
        last_touch_weight: float = 0.4,
        **kwargs
    ) -> AttributionResult:
        """Position-based attribution model - more credit to first and last touchpoints."""
        converted_customers = data[data['conversion'] == 1]['customer_id'].unique()
        customer_paths = data[data['customer_id'].isin(converted_customers)].copy()
        
        # Calculate position-based weights
        middle_weight = 1.0 - first_touch_weight - last_touch_weight
        
        def calculate_position_weight(row):
            if row['path_position'] == 1:
                return first_touch_weight
            elif row['path_position'] == row['path_length']:
                return last_touch_weight
            else:
                # Distribute middle weight equally among middle touchpoints
                middle_touchpoints = max(1, row['path_length'] - 2)
                return middle_weight / middle_touchpoints
        
        customer_paths['attribution_weight'] = customer_paths.apply(calculate_position_weight, axis=1)
        
        # Calculate channel attribution
        channel_attribution = (
            customer_paths.groupby('channel')['attribution_weight']
            .sum().div(customer_paths.groupby('channel')['attribution_weight'].sum().sum())
            .to_dict()
        )
        
        conversion_prob = len(converted_customers) / data['customer_id'].nunique()
        
        performance = {
            'model_accuracy': self._calculate_model_accuracy(customer_paths),
            'total_conversions': len(converted_customers),
            'attributed_conversions': len(converted_customers),
            'first_touch_weight': first_touch_weight,
            'last_touch_weight': last_touch_weight
        }
        
        return AttributionResult(
            model_name='position_based',
            channel_attribution=channel_attribution,
            conversion_probability=conversion_prob,
            attribution_weights=customer_paths,
            model_performance=performance
        )
    
    def _data_driven_attribution(self, data: pd.DataFrame, **kwargs) -> AttributionResult:
        """Data-driven attribution using causal inference."""
        if not self.enable_optimizations:
            # Fallback to linear attribution if optimization not available
            if self.logger:
                self.logger.warning("Performance optimizations not available, falling back to linear attribution")
            return self._linear_attribution(data, **kwargs)
        
        try:
            # Prepare features for causal analysis
            features = self._extract_channel_features(data)
            
            # Use causal inference to determine attribution weights
            if 'conversion' in data.columns:
                X = features.drop(['conversion', 'customer_id'], axis=1, errors='ignore').values
                y = features['conversion'].values
                
                # Use vectorized ATE estimation
                channel_effects = {}
                for channel in data['channel'].unique():
                    treatment = (data['channel'] == channel).astype(int).values[:len(y)]
                    
                    if len(treatment) == len(y) and len(X) == len(y):
                        ate_result = causal_inference.estimate_ate_vectorized(
                            X, treatment, y, method='doubly_robust'
                        )
                        channel_effects[channel] = ate_result['ate']
                
                # Normalize effects to get attribution weights
                total_effect = sum(max(0, effect) for effect in channel_effects.values())
                if total_effect > 0:
                    channel_attribution = {
                        channel: max(0, effect) / total_effect 
                        for channel, effect in channel_effects.items()
                    }
                else:
                    # Fallback to equal weights
                    n_channels = len(channel_effects)
                    channel_attribution = {channel: 1.0/n_channels for channel in channel_effects}
                
                # Create attribution weights DataFrame
                weights_df = data.copy()
                weights_df['attribution_weight'] = weights_df['channel'].map(channel_attribution).fillna(0)
                
                conversion_prob = y.mean()
                
                performance = {
                    'model_accuracy': self._calculate_model_accuracy(weights_df),
                    'total_conversions': int(y.sum()),
                    'attributed_conversions': int(y.sum()),
                    'causal_method': 'doubly_robust'
                }
                
                return AttributionResult(
                    model_name='data_driven',
                    channel_attribution=channel_attribution,
                    conversion_probability=conversion_prob,
                    attribution_weights=weights_df,
                    model_performance=performance
                )
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in data-driven attribution: {e}, falling back to linear")
        
        # Fallback to linear attribution
        return self._linear_attribution(data, **kwargs)
    
    def _shapley_attribution(self, data: pd.DataFrame, **kwargs) -> AttributionResult:
        """Shapley value attribution model."""
        # Simplified Shapley value calculation for marketing attribution
        converted_customers = data[data['conversion'] == 1]['customer_id'].unique()
        customer_paths = data[data['customer_id'].isin(converted_customers)].copy()
        
        channels = customer_paths['channel'].unique()
        shapley_values = {}
        
        # Calculate Shapley values for each channel
        for channel in channels:
            marginal_contributions = []
            
            # For each customer path containing this channel
            channel_customers = customer_paths[customer_paths['channel'] == channel]['customer_id'].unique()
            
            for customer_id in channel_customers:
                customer_data = customer_paths[customer_paths['customer_id'] == customer_id]
                customer_channels = customer_data['channel'].unique()
                
                # Calculate marginal contribution
                # This is a simplified version - full Shapley calculation would be exponentially complex
                if len(customer_channels) == 1:
                    contribution = 1.0
                else:
                    contribution = 1.0 / len(customer_channels)
                
                marginal_contributions.append(contribution)
            
            shapley_values[channel] = np.mean(marginal_contributions) if marginal_contributions else 0
        
        # Normalize to get attribution weights
        total_shapley = sum(shapley_values.values())
        if total_shapley > 0:
            channel_attribution = {ch: val/total_shapley for ch, val in shapley_values.items()}
        else:
            channel_attribution = {ch: 1.0/len(channels) for ch in channels}
        
        # Create weights DataFrame
        weights_df = customer_paths.copy()
        weights_df['attribution_weight'] = weights_df['channel'].map(channel_attribution).fillna(0)
        
        conversion_prob = len(converted_customers) / data['customer_id'].nunique()
        
        performance = {
            'model_accuracy': self._calculate_model_accuracy(weights_df),
            'total_conversions': len(converted_customers),
            'attributed_conversions': len(converted_customers)
        }
        
        return AttributionResult(
            model_name='shapley',
            channel_attribution=channel_attribution,
            conversion_probability=conversion_prob,
            attribution_weights=weights_df,
            model_performance=performance
        )
    
    def _extract_channel_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for each channel for causal analysis."""
        # Create channel interaction features
        channel_dummies = pd.get_dummies(data['channel'], prefix='channel')
        
        # Aggregate by customer
        customer_features = data.groupby('customer_id').agg({
            'conversion': 'max',
            'path_length': 'first',
            'time_since_first_touch': 'max'
        })
        
        # Add channel touchpoint counts
        channel_counts = data.groupby(['customer_id', 'channel']).size().unstack(fill_value=0)
        channel_counts.columns = [f'touchpoints_{col}' for col in channel_counts.columns]
        
        # Combine features
        features = customer_features.join(channel_counts).fillna(0)
        features['customer_id'] = features.index
        
        return features.reset_index(drop=True)
    
    def _calculate_model_accuracy(self, weights_df: pd.DataFrame) -> float:
        """Calculate a simple accuracy metric for the attribution model."""
        if 'conversion' in weights_df.columns and 'attribution_weight' in weights_df.columns:
            # Simple correlation between weights and actual conversions
            return abs(weights_df['conversion'].corr(weights_df['attribution_weight']))
        return 0.0