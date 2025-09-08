"""
Enhanced CausalLLM with Standardized Interfaces and Configuration Management

This module provides the main CausalLLM class with standardized interfaces,
centralized configuration, and unified async support.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import numpy as np

from .config.settings import CausalLLMConfig, get_config, load_config
from .interfaces.base import (
    CausalDiscoveryResult, CausalInferenceResult, ComprehensiveCausalAnalysis,
    AnalysisMetadata, standardize_column_names, validate_data_requirements
)
from .interfaces.async_interface import (
    AsyncCausalInterface, AsyncExecutionConfig, AsyncCausalContext
)

logger = logging.getLogger(__name__)


class EnhancedCausalLLM:
    """
    Enhanced CausalLLM with standardized interfaces and centralized configuration.
    
    This class provides a unified interface for all causal analysis operations,
    with consistent parameter naming, async support, and centralized configuration
    management.
    """
    
    def __init__(self,
                 config: Optional[CausalLLMConfig] = None,
                 config_file: Optional[str] = None,
                 **override_params):
        """
        Initialize EnhancedCausalLLM with configuration management.
        
        Args:
            config: CausalLLMConfig instance. If None, loads from file or uses defaults.
            config_file: Path to configuration file. If None, searches for default files.
            **override_params: Parameters to override in configuration.
        """
        # Load configuration
        if config is not None:
            self.config = config
        elif config_file is not None:
            self.config = load_config(config_file)
        else:
            self.config = get_config()
        
        # Apply parameter overrides
        if override_params:
            self.config.update(**override_params)
        
        # Initialize components
        self._setup_logging()
        self._initialize_components()
        
        # Track performance metrics
        self.performance_metrics = {
            'total_analyses': 0,
            'total_execution_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _setup_logging(self):
        """Configure logging based on configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.logging.level.upper()),
            format=self.config.logging.format
        )
        
        if self.config.logging.file_path:
            file_handler = logging.FileHandler(self.config.logging.file_path)
            file_handler.setLevel(getattr(logging, self.config.logging.level.upper()))
            file_handler.setFormatter(logging.Formatter(self.config.logging.format))
            logger.addHandler(file_handler)
        
        logger.info("CausalLLM initialized with configuration")
    
    def _initialize_components(self):
        """Initialize internal components based on configuration."""
        # Initialize async interface if enabled
        if self.config.performance.use_async:
            async_config = AsyncExecutionConfig(
                max_workers=self.config.performance.max_workers,
                enable_progress_tracking=self.config.logging.enable_progress_bars,
                chunk_size=self.config.performance.chunk_size,
                memory_limit_gb=self.config.performance.max_memory_gb
            )
            self.async_interface = AsyncCausalInterface(async_config)
        else:
            self.async_interface = None
        
        # Initialize caching if enabled
        if self.config.performance.cache_enabled:
            self._setup_caching()
        
        logger.debug("Components initialized successfully")
    
    def _setup_caching(self):
        """Setup caching system based on configuration."""
        # This would integrate with the caching system
        # For now, we'll use a simple in-memory cache
        self._cache = {}
        logger.debug("Caching system initialized")
    
    def comprehensive_analysis(self,
                             data: pd.DataFrame,
                             treatment_variable: Optional[str] = None,
                             outcome_variable: Optional[str] = None,
                             covariate_variables: Optional[List[str]] = None,
                             variable_names: Optional[List[str]] = None,
                             domain_context: Optional[str] = None,
                             **kwargs) -> ComprehensiveCausalAnalysis:
        """
        Perform comprehensive causal analysis with standardized interface.
        
        Args:
            data: Input DataFrame for analysis
            treatment_variable: Name of treatment/intervention column
            outcome_variable: Name of outcome variable column  
            covariate_variables: List of covariate variable names
            variable_names: List of variables to include in analysis
            domain_context: Domain context for specialized analysis
            **kwargs: Additional parameters
            
        Returns:
            ComprehensiveCausalAnalysis with discovery and inference results
            
        Raises:
            ValueError: If data validation fails
            RuntimeError: If analysis fails
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            validate_data_requirements(
                data, 
                min_samples=self.config.statistical.min_sample_size
            )
            
            # Standardize column names if variables specified
            if treatment_variable and outcome_variable:
                column_mapping = standardize_column_names(
                    data, treatment_variable, outcome_variable, covariate_variables
                )
                logger.debug(f"Column mapping: {column_mapping}")
            
            # Check cache
            cache_key = self._generate_cache_key(
                data, treatment_variable, outcome_variable, 
                covariate_variables, domain_context, kwargs
            )
            
            if self.config.performance.cache_enabled and cache_key in self._cache:
                self.performance_metrics['cache_hits'] += 1
                logger.info("Returning cached result")
                return self._cache[cache_key]
            
            self.performance_metrics['cache_misses'] += 1
            
            # Choose sync or async execution
            if self.config.performance.use_async and self.async_interface:
                result = asyncio.run(self._comprehensive_analysis_async(
                    data, treatment_variable, outcome_variable,
                    covariate_variables, variable_names, domain_context, **kwargs
                ))
            else:
                result = self._comprehensive_analysis_sync(
                    data, treatment_variable, outcome_variable,
                    covariate_variables, variable_names, domain_context, **kwargs
                )
            
            # Update performance metrics
            execution_time = time.time() - start_time
            self.performance_metrics['total_analyses'] += 1
            self.performance_metrics['total_execution_time'] += execution_time
            result.performance_metrics['execution_time'] = execution_time
            
            # Cache result
            if self.config.performance.cache_enabled:
                self._cache[cache_key] = result
            
            logger.info(f"Comprehensive analysis completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {str(e)}")
            raise RuntimeError(f"Analysis failed: {str(e)}") from e
    
    def discover_causal_relationships(self,
                                    data: pd.DataFrame,
                                    variable_names: Optional[List[str]] = None,
                                    domain_context: Optional[str] = None,
                                    method: str = 'pc_algorithm',
                                    **kwargs) -> CausalDiscoveryResult:
        """
        Discover causal relationships with standardized interface.
        
        Args:
            data: Input DataFrame for discovery
            variable_names: Variables to include in discovery
            domain_context: Domain context for enhanced discovery
            method: Discovery method to use
            **kwargs: Additional parameters
            
        Returns:
            CausalDiscoveryResult with discovered relationships
        """
        start_time = time.time()
        
        try:
            validate_data_requirements(data)
            
            # Choose sync or async execution
            if self.config.performance.use_async and self.async_interface:
                result = asyncio.run(self.async_interface.discover_causal_structure_async(
                    data, variable_names, domain_context, method, **kwargs
                ))
            else:
                result = self._discover_sync(data, variable_names, domain_context, method, **kwargs)
            
            execution_time = time.time() - start_time
            result.metadata.execution_time_seconds = execution_time
            
            logger.info(f"Causal discovery completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Causal discovery failed: {str(e)}")
            raise RuntimeError(f"Discovery failed: {str(e)}") from e
    
    def estimate_causal_effect(self,
                              data: pd.DataFrame,
                              treatment_variable: str,
                              outcome_variable: str,
                              covariate_variables: Optional[List[str]] = None,
                              method: str = 'comprehensive',
                              **kwargs) -> CausalInferenceResult:
        """
        Estimate causal effect with standardized interface.
        
        Args:
            data: Input DataFrame for inference
            treatment_variable: Name of treatment variable
            outcome_variable: Name of outcome variable
            covariate_variables: List of covariate variables
            method: Estimation method to use
            **kwargs: Additional parameters
            
        Returns:
            CausalInferenceResult with effect estimates
        """
        start_time = time.time()
        
        try:
            validate_data_requirements(data)
            standardize_column_names(data, treatment_variable, outcome_variable, covariate_variables)
            
            # Choose sync or async execution
            if self.config.performance.use_async and self.async_interface:
                result = asyncio.run(self.async_interface.estimate_causal_effect_async(
                    data, treatment_variable, outcome_variable, 
                    covariate_variables, method, **kwargs
                ))
            else:
                result = self._estimate_effect_sync(
                    data, treatment_variable, outcome_variable,
                    covariate_variables, method, **kwargs
                )
            
            execution_time = time.time() - start_time
            result.metadata.execution_time_seconds = execution_time
            
            logger.info(f"Causal effect estimation completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Causal effect estimation failed: {str(e)}")
            raise RuntimeError(f"Effect estimation failed: {str(e)}") from e
    
    async def comprehensive_analysis_async(self, *args, **kwargs) -> ComprehensiveCausalAnalysis:
        """Async version of comprehensive analysis."""
        if not self.async_interface:
            # Initialize async interface if not already done
            async_config = AsyncExecutionConfig(
                max_workers=self.config.performance.max_workers,
                enable_progress_tracking=self.config.logging.enable_progress_bars
            )
            self.async_interface = AsyncCausalInterface(async_config)
        
        return await self._comprehensive_analysis_async(*args, **kwargs)
    
    def generate_intervention_recommendations(self,
                                            analysis: ComprehensiveCausalAnalysis,
                                            target_outcome_variable: str,
                                            budget_constraint: Optional[float] = None,
                                            **kwargs) -> Dict[str, Any]:
        """
        Generate intervention recommendations with standardized interface.
        
        Args:
            analysis: Results from comprehensive analysis
            target_outcome_variable: Variable to optimize
            budget_constraint: Maximum budget for interventions
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with intervention recommendations
        """
        try:
            # Extract actionable relationships from analysis
            actionable_relationships = []
            
            for rel_name, inference_result in analysis.inference_results.items():
                if inference_result.primary_effect.p_value and inference_result.primary_effect.p_value < 0.05:
                    actionable_relationships.append({
                        'relationship': rel_name,
                        'effect_size': inference_result.primary_effect.estimate,
                        'confidence': inference_result.confidence_level,
                        'variable': inference_result.treatment_variable
                    })
            
            # Sort by effect size (absolute value)
            actionable_relationships.sort(
                key=lambda x: abs(x['effect_size']), reverse=True
            )
            
            # Generate recommendations
            primary_interventions = []
            secondary_interventions = []
            
            for i, rel in enumerate(actionable_relationships):
                intervention = {
                    'target_variable': rel['variable'],
                    'expected_outcome_change': rel['effect_size'],
                    'confidence_level': rel['confidence'],
                    'priority_rank': i + 1
                }
                
                if i < 3:  # Top 3 are primary
                    primary_interventions.append(intervention)
                else:
                    secondary_interventions.append(intervention)
            
            recommendations = {
                'primary_interventions': primary_interventions,
                'secondary_interventions': secondary_interventions,
                'total_relationships_analyzed': len(actionable_relationships),
                'analysis_confidence': analysis.confidence_score
            }
            
            if budget_constraint:
                recommendations['budget_constraint'] = budget_constraint
                # Add cost-effectiveness estimates (placeholder)
                for intervention in primary_interventions + secondary_interventions:
                    intervention['estimated_cost'] = budget_constraint * 0.1  # Placeholder
                    intervention['roi_estimate'] = abs(intervention['expected_outcome_change']) / intervention['estimated_cost']
            
            logger.info(f"Generated {len(primary_interventions)} primary interventions")
            return recommendations
            
        except Exception as e:
            logger.error(f"Intervention generation failed: {str(e)}")
            raise RuntimeError(f"Recommendation generation failed: {str(e)}") from e
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return self.config.to_dict()
    
    def update_configuration(self, **kwargs):
        """Update configuration with new parameters."""
        self.config.update(**kwargs)
        self._initialize_components()  # Re-initialize with new config
    
    def save_configuration(self, file_path: str):
        """Save current configuration to file."""
        self.config.save(file_path)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics and statistics."""
        metrics = self.performance_metrics.copy()
        
        if metrics['total_analyses'] > 0:
            metrics['average_execution_time'] = metrics['total_execution_time'] / metrics['total_analyses']
        else:
            metrics['average_execution_time'] = 0.0
        
        if self.async_interface:
            async_stats = self.async_interface.get_execution_stats()
            metrics.update({'async_stats': async_stats})
        
        return metrics
    
    def reset_performance_metrics(self):
        """Reset performance tracking metrics."""
        self.performance_metrics = {
            'total_analyses': 0,
            'total_execution_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _generate_cache_key(self, data: pd.DataFrame, *args) -> str:
        """Generate cache key for analysis results."""
        # Simple hash-based cache key (in production, use more sophisticated hashing)
        key_components = [
            str(data.shape),
            str(data.columns.tolist()),
            str(args)
        ]
        return hash(str(key_components))
    
    async def _comprehensive_analysis_async(self, *args, **kwargs) -> ComprehensiveCausalAnalysis:
        """Internal async comprehensive analysis."""
        return await self.async_interface.comprehensive_analysis_async(*args, **kwargs)
    
    def _comprehensive_analysis_sync(self, *args, **kwargs) -> ComprehensiveCausalAnalysis:
        """Internal synchronous comprehensive analysis."""
        # This would call the existing synchronous implementation
        # For now, return a placeholder result
        return ComprehensiveCausalAnalysis(
            discovery_results=CausalDiscoveryResult(
                discovered_edges=[],
                metadata=AnalysisMetadata("sync_discovery")
            ),
            inference_results={},
            metadata=AnalysisMetadata("sync_comprehensive")
        )
    
    def _discover_sync(self, *args, **kwargs) -> CausalDiscoveryResult:
        """Internal synchronous discovery."""
        # Placeholder for sync discovery
        return CausalDiscoveryResult(
            discovered_edges=[],
            metadata=AnalysisMetadata("sync_discovery")
        )
    
    def _estimate_effect_sync(self, *args, **kwargs) -> CausalInferenceResult:
        """Internal synchronous effect estimation."""
        # Placeholder for sync inference
        from .interfaces.base import StatisticalResult
        
        return CausalInferenceResult(
            primary_effect=StatisticalResult(estimate=0.0),
            treatment_variable=args[1] if len(args) > 1 else "treatment",
            outcome_variable=args[2] if len(args) > 2 else "outcome",
            metadata=AnalysisMetadata("sync_inference")
        )
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.async_interface:
            asyncio.run(self.async_interface.cleanup())
        
        logger.info("CausalLLM cleanup completed")


# Convenience functions with new interfaces

def create_enhanced_causal_llm(config_file: Optional[str] = None, **kwargs) -> EnhancedCausalLLM:
    """
    Create EnhancedCausalLLM instance with configuration.
    
    Args:
        config_file: Path to configuration file
        **kwargs: Configuration overrides
        
    Returns:
        Configured EnhancedCausalLLM instance
    """
    return EnhancedCausalLLM(config_file=config_file, **kwargs)


async def run_async_analysis(data: pd.DataFrame, 
                           config_file: Optional[str] = None,
                           **kwargs) -> ComprehensiveCausalAnalysis:
    """
    Convenience function for async comprehensive analysis.
    
    Args:
        data: Input DataFrame
        config_file: Configuration file path
        **kwargs: Analysis parameters
        
    Returns:
        ComprehensiveCausalAnalysis result
    """
    causal_llm = create_enhanced_causal_llm(config_file, use_async=True)
    try:
        return await causal_llm.comprehensive_analysis_async(data, **kwargs)
    finally:
        causal_llm.cleanup()


# Context manager for enhanced causal analysis

class CausalAnalysisContext:
    """Context manager for enhanced causal analysis with automatic cleanup."""
    
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        self.config_file = config_file
        self.kwargs = kwargs
        self.causal_llm = None
    
    def __enter__(self) -> EnhancedCausalLLM:
        self.causal_llm = create_enhanced_causal_llm(self.config_file, **self.kwargs)
        return self.causal_llm
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.causal_llm:
            self.causal_llm.cleanup()


# Example usage:
# with CausalAnalysisContext(config_file="my_config.json") as causal:
#     result = causal.comprehensive_analysis(data)