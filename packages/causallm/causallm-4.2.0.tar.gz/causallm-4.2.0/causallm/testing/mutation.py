"""
Mutation Testing System for CausalLLM

Provides mutation testing capabilities to assess test suite quality
by introducing systematic code changes and verifying tests catch them.
"""

import ast
import copy
import subprocess
import tempfile
import os
import sys
from typing import Dict, List, Any, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import random
import importlib.util


@dataclass
class MutationResult:
    """Result of a single mutation test."""
    mutation_id: str
    mutator_name: str
    file_path: str
    line_number: int
    original_code: str
    mutated_code: str
    killed: bool  # True if tests detected the mutation
    test_output: str
    execution_time: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'mutation_id': self.mutation_id,
            'mutator_name': self.mutator_name,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'original_code': self.original_code,
            'mutated_code': self.mutated_code,
            'killed': self.killed,
            'test_output': self.test_output,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class MutationTestConfig:
    """Configuration for mutation testing."""
    target_files: List[str] = field(default_factory=list)
    test_command: str = "pytest"
    timeout: int = 300  # 5 minutes default
    skip_patterns: List[str] = field(default_factory=lambda: ["__init__.py", "test_"])
    mutation_score_threshold: float = 0.8
    max_mutations_per_file: int = 50
    random_seed: Optional[int] = None
    
    def __post_init__(self):
        if self.random_seed is not None:
            random.seed(self.random_seed)


class BaseMutator:
    """Base class for mutation operators."""
    
    def __init__(self, name: str):
        self.name = name
    
    def can_mutate(self, node: ast.AST) -> bool:
        """Check if this mutator can mutate the given AST node."""
        raise NotImplementedError
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        """Generate mutations for the given node."""
        raise NotImplementedError


class ArithmeticMutator(BaseMutator):
    """Mutator for arithmetic operators."""
    
    def __init__(self):
        super().__init__("ArithmeticMutator")
        self.mutations = {
            ast.Add: [ast.Sub, ast.Mult, ast.Div],
            ast.Sub: [ast.Add, ast.Mult, ast.Div], 
            ast.Mult: [ast.Add, ast.Sub, ast.Div],
            ast.Div: [ast.Add, ast.Sub, ast.Mult],
            ast.Mod: [ast.Add, ast.Sub],
            ast.Pow: [ast.Mult, ast.Div]
        }
    
    def can_mutate(self, node: ast.AST) -> bool:
        return isinstance(node, ast.BinOp) and type(node.op) in self.mutations
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutations = []
        original_op = type(node.op)
        
        for new_op_class in self.mutations[original_op]:
            mutated_node = copy.deepcopy(node)
            mutated_node.op = new_op_class()
            mutations.append(mutated_node)
        
        return mutations


class ComparisonMutator(BaseMutator):
    """Mutator for comparison operators."""
    
    def __init__(self):
        super().__init__("ComparisonMutator")
        self.mutations = {
            ast.Eq: [ast.NotEq, ast.Lt, ast.Gt],
            ast.NotEq: [ast.Eq, ast.Lt, ast.Gt],
            ast.Lt: [ast.Le, ast.Gt, ast.GtE],
            ast.Le: [ast.Lt, ast.Gt, ast.GtE],
            ast.Gt: [ast.Ge, ast.Lt, ast.LtE],
            ast.GtE: [ast.Gt, ast.Lt, ast.LtE],
            ast.Is: [ast.IsNot],
            ast.IsNot: [ast.Is],
            ast.In: [ast.NotIn],
            ast.NotIn: [ast.In]
        }
    
    def can_mutate(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.Compare) and 
                len(node.ops) == 1 and 
                type(node.ops[0]) in self.mutations)
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutations = []
        original_op = type(node.ops[0])
        
        for new_op_class in self.mutations[original_op]:
            mutated_node = copy.deepcopy(node)
            mutated_node.ops = [new_op_class()]
            mutations.append(mutated_node)
        
        return mutations


