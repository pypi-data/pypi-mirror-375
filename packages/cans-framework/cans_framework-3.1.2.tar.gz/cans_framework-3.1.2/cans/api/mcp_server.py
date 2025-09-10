"""
CANS Model Context Protocol (MCP) Server

Provides MCP server functionality for seamless integration with LLMs and AI applications.
Enables LLMs to directly interact with CANS for causal analysis tasks.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime

# MCP server imports
try:
    from mcp.server import Server
    from mcp.types import (
        Tool, 
        TextResourceContents,
        Resource,
        CallToolResult,
        ListToolsResult,
        ListResourcesResult,
        ReadResourceResult
    )
    MCP_AVAILABLE = True
except ImportError:
    print("MCP not available. Install with: pip install model-context-protocol")
    MCP_AVAILABLE = False

from cans import (
    validate_causal_assumptions,
    CANSConfig,
    CausalEvaluator,
    load_csv_dataset
)

logger = logging.getLogger(__name__)


class CANSMCPServer:
    """MCP Server for CANS framework."""
    
    def __init__(self):
        if not MCP_AVAILABLE:
            raise ImportError("MCP dependencies not available")
            
        self.server = Server("cans")
        self.analysis_history: List[Dict] = []
        self.models: Dict[str, Any] = {}
        
        # Register tools
        self._register_tools()
        self._register_resources()
    
    def _register_tools(self):
        """Register MCP tools for causal analysis."""
        
        @self.server.call_tool()
        async def validate_causal_assumptions_tool(
            data_path: str,
            treatment_column: str,
            outcome_column: str,
            feature_columns: Optional[str] = None
        ) -> CallToolResult:
            """Validate causal assumptions for a dataset.
            
            Args:
                data_path: Path to CSV file containing the data
                treatment_column: Name of the binary treatment column
                outcome_column: Name of the outcome column
                feature_columns: Comma-separated list of feature columns (optional)
            """
            try:
                # Load data
                df = pd.read_csv(data_path)
                
                # Extract variables
                T = df[treatment_column].values
                Y = df[outcome_column].values
                
                if feature_columns:
                    feature_cols = [col.strip() for col in feature_columns.split(",")]
                    X = df[feature_cols].values
                else:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    feature_cols = [col for col in numeric_cols 
                                  if col not in [treatment_column, outcome_column]]
                    X = df[feature_cols].values
                
                # Run validation
                results = validate_causal_assumptions(X, T, Y)
                
                # Store in history
                analysis_record = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "assumption_validation",
                    "data_path": data_path,
                    "treatment_column": treatment_column,
                    "outcome_column": outcome_column,
                    "results": results,
                    "sample_size": len(df),
                    "treatment_rate": float(T.mean())
                }
                self.analysis_history.append(analysis_record)
                
                # Format response for LLM
                summary = f"""
Causal Assumption Validation Results:
=====================================

Dataset: {data_path}
Sample Size: {len(df):,}
Treatment Rate: {T.mean():.1%}
Features Used: {len(feature_cols)}

VALIDATION SUMMARY:
✅ Overall Causal Identification: {'VALID' if results.get('causal_identification_valid') else 'INVALID'}

DETAILED TESTS:
📊 Unconfoundedness Test:
   - Valid: {'✅' if results.get('unconfoundedness_test', {}).get('valid') else '❌'}
   - P-value: {results.get('unconfoundedness_test', {}).get('p_value', 'N/A')}
   - Method: {results.get('unconfoundedness_test', {}).get('method', 'N/A')}

🎯 Positivity Test:
   - Valid: {'✅' if results.get('positivity_test', {}).get('valid') else '❌'}
   - Overlap Score: {results.get('positivity_test', {}).get('overlap_score', 'N/A')}
   - Min Propensity: {results.get('positivity_test', {}).get('min_propensity', 'N/A')}

🔗 SUTVA Test:
   - Valid: {'✅' if results.get('sutva_test', {}).get('valid') else '❌'}
   - Interference Score: {results.get('sutva_test', {}).get('interference_score', 'N/A')}

