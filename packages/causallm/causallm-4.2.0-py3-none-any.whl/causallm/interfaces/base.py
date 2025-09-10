"""
Standardized interfaces for CausalLLM components.

This module defines abstract base classes and protocols that ensure consistent
interfaces across all CausalLLM components, including unified parameter naming,
async support, and standardized result types.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Protocol, TypeVar, Generic
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio

# Type variables for generic interfaces
T = TypeVar('T')
ResultType = TypeVar('ResultType')


@dataclass
class AnalysisMetadata:
    """Standard metadata for all analysis results."""
    analysis_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    method_used: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    execution_time_seconds: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    confidence_level: float = 0.95
    warnings: List[str] = field(default_factory=list)
    version: str = "4.0.0"


@dataclass
class CausalEdge:
    """Standard representation of a causal relationship."""
    cause: str
    effect: str
    confidence: float
    effect_size: Optional[float] = None
    p_value: Optional[float] = None
    method: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.cause} → {self.effect} (conf: {self.confidence:.3f})"


@dataclass
class StatisticalResult:
    """Standard statistical result with confidence intervals."""
    estimate: float
    std_error: Optional[float] = None
    confidence_interval: Optional[tuple] = None
    p_value: Optional[float] = None
    test_statistic: Optional[float] = None
    degrees_of_freedom: Optional[int] = None
    method: str = ""
    assumptions_met: bool = True
    assumption_tests: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalDiscoveryResult:
    """Standardized result from causal structure discovery."""
    discovered_edges: List[CausalEdge]
    adjacency_matrix: Optional[np.ndarray] = None
    variable_names: List[str] = field(default_factory=list)
    graph_density: float = 0.0
    suggested_confounders: List[str] = field(default_factory=list)
    domain_insights: Dict[str, Any] = field(default_factory=dict)
    statistical_summary: Dict[str, float] = field(default_factory=dict)
    metadata: AnalysisMetadata = field(default_factory=lambda: AnalysisMetadata("discovery"))
    
    def get_edges_by_confidence(self, min_confidence: float = 0.5) -> List[CausalEdge]:
        """Filter edges by minimum confidence threshold."""
        return [edge for edge in self.discovered_edges if edge.confidence >= min_confidence]
    
    def to_networkx(self):
        """Convert to NetworkX graph object."""
        try:
            import networkx as nx
            G = nx.DiGraph()
            for edge in self.discovered_edges:
                G.add_edge(edge.cause, edge.effect, 
                          confidence=edge.confidence,
                          effect_size=edge.effect_size)
            return G
        except ImportError:
            raise ImportError("NetworkX is required for graph conversion. Install with: pip install networkx")


@dataclass  
class CausalInferenceResult:
    """Standardized result from causal effect estimation."""
    primary_effect: StatisticalResult
    treatment_variable: str
    outcome_variable: str
    covariates: List[str] = field(default_factory=list)
    robustness_checks: List[StatisticalResult] = field(default_factory=list)
    sensitivity_analysis: Dict[str, Any] = field(default_factory=dict)
    assumptions_tested: Dict[str, bool] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    interpretation: str = ""
    clinical_significance: Optional[str] = None
    metadata: AnalysisMetadata = field(default_factory=lambda: AnalysisMetadata("inference"))
    
    @property
    def confidence_level(self) -> str:
        """Get overall confidence assessment."""
        primary_sig = self.primary_effect.p_value < 0.05 if self.primary_effect.p_value else False
        robust_count = sum(1 for result in self.robustness_checks 
                          if result.p_value and result.p_value < 0.05)
        
        if primary_sig and robust_count >= len(self.robustness_checks) * 0.7:
            return "High"
        elif primary_sig and robust_count >= len(self.robustness_checks) * 0.5:
            return "Medium"
        else:
            return "Low"


@dataclass
class ComprehensiveCausalAnalysis:
    """Complete analysis result combining discovery and inference."""
    discovery_results: CausalDiscoveryResult
    inference_results: Dict[str, CausalInferenceResult]
    domain_recommendations: List[str] = field(default_factory=list)
    actionable_insights: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: AnalysisMetadata = field(default_factory=lambda: AnalysisMetadata("comprehensive"))
    
    def get_top_relationships(self, n: int = 5) -> List[tuple]:
        """Get top N causal relationships by effect size."""
        relationships = []
        for rel_name, result in self.inference_results.items():
            relationships.append((rel_name, result.primary_effect.estimate))
        
        return sorted(relationships, key=lambda x: abs(x[1]), reverse=True)[:n]


# Protocol definitions for standardized interfaces

class CausalAnalyzer(Protocol):
    """Protocol for causal analysis components."""
    
    def analyze(self, 
                data: pd.DataFrame,
                treatment_variable: str,
                outcome_variable: str,
                covariate_variables: Optional[List[str]] = None,
                **kwargs) -> CausalInferenceResult:
        """Perform causal analysis with standardized interface."""
        ...
    
    async def analyze_async(self, 
                           data: pd.DataFrame,
                           treatment_variable: str,
                           outcome_variable: str,
                           covariate_variables: Optional[List[str]] = None,
                           **kwargs) -> CausalInferenceResult:
        """Async version of causal analysis."""
        ...


class CausalDiscoverer(Protocol):
    """Protocol for causal structure discovery components."""
    
    def discover(self,
                data: pd.DataFrame,
                variable_names: Optional[List[str]] = None,
                domain_context: Optional[str] = None,
                **kwargs) -> CausalDiscoveryResult:
        """Discover causal structure with standardized interface."""
        ...
    
    async def discover_async(self,
                            data: pd.DataFrame,
                            variable_names: Optional[List[str]] = None,
                            domain_context: Optional[str] = None,
                            **kwargs) -> CausalDiscoveryResult:
        """Async version of causal discovery."""
        ...


class DataProcessor(Protocol):
    """Protocol for data processing components."""
    
    def process(self, 
               data: pd.DataFrame,
               chunk_size: Optional[int] = None,
               **kwargs) -> pd.DataFrame:
        """Process data with standardized interface."""
        ...
    
    async def process_async(self, 
                           data: pd.DataFrame,
                           chunk_size: Optional[int] = None,
                           **kwargs) -> pd.DataFrame:
        """Async version of data processing."""
        ...


class DomainPackage(Protocol):
    """Protocol for domain-specific packages."""
    
    def generate_data(self, 
                     n_samples: int,
                     **kwargs) -> pd.DataFrame:
        """Generate domain-specific synthetic data."""
        ...
    
    def get_domain_knowledge(self) -> Dict[str, Any]:
        """Get domain-specific knowledge and constraints."""
        ...
    
    def analyze_domain_specific(self,
                               data: pd.DataFrame,
                               analysis_type: str,
                               **kwargs) -> Union[CausalDiscoveryResult, CausalInferenceResult]:
        """Perform domain-specific analysis."""
        ...


# Abstract base classes for implementation

class BaseCausalAnalyzer(ABC):
    """Base class for causal analyzers with standardized interface."""
    
    def __init__(self, 
                 significance_level: float = 0.05,
                 confidence_level: float = 0.95,
                 **kwargs):
        self.significance_level = significance_level
        self.confidence_level = confidence_level
        self.config = kwargs
    
    @abstractmethod
    def analyze(self, 
                data: pd.DataFrame,
                treatment_variable: str,
                outcome_variable: str,
                covariate_variables: Optional[List[str]] = None,
                **kwargs) -> CausalInferenceResult:
        """Implement causal analysis logic."""
        pass
    
    async def analyze_async(self, 
                           data: pd.DataFrame,
                           treatment_variable: str,
                           outcome_variable: str,
                           covariate_variables: Optional[List[str]] = None,
                           **kwargs) -> CausalInferenceResult:
        """Default async implementation using thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.analyze, 
            data, treatment_variable, outcome_variable, covariate_variables
        )
    
    def _create_metadata(self, method_name: str, parameters: Dict[str, Any]) -> AnalysisMetadata:
        """Create standardized metadata."""
        return AnalysisMetadata(
            analysis_id=f"{method_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            method_used=method_name,
            parameters=parameters,
            confidence_level=self.confidence_level
        )


