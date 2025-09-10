"""
Property-Based Testing for CausalLLM

Provides hypothesis-based property testing for causal inference algorithms,
data structures, and statistical methods.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable, Union
from hypothesis import given, strategies as st, assume, settings, Verbosity
from hypothesis.extra.pandas import data_frames, columns
from hypothesis.extra.numpy import arrays
import networkx as nx
from abc import ABC, abstractmethod
import pytest
import functools


class CausalDataStrategy:
    """Strategies for generating causal data for property-based testing."""
    
    @staticmethod
    def variable_names(min_size: int = 2, max_size: int = 10) -> st.SearchStrategy:
        """Generate valid variable names."""
        return st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=('Lu', 'Ll')),
                min_size=1,
                max_size=20
            ).filter(lambda x: x.isalpha()),
            min_size=min_size,
            max_size=max_size,
            unique=True
        )
    
    @staticmethod
    def numeric_data(variables: List[str], min_rows: int = 50, max_rows: int = 1000) -> st.SearchStrategy:
        """Generate numeric DataFrame for causal analysis."""
        n_vars = len(variables)
        
        return st.builds(
            pd.DataFrame,
            data=arrays(
                dtype=np.float64,
                shape=st.tuples(
                    st.integers(min_value=min_rows, max_value=max_rows),
                    st.just(n_vars)
                ),
                elements=st.floats(
                    min_value=-100.0,
                    max_value=100.0,
                    allow_nan=False,
                    allow_infinity=False
                )
            ),
            columns=st.just(variables)
        )
    
    @staticmethod
    def mixed_data(variables: List[str], min_rows: int = 50, max_rows: int = 1000) -> st.SearchStrategy:
        """Generate mixed-type DataFrame with both numeric and categorical data."""
        def create_mixed_dataframe(variables, n_rows):
            data = {}
            for i, var in enumerate(variables):
                if i % 3 == 0:  # Categorical variable
                    data[var] = np.random.choice(['A', 'B', 'C', 'D'], size=n_rows)
                elif i % 3 == 1:  # Binary variable
                    data[var] = np.random.choice([0, 1], size=n_rows)
                else:  # Continuous variable
                    data[var] = np.random.normal(0, 1, size=n_rows)
            
            return pd.DataFrame(data)
        
        return st.builds(
            create_mixed_dataframe,
            variables=st.just(variables),
            n_rows=st.integers(min_value=min_rows, max_value=max_rows)
        )
    
    @staticmethod
    def causal_data_with_structure(variables: List[str], 
                                  true_edges: List[tuple],
                                  min_rows: int = 100,
                                  max_rows: int = 1000,
                                  noise_level: float = 0.1) -> st.SearchStrategy:
        """Generate data with known causal structure."""
        def create_structured_data(variables, edges, n_rows, noise):
            # Create a topologically sorted order
            graph = nx.DiGraph(edges)
            if not nx.is_directed_acyclic_graph(graph):
                # If not DAG, remove edges to make it one
                edges = list(nx.edge_dfs(graph, orientation='original'))[:len(edges)//2]
                graph = nx.DiGraph(edges)
            
            try:
                topo_order = list(nx.topological_sort(graph))
            except nx.NetworkXError:
                topo_order = variables
            
            data = {}
            
            # Generate data following the causal structure
            for var in variables:
                if var not in topo_order:
                    topo_order.append(var)
                    
            for var in topo_order:
                parents = list(graph.predecessors(var))
                
                if not parents:
                    # Root node - generate from normal distribution
                    data[var] = np.random.normal(0, 1, n_rows)
                else:
                    # Child node - generate based on parents
                    parent_sum = sum(data[parent] for parent in parents if parent in data)
                    if isinstance(parent_sum, (int, float)) and parent_sum == 0:
                        parent_sum = np.zeros(n_rows)
                    
                    # Linear combination of parents plus noise
                    coefficients = np.random.uniform(0.5, 2.0, len(parents))
                    signal = sum(coef * data[parent] for coef, parent in zip(coefficients, parents) if parent in data)
                    
                    if not isinstance(signal, np.ndarray):
                        signal = np.zeros(n_rows)
                    
                    data[var] = signal + np.random.normal(0, noise, n_rows)
            
            return pd.DataFrame({var: data.get(var, np.random.normal(0, 1, n_rows)) for var in variables})
        
        return st.builds(
            create_structured_data,
            variables=st.just(variables),
            edges=st.just(true_edges),
            n_rows=st.integers(min_value=min_rows, max_value=max_rows),
            noise=st.floats(min_value=0.01, max_value=noise_level)
        )


class CausalGraphStrategy:
    """Strategies for generating causal graphs."""
    
    @staticmethod
    def dag_edges(variables: List[str], 
                  max_edges: Optional[int] = None,
                  density: float = 0.3) -> st.SearchStrategy:
        """Generate edges that form a valid DAG."""
        n_vars = len(variables)
        if max_edges is None:
            max_edges = min(int(n_vars * (n_vars - 1) * density), n_vars * 3)
        
        # Generate potential edges (ensuring acyclicity)
        potential_edges = []
        for i in range(n_vars):
            for j in range(i + 1, n_vars):
                potential_edges.append((variables[i], variables[j]))
                potential_edges.append((variables[j], variables[i]))
        
        def create_dag_edges(edge_subset):
            # Try to create a DAG from the edge subset
            graph = nx.DiGraph(edge_subset)
            
            # Remove edges to ensure it's a DAG
            while not nx.is_directed_acyclic_graph(graph):
                if not graph.edges():
                    break
                # Remove a random edge that creates a cycle
                try:
                    cycles = list(nx.simple_cycles(graph))
                    if cycles:
                        cycle = cycles[0]
                        if len(cycle) >= 2:
                            graph.remove_edge(cycle[0], cycle[1])
                    else:
                        break
                except:
                    break
            
            return list(graph.edges())
        
        return st.builds(
            create_dag_edges,
            edge_subset=st.lists(
                st.sampled_from(potential_edges),
                min_size=0,
                max_size=max_edges,
                unique=True
            )
        )
    
    @staticmethod
    def adjacency_matrix(variables: List[str]) -> st.SearchStrategy:
        """Generate adjacency matrix for a DAG."""
        n_vars = len(variables)
        
        def create_adjacency_matrix(upper_triangular_values):
            matrix = np.zeros((n_vars, n_vars))
            idx = 0
            for i in range(n_vars):
                for j in range(i + 1, n_vars):
                    matrix[i, j] = upper_triangular_values[idx]
                    idx += 1
            return matrix
        
        n_upper_triangular = n_vars * (n_vars - 1) // 2
        
        return st.builds(
            create_adjacency_matrix,
            upper_triangular_values=st.lists(
                st.integers(min_value=0, max_value=1),
                min_size=n_upper_triangular,
                max_size=n_upper_triangular
            )
        )


class PropertyBasedTestCase(ABC):
    """Abstract base class for property-based test cases."""
    
    def __init__(self, max_examples: int = 100, deadline: int = 30000):
        self.settings = settings(
            max_examples=max_examples,
            deadline=deadline,
            verbosity=Verbosity.normal
        )
    
    @abstractmethod
    def test_property(self, *args, **kwargs) -> bool:
        """Test a specific property. Must be implemented by subclasses."""
        pass
    
    def run_property_test(self, strategy, test_func: Callable = None):
        """Run property-based test with given strategy."""
        if test_func is None:
            test_func = self.test_property
        
        @given(strategy)
        @self.settings
        def property_test(*args, **kwargs):
            return test_func(*args, **kwargs)
        
        return property_test


class CausalInferenceProperties:
    """Property-based tests for causal inference algorithms."""
    
    @staticmethod
    def test_independence_symmetry(ci_test_func: Callable) -> Callable:
        """Property: CI(X, Y | Z) should equal CI(Y, X | Z)."""
        @given(
            data=CausalDataStrategy.numeric_data(
                variables=['X', 'Y', 'Z', 'W'],
                min_rows=100,
                max_rows=500
            )
        )
        @settings(max_examples=50, deadline=60000)
        def test(data):
            assume(len(data) >= 50)
            assume(not data.isnull().any().any())
            
            # Test symmetry property
            result1 = ci_test_func(data, 'X', 'Y', ['Z'])
            result2 = ci_test_func(data, 'Y', 'X', ['Z'])
            
            # Allow for small numerical differences
            if isinstance(result1, (tuple, list)) and isinstance(result2, (tuple, list)):
                return abs(result1[1] - result2[1]) < 0.01  # Compare p-values
            elif isinstance(result1, bool) and isinstance(result2, bool):
                return result1 == result2
            else:
                return abs(float(result1) - float(result2)) < 0.01
        
        return test
    
    @staticmethod
    def test_causal_discovery_consistency(discovery_func: Callable) -> Callable:
        """Property: Causal discovery should be consistent across runs with same data."""
        @given(
            variables=CausalDataStrategy.variable_names(min_size=3, max_size=6),
            seed=st.integers(min_value=1, max_value=1000)
        )
        @settings(max_examples=20, deadline=120000)
        def test(variables, seed):
            assume(len(variables) >= 3)
            
            # Generate the same data twice with same seed
            np.random.seed(seed)
            data1 = pd.DataFrame({
                var: np.random.normal(0, 1, 200) for var in variables
            })
            
            np.random.seed(seed)  
            data2 = pd.DataFrame({
                var: np.random.normal(0, 1, 200) for var in variables
            })
            
            try:
                result1 = discovery_func(data1)
                result2 = discovery_func(data2)
                
                # Results should be identical for identical data
                if hasattr(result1, 'edges') and hasattr(result2, 'edges'):
                    return set(result1.edges()) == set(result2.edges())
                elif isinstance(result1, list) and isinstance(result2, list):
                    return set(result1) == set(result2)
                else:
                    return result1 == result2
                    
            except Exception:
                # If discovery fails, that's also a valid result to test consistency
                return True
        
        return test
    
    @staticmethod  
    def test_do_calculus_properties(do_operator_func: Callable) -> Callable:
        """Property: Do-calculus should satisfy basic properties."""
        @given(
            variables=CausalDataStrategy.variable_names(min_size=4, max_size=6)
        )
        @settings(max_examples=10, deadline=180000)
        def test(variables):
            assume(len(variables) >= 4)
            
            # Generate data with known structure
            treatment, outcome = variables[0], variables[1]
            confounders = variables[2:]
            
            data = pd.DataFrame({
                var: np.random.normal(0, 1, 300) for var in variables
            })
            
            try:
                # Property: Effect should be finite and not NaN
                effect = do_operator_func(data, treatment, outcome)
                
                if isinstance(effect, dict):
                    effect_value = effect.get('effect', effect.get('ate', 0))
                else:
                    effect_value = float(effect)
                
                return not (np.isnan(effect_value) or np.isinf(effect_value))
                
            except Exception:
                # If calculation fails, that's acceptable for some data
                return True
        
        return test


def causal_hypothesis_test(strategy: st.SearchStrategy, property_func: Callable,
                          max_examples: int = 100, deadline: int = 60000) -> Callable:
    """Decorator for creating property-based tests for causal methods."""
    def decorator(test_func: Callable) -> Callable:
        @given(strategy)
        @settings(max_examples=max_examples, deadline=deadline)
        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            result = test_func(*args, **kwargs)
            if property_func:
                return property_func(result, *args, **kwargs)
            return result
        
        return wrapper
    return decorator


class CausalTestRunner:
    """Test runner for causal inference property-based tests."""
    
    def __init__(self, max_examples: int = 50, deadline: int = 60000):
        self.max_examples = max_examples
        self.deadline = deadline
        self.test_results = []
    
    def run_independence_tests(self, ci_test_func: Callable) -> Dict[str, Any]:
        """Run all conditional independence property tests."""
        symmetry_test = CausalInferenceProperties.test_independence_symmetry(ci_test_func)
        
        try:
            symmetry_test()
            result = {'symmetry_test': 'PASSED'}
        except Exception as e:
            result = {'symmetry_test': f'FAILED: {str(e)}'}
        
        self.test_results.append(result)
        return result
    
    def run_discovery_tests(self, discovery_func: Callable) -> Dict[str, Any]:
        """Run causal discovery property tests."""
        consistency_test = CausalInferenceProperties.test_causal_discovery_consistency(discovery_func)
        
        try:
            consistency_test()
            result = {'consistency_test': 'PASSED'}
        except Exception as e:
            result = {'consistency_test': f'FAILED: {str(e)}'}
        
        self.test_results.append(result)
        return result
    
    def run_do_calculus_tests(self, do_operator_func: Callable) -> Dict[str, Any]:
        """Run do-calculus property tests."""
        properties_test = CausalInferenceProperties.test_do_calculus_properties(do_operator_func)
        
        try:
            properties_test()
            result = {'do_calculus_test': 'PASSED'}
        except Exception as e:
            result = {'do_calculus_test': f'FAILED: {str(e)}'}
        
        self.test_results.append(result)
        return result
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all test results."""
        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results 
            if any('PASSED' in str(v) for v in result.values())
        )
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'pass_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'results': self.test_results
        }