RECOMMENDATIONS:
"""
                if not results.get('causal_identification_valid'):
                    summary += "⚠️  Causal identification conditions not met. Consider:\n"
                    summary += "   • Including additional confounding variables\n"
                    summary += "   • Checking data quality and collection process\n"
                    summary += "   • Using alternative identification strategies\n"
                else:
                    summary += "✅ Dataset appears suitable for causal inference!\n"
                
                return CallToolResult(content=[{"type": "text", "text": summary}])
                
            except Exception as e:
                error_msg = f"Error validating assumptions: {str(e)}"
                logger.error(error_msg)
                return CallToolResult(
                    content=[{"type": "text", "text": error_msg}],
                    isError=True
                )
        
        @self.server.call_tool()
        async def quick_causal_analysis(
            data_path: str,
            treatment_column: str,
            outcome_column: str,
            text_column: Optional[str] = None,
            feature_columns: Optional[str] = None
        ) -> CallToolResult:
            """Perform quick causal analysis including assumption validation and basic modeling.
            
            Args:
                data_path: Path to CSV file containing the data
                treatment_column: Name of the binary treatment column  
                outcome_column: Name of the outcome column
                text_column: Name of text column for NLP features (optional)
                feature_columns: Comma-separated list of feature columns (optional)
            """
            try:
                # Load and validate data
                df = pd.read_csv(data_path)
                
                # Basic data validation
                if treatment_column not in df.columns:
                    raise ValueError(f"Treatment column '{treatment_column}' not found")
                if outcome_column not in df.columns:
                    raise ValueError(f"Outcome column '{outcome_column}' not found")
                
                # Extract variables for assumption testing
                T = df[treatment_column].values
                Y = df[outcome_column].values
                
                if feature_columns:
                    feature_cols = [col.strip() for col in feature_columns.split(",")]
                    X = df[feature_cols].values
                else:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    feature_cols = [col for col in numeric_cols 
                                  if col not in [treatment_column, outcome_column]]
                    X = df[feature_cols].values
                
                # Step 1: Validate assumptions
                assumptions = validate_causal_assumptions(X, T, Y)
                
                # Step 2: Basic descriptive analysis
                treatment_group = df[df[treatment_column] == 1][outcome_column]
                control_group = df[df[treatment_column] == 0][outcome_column]
                
                naive_ate = treatment_group.mean() - control_group.mean()
                
                # Store comprehensive analysis
                analysis_record = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "quick_analysis",
                    "data_path": data_path,
                    "results": {
                        "assumptions": assumptions,
                        "naive_ate": naive_ate,
                        "sample_size": len(df),
                        "treatment_rate": float(T.mean()),
                        "outcome_stats": {
                            "treatment_mean": float(treatment_group.mean()),
                            "control_mean": float(control_group.mean()),
                            "treatment_std": float(treatment_group.std()),
                            "control_std": float(control_group.std())
                        }
                    }
                }
                self.analysis_history.append(analysis_record)
                
                # Generate comprehensive report
                report = f"""
CANS Quick Causal Analysis Report
=================================

📊 DATASET OVERVIEW:
   • File: {data_path}
   • Sample Size: {len(df):,}
   • Treatment Rate: {T.mean():.1%} ({int(T.sum())} treated, {int(len(T)-T.sum())} control)
   • Features: {len(feature_cols)}
   • Text Column: {'Yes' if text_column else 'No'}

🔍 CAUSAL ASSUMPTIONS:
   Overall Valid: {'✅ YES' if assumptions.get('causal_identification_valid') else '❌ NO'}
   
   Unconfoundedness: {'✅' if assumptions.get('unconfoundedness_test', {}).get('valid') else '❌'}
   Positivity: {'✅' if assumptions.get('positivity_test', {}).get('valid') else '❌'}
   SUTVA: {'✅' if assumptions.get('sutva_test', {}).get('valid') else '❌'}

📈 PRELIMINARY RESULTS:
   Treatment Group Mean: {treatment_group.mean():.3f} (±{treatment_group.std():.3f})
   Control Group Mean: {control_group.mean():.3f} (±{control_group.std():.3f})
   
   Naive Treatment Effect: {naive_ate:.3f}
   {'✅ Positive effect detected' if naive_ate > 0 else '⚠️  Negative or no effect'}

