#!/usr/bin/env python3
"""
CausalLLM Command Line Interface

Provides command-line access to CausalLLM functionality for causal inference,
discovery, and analysis.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd

from . import CausalLLM, __version__
from .core.utils.logging import setup_package_logging


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog='causallm',
        description='CausalLLM - Open Source Causal Inference powered by LLMs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  causallm discover --data data.csv --variables "age,income,health" --output results.json
  causallm effect --data data.csv --treatment exercise --outcome health --method iv
  causallm counterfactual --data data.csv --intervention "exercise=1" --output scenarios.json
  causallm info --enterprise
  causallm web --port 8080
        """
    )
    
    parser.add_argument('--version', action='version', version=f'CausalLLM {__version__}')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--config', '-c', type=str, help='Configuration file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Discovery command
    discovery_parser = subparsers.add_parser('discover', help='Discover causal relationships')
    discovery_parser.add_argument('--data', '-d', required=True, help='Path to data file (CSV/JSON)')
    discovery_parser.add_argument('--variables', '-var', required=True, help='Comma-separated variable names')
    discovery_parser.add_argument('--domain', help='Domain context (healthcare, marketing, etc.)')
    discovery_parser.add_argument('--method', default='hybrid', choices=['llm', 'statistical', 'hybrid'])
    discovery_parser.add_argument('--output', '-o', help='Output file path')
    discovery_parser.add_argument('--llm-provider', default='openai', choices=['openai', 'anthropic'])
    discovery_parser.add_argument('--llm-model', default='gpt-4', help='LLM model name')
    
    # Effect estimation command
    effect_parser = subparsers.add_parser('effect', help='Estimate causal effects')
    effect_parser.add_argument('--data', '-d', required=True, help='Path to data file (CSV/JSON)')
    effect_parser.add_argument('--treatment', '-t', required=True, help='Treatment variable')
    effect_parser.add_argument('--outcome', '-y', required=True, help='Outcome variable')
    effect_parser.add_argument('--confounders', help='Comma-separated confounder variables')
    effect_parser.add_argument('--method', default='backdoor', choices=['backdoor', 'iv', 'regression_discontinuity'])
    effect_parser.add_argument('--output', '-o', help='Output file path')
    
    # Counterfactual command
    counterfactual_parser = subparsers.add_parser('counterfactual', help='Generate counterfactual scenarios')
    counterfactual_parser.add_argument('--data', '-d', required=True, help='Path to data file (CSV/JSON)')
    counterfactual_parser.add_argument('--intervention', '-i', required=True, help='Intervention specification (e.g., "variable=value")')
    counterfactual_parser.add_argument('--samples', '-n', type=int, default=100, help='Number of counterfactual samples')
    counterfactual_parser.add_argument('--output', '-o', help='Output file path')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Display package information')
    info_parser.add_argument('--enterprise', action='store_true', help='Show enterprise features')
    info_parser.add_argument('--domains', action='store_true', help='List available domains')
    info_parser.add_argument('--examples', action='store_true', help='Show usage examples')
    
    # Web interface command
    web_parser = subparsers.add_parser('web', help='Launch web interface')
    web_parser.add_argument('--port', '-p', type=int, default=8080, help='Port number (default: 8080)')
    web_parser.add_argument('--host', default='localhost', help='Host address (default: localhost)')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    return parser


