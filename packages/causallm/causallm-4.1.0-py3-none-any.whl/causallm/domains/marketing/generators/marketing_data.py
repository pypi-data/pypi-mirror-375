"""
Marketing Data Generator

Generates realistic synthetic marketing data for testing attribution models
and campaign analysis with configurable parameters.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random

class MarketingDataGenerator:
    """
    Generates comprehensive marketing datasets including:
    - Customer journeys with multiple touchpoints
    - Campaign data with spend and performance metrics
    - Cross-channel attribution scenarios
    - Customer lifetime value data
    """
    
    def __init__(self, seed: int = 42):
        """Initialize the data generator with random seed."""
        np.random.seed(seed)
        random.seed(seed)
        
        # Marketing channel definitions
        self.channels = {
            'paid_search': {'cpc': 2.5, 'conversion_rate': 0.03, 'volume_weight': 0.25},
            'display': {'cpc': 0.8, 'conversion_rate': 0.01, 'volume_weight': 0.20},
            'social_media': {'cpc': 1.2, 'conversion_rate': 0.02, 'volume_weight': 0.18},
            'email': {'cpc': 0.1, 'conversion_rate': 0.05, 'volume_weight': 0.15},
            'direct': {'cpc': 0.0, 'conversion_rate': 0.08, 'volume_weight': 0.12},
            'organic_search': {'cpc': 0.0, 'conversion_rate': 0.04, 'volume_weight': 0.10}
        }
        
        # Customer segments with different behaviors
        self.customer_segments = {
            'high_value': {'lifetime_value': 500, 'conversion_probability': 0.15, 'frequency': 0.20},
            'medium_value': {'lifetime_value': 200, 'conversion_probability': 0.08, 'frequency': 0.50},
            'low_value': {'lifetime_value': 50, 'conversion_probability': 0.03, 'frequency': 0.30}
        }
    
    def generate_customer_journey_data(
        self,
        n_customers: int = 10000,
        n_touchpoints: int = 50000,
        date_range_days: int = 90,
        start_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Generate customer journey data with multiple touchpoints.
        
        Args:
            n_customers: Number of unique customers
            n_touchpoints: Total number of touchpoints
            date_range_days: Date range for the data
            start_date: Start date for the data
            
        Returns:
            DataFrame with customer journey touchpoints
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=date_range_days)
        
        # Generate customer segments
        customers_data = []
        for i in range(n_customers):
            segment = np.random.choice(
                list(self.customer_segments.keys()),
                p=[seg['frequency'] for seg in self.customer_segments.values()]
            )
            
            customers_data.append({
                'customer_id': f'customer_{i:06d}',
                'segment': segment,
                'lifetime_value': self.customer_segments[segment]['lifetime_value'] * (0.5 + np.random.random()),
                'conversion_probability': self.customer_segments[segment]['conversion_probability']
            })
        
        customers_df = pd.DataFrame(customers_data)
        
        # Generate touchpoints
        touchpoints = []
        touchpoints_per_customer = np.random.poisson(n_touchpoints / n_customers, n_customers)
        
        for idx, customer in customers_df.iterrows():
            customer_id = customer['customer_id']
            segment = customer['segment']
            n_touch = min(touchpoints_per_customer[idx], 20)  # Cap at 20 touchpoints per customer
            
            if n_touch == 0:
                continue
            
            # Generate timestamp sequence
            timestamps = self._generate_customer_timestamps(start_date, date_range_days, n_touch)
            
            # Generate channel sequence with realistic patterns
            channels = self._generate_channel_sequence(n_touch, segment)
            
            # Determine if customer converts
            converts = np.random.random() < customer['conversion_probability']
            
            for i, (timestamp, channel) in enumerate(zip(timestamps, channels)):
                touchpoint = {
                    'customer_id': customer_id,
                    'timestamp': timestamp,
                    'channel': channel,
                    'touchpoint_number': i + 1,
                    'session_id': f'{customer_id}_session_{i//3}',  # Group touchpoints into sessions
                    'conversion': 1 if (converts and i == len(channels) - 1) else 0,
                    'revenue': customer['lifetime_value'] if (converts and i == len(channels) - 1) else 0,
                    'customer_segment': segment
                }
                touchpoints.append(touchpoint)
        
        touchpoints_df = pd.DataFrame(touchpoints)
        
        # Add additional features
        touchpoints_df = self._add_campaign_data(touchpoints_df)
        touchpoints_df = self._add_cost_data(touchpoints_df)
        touchpoints_df = self._add_engagement_metrics(touchpoints_df)
        
        return touchpoints_df.sort_values(['customer_id', 'timestamp']).reset_index(drop=True)
    
    def generate_campaign_spend_data(
        self,
        n_campaigns: int = 50,
        date_range_days: int = 90,
        start_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Generate campaign spend data.
        
        Args:
            n_campaigns: Number of campaigns
            date_range_days: Date range for spend data
            start_date: Start date
            
        Returns:
            DataFrame with campaign spend information
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=date_range_days)
        
        campaigns = []
        for i in range(n_campaigns):
            channel = np.random.choice(list(self.channels.keys()))
            
            # Generate daily spend data
            campaign_length = np.random.randint(7, 60)  # Campaign length in days
            campaign_start = start_date + timedelta(days=np.random.randint(0, date_range_days - campaign_length))
            
            daily_budget = np.random.lognormal(mean=6, sigma=0.8)  # Realistic budget distribution
            
            for day in range(campaign_length):
                spend_date = campaign_start + timedelta(days=day)
                daily_spend = daily_budget * (0.7 + 0.6 * np.random.random())  # Add some variation
                
                campaigns.append({
                    'campaign_id': f'campaign_{i:03d}',
                    'channel': channel,
                    'date': spend_date,
                    'spend': round(daily_spend, 2),
                    'campaign_type': np.random.choice(['brand', 'performance', 'awareness'], p=[0.3, 0.5, 0.2]),
                    'target_audience': np.random.choice(['broad', 'lookalike', 'retargeting'], p=[0.4, 0.3, 0.3])
                })
        
        return pd.DataFrame(campaigns)
    
    def generate_cross_channel_scenario(
        self,
        scenario_type: str = 'complex_journey',
        n_customers: int = 5000
    ) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """
        Generate specific cross-channel attribution scenarios for testing.
        
        Args:
            scenario_type: Type of scenario ('simple', 'complex_journey', 'display_assisted')
            n_customers: Number of customers
            
        Returns:
            Tuple of (touchpoints_data, true_attribution_weights)
        """
        scenarios = {
            'simple': self._generate_simple_scenario,
            'complex_journey': self._generate_complex_journey_scenario,
            'display_assisted': self._generate_display_assisted_scenario
        }
        
        if scenario_type not in scenarios:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
        
        return scenarios[scenario_type](n_customers)
    
    def _generate_customer_timestamps(
        self,
        start_date: datetime,
        date_range_days: int,
        n_touchpoints: int
    ) -> List[datetime]:
        """Generate realistic timestamp sequence for a customer."""
        # Start with random date within range
        customer_start = start_date + timedelta(days=np.random.randint(0, date_range_days - 30))
        
        # Generate touchpoint intervals (with clustering)
        intervals = []
        current_time = customer_start
        
        for i in range(n_touchpoints):
            if i == 0:
                intervals.append(current_time)
            else:
                # Add some clustering - touchpoints more likely to be close together
                if np.random.random() < 0.3:  # 30% chance of same day
                    gap_hours = np.random.exponential(2)
                else:  # Otherwise spread out more
                    gap_days = np.random.exponential(3)
                    gap_hours = gap_days * 24
                
                current_time += timedelta(hours=gap_hours)
                intervals.append(current_time)
        
        return intervals
    
    def _generate_channel_sequence(self, n_touchpoints: int, segment: str) -> List[str]:
        """Generate realistic channel sequence for customer journey."""
        channels = list(self.channels.keys())
        weights = [self.channels[ch]['volume_weight'] for ch in channels]
        
        # Adjust weights based on customer segment
        if segment == 'high_value':
            # High value customers more likely to use paid channels
            paid_indices = [i for i, ch in enumerate(channels) if 'paid' in ch or ch == 'email']
            for idx in paid_indices:
                weights[idx] *= 1.5
        elif segment == 'low_value':
            # Low value customers more likely to use organic channels
            organic_indices = [i for i, ch in enumerate(channels) if ch in ['organic_search', 'direct']]
            for idx in organic_indices:
                weights[idx] *= 2
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Generate sequence with some continuity (customers tend to stick to similar channels)
        sequence = []
        for i in range(n_touchpoints):
            if i == 0 or np.random.random() < 0.7:  # 70% chance of new channel
                channel = np.random.choice(channels, p=weights)
            else:  # 30% chance of repeating previous channel
                channel = sequence[-1]
            sequence.append(channel)
        
        return sequence
    
    def _add_campaign_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add campaign IDs and related data."""
        # Generate campaign IDs for paid channels
        campaign_mapping = {}
        campaign_counter = 0
        
        for channel in df['channel'].unique():
            if channel in ['paid_search', 'display', 'social_media']:
                n_campaigns = np.random.randint(3, 8)  # 3-7 campaigns per channel
                for i in range(n_campaigns):
                    campaign_id = f'{channel}_campaign_{campaign_counter:03d}'
                    campaign_mapping[(channel, i)] = campaign_id
                    campaign_counter += 1
        
        # Assign campaign IDs
        def assign_campaign(row):
            channel = row['channel']
            if channel in ['paid_search', 'display', 'social_media']:
                campaign_idx = hash(row['customer_id']) % 5  # Distribute across campaigns
                return campaign_mapping.get((channel, campaign_idx), f'{channel}_campaign_000')
            return None
        
        df['campaign_id'] = df.apply(assign_campaign, axis=1)
        return df
    
    def _add_cost_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add cost per click and other cost metrics."""
        def get_cost(row):
            channel = row['channel']
            base_cpc = self.channels[channel]['cpc']
            # Add some variation
            return round(base_cpc * (0.8 + 0.4 * np.random.random()), 3)
        
        df['cost_per_click'] = df.apply(get_cost, axis=1)
        df['estimated_cost'] = df['cost_per_click']  # Simplified - assuming each touchpoint is a click
        
        return df
    
    def _add_engagement_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add engagement metrics like time on site, pages viewed, etc."""
        # Time on site (minutes)
        df['time_on_site'] = np.random.lognormal(mean=1.5, sigma=0.8, size=len(df))
        df['time_on_site'] = np.clip(df['time_on_site'], 0.1, 30)  # Cap at 30 minutes
        
        # Pages viewed
        df['pages_viewed'] = np.random.poisson(lam=2.5, size=len(df)) + 1
        df['pages_viewed'] = np.clip(df['pages_viewed'], 1, 10)
        
        # Bounce rate (binary)
        bounce_prob = 0.4  # 40% bounce rate
        df['bounced'] = np.random.random(len(df)) < bounce_prob
        
        # Adjust engagement based on channel
        channel_engagement = {
            'email': 1.5,  # Email traffic more engaged
            'direct': 1.3,
            'organic_search': 1.2,
            'paid_search': 1.0,
            'social_media': 0.8,
            'display': 0.6
        }
        
        for channel, multiplier in channel_engagement.items():
            mask = df['channel'] == channel
            df.loc[mask, 'time_on_site'] *= multiplier
            df.loc[mask, 'pages_viewed'] = (df.loc[mask, 'pages_viewed'] * multiplier).astype(int)
        
        return df
    
    def _generate_simple_scenario(self, n_customers: int) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Generate simple attribution scenario with known true weights."""
        # Simple scenario: Display shows ad, paid search converts
        # True attribution: Display 30%, Paid Search 70%
        
        touchpoints = []
        customer_id_base = 0
        
        for i in range(n_customers):
            customer_id = f'customer_{customer_id_base + i:06d}'
            
            # 80% of customers see display first, then paid search
            if np.random.random() < 0.8:
                touchpoints.extend([
                    {
                        'customer_id': customer_id,
                        'timestamp': datetime.now() - timedelta(days=5),
                        'channel': 'display',
                        'touchpoint_number': 1,
                        'conversion': 0,
                        'revenue': 0
                    },
                    {
                        'customer_id': customer_id,
                        'timestamp': datetime.now() - timedelta(days=1),
                        'channel': 'paid_search',
                        'touchpoint_number': 2,
                        'conversion': 1 if np.random.random() < 0.1 else 0,
                        'revenue': 100 if np.random.random() < 0.1 else 0
                    }
                ])
            else:
                # 20% only use paid search
                touchpoints.append({
                    'customer_id': customer_id,
                    'timestamp': datetime.now() - timedelta(days=1),
                    'channel': 'paid_search',
                    'touchpoint_number': 1,
                    'conversion': 1 if np.random.random() < 0.15 else 0,
                    'revenue': 100 if np.random.random() < 0.15 else 0
                })
        
        df = pd.DataFrame(touchpoints)
        true_attribution = {'display': 0.3, 'paid_search': 0.7}
        
        return df, true_attribution
    
    def _generate_complex_journey_scenario(self, n_customers: int) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Generate complex multi-touch journey scenario."""
        # Complex scenario with multiple channels
        # True attribution varies by position and effectiveness
        
        return self.generate_customer_journey_data(
            n_customers=n_customers,
            n_touchpoints=n_customers * 3,  # Average 3 touchpoints per customer
            date_range_days=30
        ), {
            'display': 0.15,
            'paid_search': 0.25,
            'social_media': 0.20,
            'email': 0.20,
            'direct': 0.15,
            'organic_search': 0.05
        }
    
    def _generate_display_assisted_scenario(self, n_customers: int) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Generate display-assisted conversion scenario."""
        # Scenario where display doesn't directly convert but assists
        
        touchpoints = []
        
        for i in range(n_customers):
            customer_id = f'customer_{i:06d}'
            
            # Customer journey: Display -> Social -> Email -> Conversion
            journey = [
                ('display', 7, 0),
                ('social_media', 3, 0),
                ('email', 0, 1 if np.random.random() < 0.12 else 0)
            ]
            
            for j, (channel, days_ago, converts) in enumerate(journey):
                touchpoints.append({
                    'customer_id': customer_id,
                    'timestamp': datetime.now() - timedelta(days=days_ago),
                    'channel': channel,
                    'touchpoint_number': j + 1,
                    'conversion': converts,
                    'revenue': 150 if converts else 0
                })
        
        df = pd.DataFrame(touchpoints)
        true_attribution = {'display': 0.4, 'social_media': 0.3, 'email': 0.3}
        
        return df, true_attribution