⚡ NEXT STEPS:
"""
                if assumptions.get('causal_identification_valid'):
                    report += """   1. ✅ Proceed with full CANS modeling
   2. 🏗️  Train GNN+Transformer model for robust estimates  
   3. 📊 Generate individual treatment effect predictions
   4. 🎯 Validate with holdout test set
   
   💡 Use: cans-analyze --data {data_path} --treatment {treatment_column} --outcome {outcome_column}"""
                else:
                    report += """   1. ⚠️  Address assumption violations first
   2. 🔍 Include additional confounding variables
   3. 📝 Consider alternative identification strategies
   4. 🧪 Perform sensitivity analysis
   
   💡 Review data collection and variable selection"""
                
                return CallToolResult(content=[{"type": "text", "text": report}])
                
            except Exception as e:
                error_msg = f"Error in quick analysis: {str(e)}"
                logger.error(error_msg)
                return CallToolResult(
                    content=[{"type": "text", "text": error_msg}],
                    isError=True
                )
        
        @self.server.call_tool()
        async def evaluate_predictions(
            predictions_path: str
        ) -> CallToolResult:
            """Evaluate causal model predictions.
            
            Args:
                predictions_path: Path to CSV with columns: mu0, mu1, treatments, outcomes
            """
            try:
                # Load predictions
                pred_df = pd.read_csv(predictions_path)
                
                required_cols = ['mu0', 'mu1', 'treatments', 'outcomes']
                missing_cols = [col for col in required_cols if col not in pred_df.columns]
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}")
                
                # Extract data
                mu0_pred = pred_df['mu0'].values
                mu1_pred = pred_df['mu1'].values
                treatments = pred_df['treatments'].values
                outcomes = pred_df['outcomes'].values
                
                # Evaluate using CANS evaluator
                evaluator = CausalEvaluator()
                metrics = evaluator.evaluate_treatment_effects(
                    outcomes, mu0_pred, mu1_pred, treatments
                )
                
                # Store evaluation
                eval_record = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "evaluation",
                    "predictions_path": predictions_path,
                    "metrics": {
                        "ate": metrics.ate,
                        "ate_std": metrics.ate_std,
                        "ate_ci": [metrics.ate_ci_lower, metrics.ate_ci_upper],
                        "factual_mse": metrics.factual_mse,
                        "pehe": metrics.pehe,
                        "cate_r2": metrics.cate_r2
                    }
                }
                self.analysis_history.append(eval_record)
                
                # Generate evaluation report
                report = f"""
CANS Model Evaluation Report
============================

📊 DATASET:
   • Predictions File: {predictions_path}
   • Sample Size: {len(pred_df):,}
   • Treatment Rate: {treatments.mean():.1%}

🎯 CAUSAL EFFECT ESTIMATES:
   Average Treatment Effect (ATE): {metrics.ate:.3f} ± {metrics.ate_std:.3f}
   95% Confidence Interval: [{metrics.ate_ci_lower:.3f}, {metrics.ate_ci_upper:.3f}]
   
   Effect Significance: {'✅ Significant' if abs(metrics.ate) > 2*metrics.ate_std else '⚠️  Not significant'}

📈 MODEL PERFORMANCE:
   Factual MSE: {metrics.factual_mse:.4f}
   {'✅ Good prediction accuracy' if metrics.factual_mse < 0.1 else '⚠️  High prediction error'}
   
   PEHE (Heterogeneous Effects): {metrics.pehe:.4f}
   {'✅ Good CATE estimation' if metrics.pehe < 1.0 else '⚠️  Poor individual effect estimation'}
   
   CATE R²: {metrics.cate_r2:.3f}
   {'✅ Good effect prediction' if metrics.cate_r2 > 0.5 else '⚠️  Weak effect prediction'}

💡 INTERPRETATION:
   • The estimated treatment effect is {metrics.ate:.3f} units
   • {'Positive' if metrics.ate > 0 else 'Negative'} effect on the outcome
   • Model prediction quality: {'Excellent' if metrics.factual_mse < 0.05 else 'Good' if metrics.factual_mse < 0.2 else 'Needs improvement'}
   • Individual effect estimation: {'Strong' if metrics.cate_r2 > 0.7 else 'Moderate' if metrics.cate_r2 > 0.3 else 'Weak'}