def load_data(file_path: str) -> pd.DataFrame:
    """Load data from CSV or JSON file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    if path.suffix.lower() == '.csv':
        return pd.read_csv(file_path)
    elif path.suffix.lower() == '.json':
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


def save_results(results: Dict[str, Any], output_path: Optional[str] = None) -> None:
    """Save results to file or print to stdout."""
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to: {output_path}")
    else:
        print(json.dumps(results, indent=2, default=str))


async def run_discovery(args) -> Dict[str, Any]:
    """Run causal discovery."""
    data = load_data(args.data)
    variables = [v.strip() for v in args.variables.split(',')]
    
    causal_llm = CausalLLM(method=args.method)
    
    domain_context = args.domain or ""
    results = await causal_llm.discover_causal_relationships(
        data=data,
        variables=variables,
        domain_context=domain_context
    )
    
    return {
        'command': 'discover',
        'data_shape': data.shape,
        'variables': variables,
        'domain': domain_context,
        'method': args.method,
        'results': results
    }


async def run_effect_estimation(args) -> Dict[str, Any]:
    """Run causal effect estimation."""
    data = load_data(args.data)
    confounders = [c.strip() for c in args.confounders.split(',')] if args.confounders else []
    
    causal_llm = CausalLLM()
    
    results = await causal_llm.estimate_causal_effect(
        data=data,
        treatment=args.treatment,
        outcome=args.outcome,
        confounders=confounders,
        method=args.method
    )
    
    return {
        'command': 'effect',
        'data_shape': data.shape,
        'treatment': args.treatment,
        'outcome': args.outcome,
        'confounders': confounders,
        'method': args.method,
        'results': results
    }


async def run_counterfactual(args) -> Dict[str, Any]:
    """Run counterfactual analysis."""
    data = load_data(args.data)
    
    # Parse intervention string (e.g., "variable=value")
    intervention_parts = args.intervention.split('=')
    if len(intervention_parts) != 2:
        raise ValueError("Intervention must be in format 'variable=value'")
    
    var_name, var_value = intervention_parts[0].strip(), intervention_parts[1].strip()
    
    # Try to convert value to appropriate type
    try:
        var_value = float(var_value)
        if var_value.is_integer():
            var_value = int(var_value)
    except ValueError:
        pass  # Keep as string
    
    intervention = {var_name: var_value}
    
    causal_llm = CausalLLM()
    
    results = await causal_llm.generate_counterfactuals(
        data=data,
        intervention=intervention,
        num_samples=args.samples
    )
    
    return {
        'command': 'counterfactual',
        'data_shape': data.shape,
        'intervention': intervention,
        'samples': args.samples,
        'results': results
    }


def show_info(args) -> None:
    """Display package information."""
    print(f"CausalLLM v{__version__}")
    print("Open Source Causal Inference powered by LLMs")
    print()
    
    if args.enterprise:
        causal_llm = CausalLLM()
        enterprise_info = causal_llm.get_enterprise_info()
        print("Enterprise Features:")
        for benefit in enterprise_info['benefits']:
            print(f"  • {benefit}")
        print(f"\nInfo: {enterprise_info['info']}")
        print()
    
    if args.domains:
        print("Available Domains:")
        try:
            from . import domains
            from .domains import DOMAINS_AVAILABLE
            if DOMAINS_AVAILABLE:
                print("  • Healthcare")
                print("  • Insurance") 
                print("  • Marketing")
                print("  • Education")
                print("  • Experimentation")
            else:
                print("  Domain packages not installed. Install with: pip install causallm[plugins]")
        except ImportError:
            print("  Domain packages not available")
        print()
    
    if args.examples:
        print("Usage Examples:")
        print("  # Discover causal relationships")
        print("  causallm discover --data healthcare_data.csv --variables 'age,treatment,outcome' --domain healthcare")
        print()
        print("  # Estimate treatment effect")
        print("  causallm effect --data experiment.csv --treatment drug --outcome recovery --confounders 'age,gender'")
        print()
        print("  # Generate counterfactuals")
        print("  causallm counterfactual --data patient_data.csv --intervention 'treatment=1' --samples 200")
        print()


def launch_web_interface(args) -> None:
    """Launch the web interface."""
    try:
        from .web import create_web_app
        create_web_app(host=args.host, port=args.port, debug=args.debug)
    except ImportError:
        print("Web interface not available. Install UI dependencies with:")
        print("pip install causallm[ui]")
        sys.exit(1)


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.verbose:
        setup_package_logging(level="DEBUG")
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'discover':
            results = await run_discovery(args)
            save_results(results, args.output)
        
        elif args.command == 'effect':
            results = await run_effect_estimation(args)
            save_results(results, args.output)
        
        elif args.command == 'counterfactual':
            results = await run_counterfactual(args)
            save_results(results, args.output)
        
        elif args.command == 'info':
            show_info(args)
        
        elif args.command == 'web':
            launch_web_interface(args)
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def cli_entry_point():
    """Entry point for the CLI."""
    asyncio.run(main())


if __name__ == '__main__':
    cli_entry_point()