class BaseCausalDiscoverer(ABC):
    """Base class for causal discoverers with standardized interface."""
    
    def __init__(self, 
                 significance_level: float = 0.05,
                 max_conditioning_set_size: int = 2,
                 **kwargs):
        self.significance_level = significance_level
        self.max_conditioning_set_size = max_conditioning_set_size
        self.config = kwargs
    
    @abstractmethod
    def discover(self,
                data: pd.DataFrame,
                variable_names: Optional[List[str]] = None,
                domain_context: Optional[str] = None,
                **kwargs) -> CausalDiscoveryResult:
        """Implement causal discovery logic."""
        pass
    
    async def discover_async(self,
                            data: pd.DataFrame,
                            variable_names: Optional[List[str]] = None,
                            domain_context: Optional[str] = None,
                            **kwargs) -> CausalDiscoveryResult:
        """Default async implementation using thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.discover, 
            data, variable_names, domain_context
        )
    
    def _create_metadata(self, method_name: str, parameters: Dict[str, Any]) -> AnalysisMetadata:
        """Create standardized metadata."""
        return AnalysisMetadata(
            analysis_id=f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            method_used=method_name,
            parameters=parameters
        )


class BaseDataProcessor(ABC):
    """Base class for data processors with standardized interface."""
    
    def __init__(self, 
                 chunk_size: Union[int, str] = 'auto',
                 enable_parallel: bool = True,
                 **kwargs):
        self.chunk_size = chunk_size
        self.enable_parallel = enable_parallel
        self.config = kwargs
    
    @abstractmethod
    def process(self, 
               data: pd.DataFrame,
               chunk_size: Optional[int] = None,
               **kwargs) -> pd.DataFrame:
        """Implement data processing logic."""
        pass
    
    async def process_async(self, 
                           data: pd.DataFrame,
                           chunk_size: Optional[int] = None,
                           **kwargs) -> pd.DataFrame:
        """Default async implementation using thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.process, 
            data, chunk_size
        )


