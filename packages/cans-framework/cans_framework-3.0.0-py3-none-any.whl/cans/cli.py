"""
Command-line interface for CANS framework.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

from .utils.causal_assumptions import validate_causal_assumptions
from .utils.causal_evaluation import CausalEvaluator
from .config import CANSConfig


def validate_assumptions_cli():
    """CLI command for validating causal assumptions."""
    parser = argparse.ArgumentParser(
        description="Validate causal assumptions for a dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cans-validate --data data.csv --treatment treatment --outcome outcome
  cans-validate --data data.csv --treatment T --outcome Y --features X1,X2,X3
        """
    )
    
    parser.add_argument(
        "--data", 
        required=True,
        help="Path to CSV data file"
    )
    parser.add_argument(
        "--treatment", 
        required=True,
        help="Name of treatment column"
    )
    parser.add_argument(
        "--outcome", 
        required=True,
        help="Name of outcome column"
    )
    parser.add_argument(
        "--features",
        help="Comma-separated list of feature columns (if not specified, uses all numeric columns)"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file for results (default: print to stdout)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Load data
        data = pd.read_csv(args.data)
        
        if args.verbose:
            print(f"Loaded data with shape: {data.shape}")
        
        # Extract variables
        T = data[args.treatment].values
        Y = data[args.outcome].values
        
        if args.features:
            feature_cols = [col.strip() for col in args.features.split(",")]
            X = data[feature_cols].values
        else:
            # Use all numeric columns except treatment and outcome
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [col for col in numeric_cols if col not in [args.treatment, args.outcome]]
            X = data[feature_cols].values
        
        if args.verbose:
            print(f"Using features: {feature_cols}")
            print(f"Treatment rate: {T.mean():.3f}")
            print(f"Running assumption tests...")
        
        # Run assumption tests
        results = validate_causal_assumptions(X, T, Y)
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=2, default=str))
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def evaluate_model_cli():
    """CLI command for evaluating model performance."""
    parser = argparse.ArgumentParser(
        description="Evaluate CANS model performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--predictions",
        required=True,
        help="Path to predictions file (CSV with mu0, mu1, treatments, outcomes columns)"
    )
    parser.add_argument(
        "--output",
        help="Output file for evaluation report"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    try:
        # Load predictions
        data = pd.read_csv(args.predictions)
        
        required_cols = ["mu0", "mu1", "treatments", "outcomes"]
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Extract data
        mu0_pred = data["mu0"].values
        mu1_pred = data["mu1"].values
        treatments = data["treatments"].values
        outcomes = data["outcomes"].values
        
        # Evaluate
        evaluator = CausalEvaluator()
        metrics = evaluator.evaluate_treatment_effects(
            outcomes, mu0_pred, mu1_pred, treatments
        )
        
        # Generate report
        if args.format == "json":
            result = {
                "ate": metrics.ate,
                "ate_std": metrics.ate_std,
                "ate_ci_lower": metrics.ate_ci_lower,
                "ate_ci_upper": metrics.ate_ci_upper,
                "factual_mse": metrics.factual_mse,
                "factual_mae": metrics.factual_mae,
                "pehe": metrics.pehe if metrics.pehe > 0 else None,
                "cate_r2": metrics.cate_r2 if metrics.cate_r2 != 0 else None,
            }
            output = json.dumps(result, indent=2)
        else:
            output = evaluator.generate_evaluation_report(metrics, "CLI Evaluation")
        
        # Save or print results
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Evaluation saved to {args.output}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def analyze_causal_cli():
    """CLI command for complete causal analysis."""
    parser = argparse.ArgumentParser(
        description="Run complete causal analysis workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--config",
        help="Path to CANS configuration file"
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Path to data file"
    )
    parser.add_argument(
        "--output-dir",
        default="cans_analysis",
        help="Output directory for analysis results"
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        if args.config:
            config = CANSConfig.load(args.config)
        else:
            config = CANSConfig()
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        print(f"Starting CANS analysis...")
        print(f"Data: {args.data}")
        print(f"Output directory: {output_dir}")
        print(f"This feature is coming in the next version!")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # This allows the CLI to be called directly
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "validate":
            validate_assumptions_cli()
        elif sys.argv[1] == "evaluate":
            evaluate_model_cli()
        elif sys.argv[1] == "analyze":
            analyze_causal_cli()
        else:
            print("Unknown command. Use: validate, evaluate, or analyze")
            sys.exit(1)
    else:
        print("CANS CLI. Use: cans-validate, cans-evaluate, or cans-analyze")