🎯 RECOMMENDATIONS:
"""
                if metrics.factual_mse > 0.2:
                    report += "   • Consider model hyperparameter tuning\n"
                if metrics.pehe > 1.5:
                    report += "   • Include more features for better individual effects\n"
                if abs(metrics.ate) < metrics.ate_std:
                    report += "   • Effect may not be statistically significant\n"
                if metrics.cate_r2 < 0.3:
                    report += "   • Limited individual effect predictability\n"
                
                report += f"\n✨ Overall Assessment: {'Excellent' if metrics.factual_mse < 0.1 and metrics.cate_r2 > 0.6 else 'Good' if metrics.factual_mse < 0.3 and metrics.cate_r2 > 0.3 else 'Needs Improvement'}"
                
                return CallToolResult(content=[{"type": "text", "text": report}])
                
            except Exception as e:
                error_msg = f"Error evaluating predictions: {str(e)}"
                logger.error(error_msg)
                return CallToolResult(
                    content=[{"type": "text", "text": error_msg}],
                    isError=True
                )
        
        @self.server.call_tool()
        async def get_analysis_history() -> CallToolResult:
            """Get history of all causal analyses performed."""
            try:
                if not self.analysis_history:
                    return CallToolResult(content=[{
                        "type": "text", 
                        "text": "No analysis history available."
                    }])
                
                history_report = "CANS Analysis History\n" + "="*20 + "\n\n"
                
                for i, record in enumerate(reversed(self.analysis_history[-10:]), 1):
                    history_report += f"{i}. {record['type'].title()} - {record['timestamp']}\n"
                    if 'data_path' in record:
                        history_report += f"   📁 Data: {record['data_path']}\n"
                    
                    if record['type'] == 'assumption_validation':
                        valid = record['results'].get('causal_identification_valid', False)
                        history_report += f"   🎯 Valid: {'✅' if valid else '❌'}\n"
                        history_report += f"   📊 Sample: {record['sample_size']:,} | Treatment Rate: {record['treatment_rate']:.1%}\n"
                    
                    elif record['type'] == 'evaluation':
                        metrics = record['metrics']
                        history_report += f"   🎯 ATE: {metrics['ate']:.3f} ± {metrics['ate_std']:.3f}\n"
                        history_report += f"   📈 MSE: {metrics['factual_mse']:.4f} | CATE R²: {metrics['cate_r2']:.3f}\n"
                    
                    history_report += "\n"
                
                return CallToolResult(content=[{"type": "text", "text": history_report}])
                
            except Exception as e:
                error_msg = f"Error getting history: {str(e)}"
                logger.error(error_msg)
                return CallToolResult(
                    content=[{"type": "text", "text": error_msg}],
                    isError=True
                )
    
    def _register_resources(self):
        """Register MCP resources."""
        
        @self.server.list_resources()
        async def list_resources() -> ListResourcesResult:
            """List available CANS resources."""
            resources = [
                Resource(
                    uri="cans://analysis-history",
                    name="CANS Analysis History",
                    description="History of all causal analyses performed",
                    mimeType="application/json"
                ),
                Resource(
                    uri="cans://best-practices",
                    name="CANS Best Practices Guide", 
                    description="Guidelines for effective causal inference with CANS",
                    mimeType="text/markdown"
                )
            ]
            return ListResourcesResult(resources=resources)
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            """Read a CANS resource."""
            if uri == "cans://analysis-history":
                history_data = {
                    "total_analyses": len(self.analysis_history),
                    "recent_analyses": self.analysis_history[-5:] if self.analysis_history else [],
                    "summary": {
                        "validations": sum(1 for r in self.analysis_history if r['type'] == 'assumption_validation'),
                        "evaluations": sum(1 for r in self.analysis_history if r['type'] == 'evaluation'),
                        "quick_analyses": sum(1 for r in self.analysis_history if r['type'] == 'quick_analysis')
                    }
                }
                return ReadResourceResult(
                    contents=[TextResourceContents(
                        uri=uri,
                        mimeType="application/json",
                        text=json.dumps(history_data, indent=2, default=str)
                    )]
                )
            
            elif uri == "cans://best-practices":
                best_practices = """
# CANS Best Practices Guide

## 1. Data Preparation
- ✅ Ensure binary treatment (0/1) encoding
- ✅ Include all potential confounders as features
- ✅ Handle missing values appropriately
- ✅ Validate sufficient sample size (>1000 recommended)

## 2. Assumption Testing
- ✅ Always validate assumptions before modeling
- ✅ Check positivity (treatment overlap)
- ✅ Test for unmeasured confounding
- ✅ Verify SUTVA (no interference)

## 3. Model Configuration
- ✅ Start with default settings
- ✅ Use "cfr" loss for causal inference
- ✅ Include text features when available
- ✅ Validate on held-out data

## 4. Evaluation
- ✅ Focus on ATE for policy decisions
- ✅ Examine CATE for personalization
- ✅ Check uncertainty estimates
- ✅ Validate with domain experts

## 5. Interpretation
- ✅ Consider clinical/practical significance
- ✅ Account for confidence intervals
- ✅ Validate assumptions hold
- ✅ Consider external validity
                """
                return ReadResourceResult(
                    contents=[TextResourceContents(
                        uri=uri,
                        mimeType="text/markdown", 
                        text=best_practices.strip()
                    )]
                )
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def run(self, transport_type: str = "stdio"):
        """Run the MCP server."""
        if transport_type == "stdio":
            # For stdio transport
            import sys
            from mcp.server.stdio import stdio_server
            
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream, write_stream, 
                    options=self.server.create_initialization_options()
                )
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")


async def main():
    """Main entry point for MCP server."""
    if not MCP_AVAILABLE:
        print("Error: MCP dependencies not available")
        print("Install with: pip install model-context-protocol")
        return
    
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting CANS MCP Server")
    
    server = CANSMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())