class BaseDomainPackage(ABC):
    """Base class for domain packages with standardized interface."""
    
    def __init__(self, 
                 domain_name: str,
                 enable_performance_optimizations: bool = True,
                 **kwargs):
        self.domain_name = domain_name
        self.enable_performance_optimizations = enable_performance_optimizations
        self.config = kwargs
    
    @abstractmethod
    def generate_data(self, 
                     n_samples: int,
                     **kwargs) -> pd.DataFrame:
        """Generate domain-specific synthetic data."""
        pass
    
    @abstractmethod
    def get_domain_knowledge(self) -> Dict[str, Any]:
        """Get domain-specific knowledge and constraints."""
        pass
    
    @abstractmethod
    def analyze_domain_specific(self,
                               data: pd.DataFrame,
                               analysis_type: str,
                               **kwargs) -> Union[CausalDiscoveryResult, CausalInferenceResult]:
        """Perform domain-specific analysis."""
        pass


# Utility functions for interface standardization

def standardize_column_names(data: pd.DataFrame, 
                           treatment_col: str, 
                           outcome_col: str,
                           covariate_cols: Optional[List[str]] = None) -> Dict[str, str]:
    """Standardize column names for consistent interface."""
    mapping = {}
    
    # Check if columns exist
    if treatment_col not in data.columns:
        raise ValueError(f"Treatment variable '{treatment_col}' not found in data")
    if outcome_col not in data.columns:
        raise ValueError(f"Outcome variable '{outcome_col}' not found in data")
    
    mapping['treatment'] = treatment_col
    mapping['outcome'] = outcome_col
    
    if covariate_cols:
        missing_covs = [col for col in covariate_cols if col not in data.columns]
        if missing_covs:
            raise ValueError(f"Covariate variables not found: {missing_covs}")
        mapping['covariates'] = covariate_cols
    
    return mapping


def validate_data_requirements(data: pd.DataFrame, 
                              min_samples: int = 50,
                              min_treatment_groups: int = 2) -> bool:
    """Validate data meets minimum requirements for analysis."""
    if len(data) < min_samples:
        raise ValueError(f"Insufficient data: {len(data)} samples (minimum: {min_samples})")
    
    # Check for sufficient variation in treatment if specified
    treatment_cols = [col for col in data.columns if 'treatment' in col.lower()]
    if treatment_cols:
        unique_treatments = data[treatment_cols[0]].nunique()
        if unique_treatments < min_treatment_groups:
            raise ValueError(f"Insufficient treatment variation: {unique_treatments} groups (minimum: {min_treatment_groups})")
    
    return True


def create_async_wrapper(sync_func):
    """Decorator to create async wrapper for synchronous functions."""
    async def async_wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sync_func, *args, **kwargs)
    
    return async_wrapper