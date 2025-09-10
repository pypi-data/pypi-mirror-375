"""
Unified async interfaces for CausalLLM components.

This module provides consistent async interfaces across all CausalLLM components,
enabling efficient parallel processing and resource management.
"""

import asyncio
import time
from typing import Dict, List, Optional, Union, Any, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from .base import (
    CausalDiscoveryResult, CausalInferenceResult, ComprehensiveCausalAnalysis,
    AnalysisMetadata
)


@dataclass
class AsyncExecutionConfig:
    """Configuration for async execution."""
    max_workers: Optional[int] = None
    use_process_pool: bool = False
    timeout_seconds: Optional[float] = None
    enable_progress_tracking: bool = True
    chunk_size: Union[int, str] = 'auto'
    memory_limit_gb: Optional[float] = None


@dataclass
class AsyncTaskResult:
    """Result from async task execution."""
    task_id: str
    result: Any
    execution_time: float
    memory_usage_mb: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AsyncTaskManager:
    """Manages async task execution with resource monitoring."""
    
    def __init__(self, config: AsyncExecutionConfig):
        self.config = config
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: List[AsyncTaskResult] = []
        self.executor = self._create_executor()
    
    def _create_executor(self) -> Union[ThreadPoolExecutor, ProcessPoolExecutor]:
        """Create appropriate executor based on configuration."""
        if self.config.use_process_pool:
            return ProcessPoolExecutor(max_workers=self.config.max_workers)
        else:
            return ThreadPoolExecutor(max_workers=self.config.max_workers)
    
    async def submit_task(self, 
                         task_func: Callable,
                         task_id: str,
                         *args, 
                         **kwargs) -> AsyncTaskResult:
        """Submit a task for async execution."""
        start_time = time.time()
        
        try:
            # Create task
            if asyncio.iscoroutinefunction(task_func):
                task = asyncio.create_task(task_func(*args, **kwargs))
            else:
                loop = asyncio.get_event_loop()
                task = loop.run_in_executor(self.executor, task_func, *args, **kwargs)
            
            self.active_tasks[task_id] = task
            
            # Execute with timeout
            if self.config.timeout_seconds:
                result = await asyncio.wait_for(task, timeout=self.config.timeout_seconds)
            else:
                result = await task
            
            execution_time = time.time() - start_time
            
            # Create task result
            task_result = AsyncTaskResult(
                task_id=task_id,
                result=result,
                execution_time=execution_time,
                success=True
            )
            
            self.completed_tasks.append(task_result)
            del self.active_tasks[task_id]
            
            return task_result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            task_result = AsyncTaskResult(
                task_id=task_id,
                result=None,
                execution_time=execution_time,
                success=False,
                error=f"Task timed out after {self.config.timeout_seconds}s"
            )
            self.completed_tasks.append(task_result)
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            return task_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            task_result = AsyncTaskResult(
                task_id=task_id,
                result=None,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            self.completed_tasks.append(task_result)
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            return task_result
    
    async def submit_batch(self, 
                          tasks: List[tuple],
                          progress_callback: Optional[Callable] = None) -> List[AsyncTaskResult]:
        """Submit multiple tasks for parallel execution."""
        results = []
        
        for i, (task_func, task_id, args, kwargs) in enumerate(tasks):
            result = await self.submit_task(task_func, task_id, *args, **kwargs)
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, len(tasks), result)
        
        return results
    
    async def wait_for_all(self) -> List[AsyncTaskResult]:
        """Wait for all active tasks to complete."""
        if not self.active_tasks:
            return []
        
        # Wait for all active tasks
        await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)
        
        # Return results for completed tasks
        return [result for result in self.completed_tasks 
                if result.task_id in [task_id for task_id in self.active_tasks.keys()]]
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all tasks."""
        return {
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'successful_tasks': len([t for t in self.completed_tasks if t.success]),
            'failed_tasks': len([t for t in self.completed_tasks if not t.success]),
            'total_execution_time': sum(t.execution_time for t in self.completed_tasks),
            'average_execution_time': np.mean([t.execution_time for t in self.completed_tasks]) if self.completed_tasks else 0
        }
    
    def cleanup(self):
        """Clean up resources."""
        self.executor.shutdown(wait=True)
        self.active_tasks.clear()


class AsyncCausalInterface:
    """Unified async interface for all causal analysis operations."""
    
    def __init__(self, config: Optional[AsyncExecutionConfig] = None):
        self.config = config or AsyncExecutionConfig()
        self.task_manager = AsyncTaskManager(self.config)
    
    async def discover_causal_structure_async(self,
                                            data: pd.DataFrame,
                                            variable_names: Optional[List[str]] = None,
                                            domain_context: Optional[str] = None,
                                            method: str = 'pc_algorithm',
                                            **kwargs) -> CausalDiscoveryResult:
        """Async causal structure discovery."""
        task_id = f"discovery_{int(time.time())}"
        
        # Import discovery engine dynamically to avoid circular imports
        from ..core.causal_discovery import create_discovery_engine
        
        def discovery_task():
            engine = create_discovery_engine(method)
            return engine.discover_structure(data, variable_names, **kwargs)
        
        result = await self.task_manager.submit_task(discovery_task, task_id)
        
        if not result.success:
            raise RuntimeError(f"Discovery failed: {result.error}")
        
        return result.result
    
    async def estimate_causal_effect_async(self,
                                         data: pd.DataFrame,
                                         treatment_variable: str,
                                         outcome_variable: str,
                                         covariate_variables: Optional[List[str]] = None,
                                         method: str = 'comprehensive',
                                         **kwargs) -> CausalInferenceResult:
        """Async causal effect estimation."""
        task_id = f"inference_{int(time.time())}"
        
        # Import inference engine dynamically
        from ..core.statistical_inference import StatisticalCausalInference
        
        def inference_task():
            engine = StatisticalCausalInference(**kwargs)
            return engine.estimate_causal_effect(
                data, treatment_variable, outcome_variable, 
                covariate_variables, method
            )
        
        result = await self.task_manager.submit_task(inference_task, task_id)
        
        if not result.success:
            raise RuntimeError(f"Inference failed: {result.error}")
        
        return result.result
    
    async def comprehensive_analysis_async(self,
                                         data: pd.DataFrame,
                                         treatment_variable: Optional[str] = None,
                                         outcome_variable: Optional[str] = None,
                                         variable_names: Optional[List[str]] = None,
                                         domain_context: Optional[str] = None,
                                         covariate_variables: Optional[List[str]] = None,
                                         **kwargs) -> ComprehensiveCausalAnalysis:
        """Async comprehensive causal analysis."""
        
        # Step 1: Discovery (if no specific variables provided)
        discovery_result = None
        if not treatment_variable or not outcome_variable:
            discovery_result = await self.discover_causal_structure_async(
                data, variable_names, domain_context, **kwargs
            )
            
            # Extract top relationships for inference
            if not treatment_variable and discovery_result.discovered_edges:
                treatment_variable = discovery_result.discovered_edges[0].cause
            if not outcome_variable and discovery_result.discovered_edges:
                outcome_variable = discovery_result.discovered_edges[0].effect
        
        # Step 2: Parallel inference for discovered relationships
        inference_tasks = []
        relationship_names = []
        
        if discovery_result:
            for i, edge in enumerate(discovery_result.discovered_edges[:5]):  # Top 5 relationships
                task_id = f"inference_{edge.cause}_{edge.effect}_{i}"
                relationship_names.append(f"{edge.cause} → {edge.effect}")
                
                inference_tasks.append((
                    self._inference_wrapper,
                    task_id,
                    (data, edge.cause, edge.effect, covariate_variables),
                    kwargs
                ))
        else:
            # Single inference task
            task_id = f"inference_{treatment_variable}_{outcome_variable}"
            relationship_names.append(f"{treatment_variable} → {outcome_variable}")
            
            inference_tasks.append((
                self._inference_wrapper,
                task_id,
                (data, treatment_variable, outcome_variable, covariate_variables),
                kwargs
            ))
        
        # Execute inference tasks in parallel
        inference_results = await self.task_manager.submit_batch(inference_tasks)
        
        # Compile results
        inference_dict = {}
        for i, result in enumerate(inference_results):
            if result.success:
                inference_dict[relationship_names[i]] = result.result
        
        # Create comprehensive result
        if not discovery_result:
            # Create minimal discovery result
            discovery_result = CausalDiscoveryResult(
                discovered_edges=[],
                metadata=AnalysisMetadata("comprehensive_discovery")
            )
        
        comprehensive_result = ComprehensiveCausalAnalysis(
            discovery_results=discovery_result,
            inference_results=inference_dict,
            metadata=AnalysisMetadata("comprehensive_analysis")
        )
        
        # Calculate confidence score
        successful_inferences = [r for r in inference_results if r.success]
        if successful_inferences:
            avg_confidence = np.mean([
                0.8 if result.result.primary_effect.p_value < 0.05 else 0.4
                for result in successful_inferences
                if result.result.primary_effect.p_value is not None
            ])
            comprehensive_result.confidence_score = avg_confidence
        
        return comprehensive_result
    
    def _inference_wrapper(self, data: pd.DataFrame, 
                          treatment: str, 
                          outcome: str, 
                          covariates: Optional[List[str]],
                          **kwargs) -> CausalInferenceResult:
        """Wrapper for inference to be used in async tasks."""
        from ..core.statistical_inference import StatisticalCausalInference
        
        engine = StatisticalCausalInference(**kwargs)
        return engine.estimate_causal_effect(data, treatment, outcome, covariates)
    
    async def parallel_bootstrap_analysis(self,
                                        data: pd.DataFrame,
                                        analysis_func: Callable,
                                        n_bootstrap: int = 1000,
                                        confidence_level: float = 0.95,
                                        **kwargs) -> Dict[str, Any]:
        """Perform bootstrap analysis using parallel processing."""
        
        # Create bootstrap samples
        bootstrap_tasks = []
        for i in range(n_bootstrap):
            task_id = f"bootstrap_{i}"
            
            # Create bootstrap sample
            bootstrap_sample = data.sample(n=len(data), replace=True)
            
            bootstrap_tasks.append((
                analysis_func,
                task_id,
                (bootstrap_sample,),
                kwargs
            ))
        
        # Execute bootstrap tasks in parallel
        bootstrap_results = await self.task_manager.submit_batch(bootstrap_tasks)
        
        # Compile bootstrap statistics
        successful_results = [r.result for r in bootstrap_results if r.success]
        
        if not successful_results:
            raise RuntimeError("All bootstrap samples failed")
        
        # Calculate confidence intervals
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        if isinstance(successful_results[0], (int, float)):
            # Scalar results
            estimates = successful_results
            mean_estimate = np.mean(estimates)
            std_error = np.std(estimates)
            ci_lower = np.percentile(estimates, lower_percentile)
            ci_upper = np.percentile(estimates, upper_percentile)
            
            return {
                'mean_estimate': mean_estimate,
                'std_error': std_error,
                'confidence_interval': (ci_lower, ci_upper),
                'confidence_level': confidence_level,
                'n_bootstrap': len(successful_results),
                'bootstrap_estimates': estimates
            }
        else:
            # Complex results - return raw bootstrap results
            return {
                'bootstrap_results': successful_results,
                'n_bootstrap': len(successful_results),
                'confidence_level': confidence_level
            }
    
    async def parallel_correlation_analysis(self,
                                          data: pd.DataFrame,
                                          chunk_size: int = 5000,
                                          method: str = 'pearson',
                                          **kwargs) -> pd.DataFrame:
        """Compute correlation matrix using parallel processing."""
        
        if len(data) <= chunk_size:
            # Small dataset - compute directly
            return data.corr(method=method)
        
        # Split data into chunks
        chunks = [data.iloc[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        
        # Create correlation tasks
        corr_tasks = []
        for i, chunk in enumerate(chunks):
            task_id = f"corr_chunk_{i}"
            corr_tasks.append((
                lambda chunk_data: chunk_data.corr(method=method),
                task_id,
                (chunk,),
                {}
            ))
        
        # Execute correlation tasks in parallel
        corr_results = await self.task_manager.submit_batch(corr_tasks)
        
        # Combine correlation matrices
        successful_corrs = [r.result for r in corr_results if r.success]
        
        if not successful_corrs:
            raise RuntimeError("All correlation computations failed")
        
        # Average correlation matrices (weighted by chunk size)
        combined_corr = sum(successful_corrs) / len(successful_corrs)
        
        return combined_corr
    
    async def cleanup(self):
        """Clean up async resources."""
        await self.task_manager.wait_for_all()
        self.task_manager.cleanup()
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return self.task_manager.get_task_status()


# Convenience functions for async operations

async def run_async_discovery(data: pd.DataFrame, 
                             config: Optional[AsyncExecutionConfig] = None,
                             **kwargs) -> CausalDiscoveryResult:
    """Convenience function for async causal discovery."""
    interface = AsyncCausalInterface(config)
    try:
        result = await interface.discover_causal_structure_async(data, **kwargs)
        return result
    finally:
        await interface.cleanup()


async def run_async_inference(data: pd.DataFrame,
                             treatment: str,
                             outcome: str,
                             config: Optional[AsyncExecutionConfig] = None,
                             **kwargs) -> CausalInferenceResult:
    """Convenience function for async causal inference."""
    interface = AsyncCausalInterface(config)
    try:
        result = await interface.estimate_causal_effect_async(
            data, treatment, outcome, **kwargs
        )
        return result
    finally:
        await interface.cleanup()


async def run_comprehensive_analysis(data: pd.DataFrame,
                                   config: Optional[AsyncExecutionConfig] = None,
                                   **kwargs) -> ComprehensiveCausalAnalysis:
    """Convenience function for async comprehensive analysis."""
    interface = AsyncCausalInterface(config)
    try:
        result = await interface.comprehensive_analysis_async(data, **kwargs)
        return result
    finally:
        await interface.cleanup()


# Context manager for async interface

class AsyncCausalContext:
    """Context manager for async causal analysis operations."""
    
    def __init__(self, config: Optional[AsyncExecutionConfig] = None):
        self.config = config
        self.interface = None
    
    async def __aenter__(self) -> AsyncCausalInterface:
        self.interface = AsyncCausalInterface(self.config)
        return self.interface
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.interface:
            await self.interface.cleanup()


# Example usage:
# async def main():
#     async with AsyncCausalContext() as causal:
#         result = await causal.comprehensive_analysis_async(data)
#         return result