class BooleanMutator(BaseMutator):
    """Mutator for boolean operators and values."""
    
    def __init__(self):
        super().__init__("BooleanMutator")
    
    def can_mutate(self, node: ast.AST) -> bool:
        return (isinstance(node, (ast.BoolOp, ast.UnaryOp, ast.Constant)) and
                (isinstance(node, ast.BoolOp) or
                 (isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not)) or
                 (isinstance(node, ast.Constant) and isinstance(node.value, bool))))
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        mutations = []
        
        if isinstance(node, ast.BoolOp):
            # Mutate And <-> Or
            mutated_node = copy.deepcopy(node)
            if isinstance(node.op, ast.And):
                mutated_node.op = ast.Or()
            else:
                mutated_node.op = ast.And()
            mutations.append(mutated_node)
        
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            # Remove 'not' operator
            mutations.append(node.operand)
        
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            # Flip boolean constants
            mutated_node = copy.deepcopy(node)
            mutated_node.value = not node.value
            mutations.append(mutated_node)
        
        return mutations


class ConditionalMutator(BaseMutator):
    """Mutator for conditional statements."""
    
    def __init__(self):
        super().__init__("ConditionalMutator")
    
    def can_mutate(self, node: ast.AST) -> bool:
        return isinstance(node, (ast.If, ast.While))
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        mutations = []
        
        if isinstance(node, (ast.If, ast.While)):
            # Negate the condition
            mutated_node = copy.deepcopy(node)
            mutated_node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
            mutations.append(mutated_node)
            
            # Replace condition with True
            mutated_node_true = copy.deepcopy(node)
            mutated_node_true.test = ast.Constant(value=True)
            mutations.append(mutated_node_true)
            
            # Replace condition with False
            mutated_node_false = copy.deepcopy(node)
            mutated_node_false.test = ast.Constant(value=False)
            mutations.append(mutated_node_false)
        
        return mutations


class ConstantMutator(BaseMutator):
    """Mutator for numeric constants."""
    
    def __init__(self):
        super().__init__("ConstantMutator")
    
    def can_mutate(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.Constant) and 
                isinstance(node.value, (int, float)) and
                not isinstance(node.value, bool))
    
    def mutate(self, node: ast.AST) -> List[ast.AST]:
        if not self.can_mutate(node):
            return []
        
        mutations = []
        original_value = node.value
        
        # Common mutations for numeric constants
        mutation_values = []
        
        if isinstance(original_value, int):
            mutation_values = [
                original_value + 1,
                original_value - 1,
                original_value * 2,
                0,
                1,
                -1
            ]
        elif isinstance(original_value, float):
            mutation_values = [
                original_value + 1.0,
                original_value - 1.0,
                original_value * 2.0,
                0.0,
                1.0,
                -1.0
            ]
        
        # Remove duplicates and the original value
        mutation_values = list(set(mutation_values))
        if original_value in mutation_values:
            mutation_values.remove(original_value)
        
        for value in mutation_values:
            mutated_node = copy.deepcopy(node)
            mutated_node.value = value
            mutations.append(mutated_node)
        
        return mutations


