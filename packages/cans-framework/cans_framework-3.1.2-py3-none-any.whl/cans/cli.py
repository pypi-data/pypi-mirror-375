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
        epilog="""
Examples:
  cans-analyze --data data.csv --treatment T --outcome Y --output-dir results/
  cans-analyze --data data.csv --treatment treatment --outcome outcome --config config.json
        """
    )
    
    parser.add_argument(
        "--data",
        required=True,
        help="Path to CSV data file"
    )
    parser.add_argument(
        "--treatment",
        help="Name of treatment column (required for analysis)"
    )
    parser.add_argument(
        "--outcome", 
        help="Name of outcome column (required for analysis)"
    )
    parser.add_argument(
        "--text-column",
        help="Name of text column for NLP features (optional)"
    )
    parser.add_argument(
        "--features",
        help="Comma-separated list of feature columns (optional)"
    )
    parser.add_argument(
        "--config",
        help="Path to CANS configuration file (optional)"
    )
    parser.add_argument(
        "--output-dir",
        default="cans_analysis",
        help="Output directory for analysis results (default: cans_analysis)"
    )
    parser.add_argument(
        "--skip-assumptions",
        action="store_true", 
        help="Skip causal assumption testing"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick analysis with reduced epochs"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Validate required arguments for full analysis
        if not args.skip_assumptions and (not args.treatment or not args.outcome):
            print("Error: --treatment and --outcome are required for causal analysis", file=sys.stderr)
            print("Use --skip-assumptions if you only want to process data", file=sys.stderr)
            sys.exit(1)
        
        # Load configuration
        if args.config:
            config = CANSConfig.load(args.config)
            if args.verbose:
                print(f"Loaded configuration from {args.config}")
        else:
            config = CANSConfig()
            if args.quick:
                config.training.epochs = 10  # Reduce for quick analysis
                config.training.batch_size = 32
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        if args.verbose:
            print(f"Starting CANS causal analysis...")
            print(f"Data: {args.data}")
            print(f"Output directory: {output_dir}")
            
        # Load and validate data
        if not Path(args.data).exists():
            raise FileNotFoundError(f"Data file not found: {args.data}")
            
        data = pd.read_csv(args.data)
        if args.verbose:
            print(f"Loaded data with shape: {data.shape}")
            
        # Basic data validation
        if args.treatment and args.treatment not in data.columns:
            raise ValueError(f"Treatment column '{args.treatment}' not found in data")
        if args.outcome and args.outcome not in data.columns:
            raise ValueError(f"Outcome column '{args.outcome}' not found in data")
            
        # Step 1: Validate assumptions (if not skipped)
        if not args.skip_assumptions and args.treatment and args.outcome:
            print("Step 1: Validating causal assumptions...")
            
            T = data[args.treatment].values
            Y = data[args.outcome].values
            
            if args.features:
                feature_cols = [col.strip() for col in args.features.split(",")]
                X = data[feature_cols].values
            else:
                numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
                feature_cols = [col for col in numeric_cols if col not in [args.treatment, args.outcome]]
                X = data[feature_cols].values
                
            if args.verbose:
                print(f"Using {len(feature_cols)} features: {feature_cols[:3]}...")
                print(f"Treatment rate: {T.mean():.3f}")
                
            assumptions_results = validate_causal_assumptions(X, T, Y)
            
            # Save assumptions results
            assumptions_file = output_dir / "assumptions_validation.json"
            with open(assumptions_file, 'w') as f:
                json.dump(assumptions_results, f, indent=2, default=str)
            print(f"✓ Assumptions validation saved to {assumptions_file}")
            
            if args.verbose:
                overall_valid = assumptions_results.get('causal_identification_valid', False)
                print(f"Causal identification valid: {overall_valid}")
        
        # Step 2: Create summary report
        print("Step 2: Creating analysis summary...")
        summary = {
            "data_file": str(args.data),
            "data_shape": list(data.shape),
            "treatment_column": args.treatment,
            "outcome_column": args.outcome,
            "text_column": args.text_column,
            "analysis_timestamp": pd.Timestamp.now().isoformat(),
            "configuration": config.to_dict() if hasattr(config, 'to_dict') else str(config)
        }
        
        if args.treatment and args.outcome:
            summary["treatment_rate"] = float(data[args.treatment].mean())
            summary["outcome_mean"] = float(data[args.outcome].mean())
            summary["outcome_std"] = float(data[args.outcome].std())
        
        summary_file = output_dir / "analysis_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Analysis summary saved to {summary_file}")
        
        # Step 3: Data preprocessing report
        print("Step 3: Creating data preprocessing report...")
        data_report = {
            "columns": list(data.columns),
            "numeric_columns": list(data.select_dtypes(include=[np.number]).columns),
            "categorical_columns": list(data.select_dtypes(include=['object']).columns),
            "missing_values": data.isnull().sum().to_dict(),
            "data_types": data.dtypes.astype(str).to_dict()
        }
        
        data_report_file = output_dir / "data_preprocessing_report.json"
        with open(data_report_file, 'w') as f:
            json.dump(data_report, f, indent=2)
        print(f"✓ Data report saved to {data_report_file}")
        
        print(f"\n🎉 CANS analysis completed successfully!")
        print(f"📁 Results available in: {output_dir}")
        print(f"📊 Files created:")
        for file in output_dir.glob("*.json"):
            print(f"   • {file.name}")
            
        # Provide next steps guidance
        print(f"\n📋 Next Steps:")
        print(f"1. Review assumptions validation in assumptions_validation.json")
        print(f"2. Check data quality in data_preprocessing_report.json") 
        print(f"3. Use Python API for model training and evaluation")
        print(f"4. Run 'cans-evaluate' on model predictions for detailed metrics")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main_cli():
    """Main CLI entry point with help and version information."""
    parser = argparse.ArgumentParser(
        description="CANS: Causal Adaptive Neural System - CLI Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Commands:
  cans-validate    Validate causal assumptions for a dataset
  cans-evaluate    Evaluate CANS model performance  
  cans-analyze     Run complete causal analysis workflow

Examples:
  cans-validate --data data.csv --treatment T --outcome Y
  cans-evaluate --predictions model_output.csv
  cans-analyze --data data.csv --treatment intervention --outcome result

For more help on a specific command:
  cans-validate --help
  cans-evaluate --help  
  cans-analyze --help

Documentation: https://github.com/rdmurugan/cans-framework#readme
        """
    )
    
    parser.add_argument(
        "--version", 
        action="version",
        version="CANS Framework v3.0.0"
    )
    
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        parser.parse_args()


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
        main_cli()