class MutationTestRunner:
    """Main class for running mutation tests."""
    
    def __init__(self, config: MutationTestConfig):
        self.config = config
        self.mutators = [
            ArithmeticMutator(),
            ComparisonMutator(),
            BooleanMutator(),
            ConditionalMutator(),
            ConstantMutator()
        ]
        self.results: List[MutationResult] = []
    
    def run_mutation_tests(self, target_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run mutation tests on specified files."""
        files_to_test = target_files or self.config.target_files
        
        if not files_to_test:
            raise ValueError("No target files specified for mutation testing")
        
        total_mutations = 0
        killed_mutations = 0
        
        for file_path in files_to_test:
            if not os.path.exists(file_path):
                print(f"Warning: File {file_path} does not exist, skipping")
                continue
            
            if any(pattern in file_path for pattern in self.config.skip_patterns):
                print(f"Skipping {file_path} (matches skip pattern)")
                continue
            
            print(f"Running mutation tests on {file_path}")
            file_results = self._test_file(file_path)
            
            total_mutations += len(file_results)
            killed_mutations += sum(1 for r in file_results if r.killed)
            
            self.results.extend(file_results)
        
        mutation_score = killed_mutations / total_mutations if total_mutations > 0 else 0
        
        return {
            'total_mutations': total_mutations,
            'killed_mutations': killed_mutations,
            'survived_mutations': total_mutations - killed_mutations,
            'mutation_score': mutation_score,
            'passed_threshold': mutation_score >= self.config.mutation_score_threshold,
            'results_by_file': self._group_results_by_file(),
            'results_by_mutator': self._group_results_by_mutator(),
            'detailed_results': [r.to_dict() for r in self.results]
        }
    
    def _test_file(self, file_path: str) -> List[MutationResult]:
        """Run mutation tests on a single file."""
        file_results = []
        
        try:
            with open(file_path, 'r') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            mutations = self._generate_mutations(tree, file_path)
            
            # Limit mutations per file
            if len(mutations) > self.config.max_mutations_per_file:
                mutations = random.sample(mutations, self.config.max_mutations_per_file)
            
            for i, (mutated_tree, mutator_name, line_number, original_code, mutated_code) in enumerate(mutations):
                mutation_id = f"{file_path}_{i}"
                
                print(f"  Testing mutation {i+1}/{len(mutations)}: {mutator_name}")
                
                result = self._test_single_mutation(
                    file_path, mutated_tree, mutation_id, mutator_name,
                    line_number, original_code, mutated_code
                )
                
                file_results.append(result)
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        return file_results
    
    def _generate_mutations(self, tree: ast.AST, file_path: str) -> List[Tuple]:
        """Generate all possible mutations for an AST."""
        mutations = []
        
        class MutationVisitor(ast.NodeVisitor):
            def visit(self, node):
                for mutator in self.mutators:
                    if mutator.can_mutate(node):
                        mutated_nodes = mutator.mutate(node)
                        for mutated_node in mutated_nodes:
                            # Create a copy of the tree with the mutation
                            mutated_tree = copy.deepcopy(tree)
                            
                            # Replace the original node with the mutated one
                            self._replace_node(mutated_tree, node, mutated_node)
                            
                            original_code = ast.unparse(node) if hasattr(ast, 'unparse') else repr(node)
                            mutated_code = ast.unparse(mutated_node) if hasattr(ast, 'unparse') else repr(mutated_node)
                            
                            mutations.append((
                                mutated_tree,
                                mutator.name,
                                getattr(node, 'lineno', 0),
                                original_code,
                                mutated_code
                            ))
                
                self.generic_visit(node)
            
            def _replace_node(self, tree, target_node, replacement_node):
                """Replace target_node with replacement_node in the tree."""
                for parent in ast.walk(tree):
                    for field, value in ast.iter_fields(parent):
                        if value == target_node:
                            setattr(parent, field, replacement_node)
                        elif isinstance(value, list) and target_node in value:
                            idx = value.index(target_node)
                            value[idx] = replacement_node
        
        visitor = MutationVisitor()
        visitor.mutators = self.mutators
        visitor.visit(tree)
        
        return mutations
    
    def _test_single_mutation(self, file_path: str, mutated_tree: ast.AST,
                            mutation_id: str, mutator_name: str,
                            line_number: int, original_code: str,
                            mutated_code: str) -> MutationResult:
        """Test a single mutation."""
        import time
        start_time = time.time()
        
        # Create temporary file with mutation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            if hasattr(ast, 'unparse'):
                temp_file.write(ast.unparse(mutated_tree))
            else:
                # Fallback for older Python versions
                temp_file.write("# Mutation testing not fully supported on this Python version\n")
                temp_file.write("pass\n")
            
            temp_file_path = temp_file.name
        
        try:
            # Replace original file temporarily
            original_backup = file_path + '.backup'
            os.rename(file_path, original_backup)
            os.rename(temp_file_path, file_path)
            
            # Run tests
            result = subprocess.run(
                self.config.test_command.split(),
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            # Mutation is killed if tests fail (non-zero exit code)
            killed = result.returncode != 0
            test_output = result.stdout + result.stderr
            
        except subprocess.TimeoutExpired:
            killed = False  # Timeout means mutation survived
            test_output = "Test execution timed out"
        
        except Exception as e:
            killed = False
            test_output = f"Error running tests: {str(e)}"
        
        finally:
            # Restore original file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(original_backup):
                    os.rename(original_backup, file_path)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as e:
                print(f"Error restoring files: {e}")
        
        execution_time = time.time() - start_time
        
        return MutationResult(
            mutation_id=mutation_id,
            mutator_name=mutator_name,
            file_path=file_path,
            line_number=line_number,
            original_code=original_code,
            mutated_code=mutated_code,
            killed=killed,
            test_output=test_output,
            execution_time=execution_time,
            timestamp=datetime.now()
        )
    
    def _group_results_by_file(self) -> Dict[str, Dict[str, Any]]:
        """Group results by file."""
        by_file = {}
        
        for result in self.results:
            if result.file_path not in by_file:
                by_file[result.file_path] = {
                    'total_mutations': 0,
                    'killed_mutations': 0,
                    'mutation_score': 0.0
                }
            
            by_file[result.file_path]['total_mutations'] += 1
            if result.killed:
                by_file[result.file_path]['killed_mutations'] += 1
        
        # Calculate mutation scores
        for file_path, stats in by_file.items():
            if stats['total_mutations'] > 0:
                stats['mutation_score'] = stats['killed_mutations'] / stats['total_mutations']
        
        return by_file
    
    def _group_results_by_mutator(self) -> Dict[str, Dict[str, Any]]:
        """Group results by mutator type."""
        by_mutator = {}
        
        for result in self.results:
            if result.mutator_name not in by_mutator:
                by_mutator[result.mutator_name] = {
                    'total_mutations': 0,
                    'killed_mutations': 0,
                    'mutation_score': 0.0
                }
            
            by_mutator[result.mutator_name]['total_mutations'] += 1
            if result.killed:
                by_mutator[result.mutator_name]['killed_mutations'] += 1
        
        # Calculate mutation scores
        for mutator_name, stats in by_mutator.items():
            if stats['total_mutations'] > 0:
                stats['mutation_score'] = stats['killed_mutations'] / stats['total_mutations']
        
        return by_mutator
    
    def export_results(self, filepath: str) -> None:
        """Export mutation test results to a file."""
        results_data = {
            'mutation_test_results': {
                'config': {
                    'target_files': self.config.target_files,
                    'test_command': self.config.test_command,
                    'timeout': self.config.timeout,
                    'mutation_score_threshold': self.config.mutation_score_threshold
                },
                'summary': {
                    'total_mutations': len(self.results),
                    'killed_mutations': sum(1 for r in self.results if r.killed),
                    'mutation_score': sum(1 for r in self.results if r.killed) / len(self.results) if self.results else 0
                },
                'results_by_file': self._group_results_by_file(),
                'results_by_mutator': self._group_results_by_mutator(),
                'detailed_results': [r.to_dict() for r in self.results]
            },
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)


# Utility functions
def run_mutation_tests(target_files: List[str], 
                      test_command: str = "pytest",
                      mutation_score_threshold: float = 0.8) -> Dict[str, Any]:
    """Convenience function to run mutation tests."""
    config = MutationTestConfig(
        target_files=target_files,
        test_command=test_command,
        mutation_score_threshold=mutation_score_threshold
    )
    
    runner = MutationTestRunner(config)
    return runner.run_mutation_tests()


def analyze_mutation_results(results_file: str) -> Dict[str, Any]:
    """Analyze mutation test results from a file."""
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    results = data['mutation_test_results']
    summary = results['summary']
    
    analysis = {
        'overall_quality': 'Good' if summary['mutation_score'] >= 0.8 else 'Needs Improvement',
        'weakest_files': [],
        'weakest_mutators': [],
        'recommendations': []
    }
    
    # Find weakest files
    by_file = results['results_by_file']
    for file_path, stats in by_file.items():
        if stats['mutation_score'] < 0.7:
            analysis['weakest_files'].append({
                'file': file_path,
                'score': stats['mutation_score']
            })
    
    # Find weakest mutators
    by_mutator = results['results_by_mutator']
    for mutator_name, stats in by_mutator.items():
        if stats['mutation_score'] < 0.7:
            analysis['weakest_mutators'].append({
                'mutator': mutator_name,
                'score': stats['mutation_score']
            })
    
    # Generate recommendations
    if summary['mutation_score'] < 0.6:
        analysis['recommendations'].append("Test suite needs significant improvement")
    elif summary['mutation_score'] < 0.8:
        analysis['recommendations'].append("Consider adding more edge case tests")
    
    if analysis['weakest_files']:
        analysis['recommendations'].append(f"Focus testing efforts on: {', '.join([f['file'] for f in analysis['weakest_files']])}")
    
    return analysis