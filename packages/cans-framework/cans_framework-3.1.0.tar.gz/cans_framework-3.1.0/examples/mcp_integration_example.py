"""
CANS MCP Server Integration Example

Demonstrates how to integrate CANS with LLMs and AI applications
using the Model Context Protocol (MCP) server.
"""

import asyncio
import json
import pandas as pd
import numpy as np
from pathlib import Path
import subprocess
import sys
import time


def create_sample_datasets():
    """Create sample datasets for MCP demonstration."""
    np.random.seed(42)
    
    # Dataset 1: Marketing Campaign Analysis
    n1 = 1000
    age = np.random.normal(35, 10, n1)
    income = np.random.normal(50000, 15000, n1)
    education = np.random.choice([12, 14, 16, 18], n1)
    
    # Treatment assignment with confounding
    treatment_prob = 1 / (1 + np.exp(-(0.01 * income + 0.02 * education - 2)))
    treatment = np.random.binomial(1, treatment_prob)
    
    # Outcome with treatment effect
    treatment_effect = 5 + 0.1 * education
    outcome = (30 + 0.5 * age + 0.0001 * income + 2 * education + 
              treatment * treatment_effect + np.random.normal(0, 5, n1))
    
    marketing_df = pd.DataFrame({
        'customer_id': range(1, n1+1),
        'age': age,
        'income': income,
        'education': education,
        'treatment': treatment,
        'conversion_rate': outcome
    })
    
    # Dataset 2: Medical Treatment Study
    n2 = 800
    age = np.random.normal(55, 15, n2)
    bmi = np.random.normal(25, 4, n2)
    severity = np.random.uniform(1, 10, n2)
    
    # Treatment assignment
    treatment_prob = 1 / (1 + np.exp(-(0.1 * severity + 0.05 * age - 4)))
    treatment = np.random.binomial(1, treatment_prob)
    
    # Recovery score with treatment effect
    treatment_effect = 10 + 0.5 * severity
    recovery = (40 + 0.3 * age - 0.5 * bmi + 2 * severity +
               treatment * treatment_effect + np.random.normal(0, 8, n2))
    
    medical_df = pd.DataFrame({
        'patient_id': range(1, n2+1),
        'age': age,
        'bmi': bmi,
        'severity_score': severity,
        'treatment': treatment,
        'recovery_score': recovery
    })
    
    # Dataset 3: Model predictions for evaluation
    predictions_df = pd.DataFrame({
        'mu0': np.random.normal(45, 8, 500),
        'mu1': np.random.normal(55, 9, 500),
        'treatments': np.random.binomial(1, 0.4, 500),
        'outcomes': np.random.normal(50, 10, 500)
    })
    
    return marketing_df, medical_df, predictions_df


def save_datasets():
    """Save sample datasets to files."""
    marketing_df, medical_df, predictions_df = create_sample_datasets()
    
    # Save datasets
    marketing_df.to_csv('marketing_campaign_data.csv', index=False)
    medical_df.to_csv('medical_treatment_data.csv', index=False)
    predictions_df.to_csv('model_predictions.csv', index=False)
    
    print("✅ Sample datasets created:")
    print(f"📊 marketing_campaign_data.csv - {len(marketing_df)} samples")
    print(f"🏥 medical_treatment_data.csv - {len(medical_df)} samples") 
    print(f"🔮 model_predictions.csv - {len(predictions_df)} predictions")
    
    return {
        'marketing': 'marketing_campaign_data.csv',
        'medical': 'medical_treatment_data.csv',
        'predictions': 'model_predictions.csv'
    }


class MCPClientSimulator:
    """Simulates an LLM client interacting with CANS MCP server."""
    
    def __init__(self):
        self.analysis_requests = [
            {
                'task': 'Marketing Campaign Analysis',
                'data_file': 'marketing_campaign_data.csv',
                'treatment': 'treatment',
                'outcome': 'conversion_rate',
                'features': 'age,income,education',
                'question': 'Analyze the effectiveness of our marketing campaign on customer conversion rates.'
            },
            {
                'task': 'Medical Treatment Study',
                'data_file': 'medical_treatment_data.csv', 
                'treatment': 'treatment',
                'outcome': 'recovery_score',
                'features': 'age,bmi,severity_score',
                'question': 'Evaluate whether the new treatment improves patient recovery scores.'
            },
            {
                'task': 'Model Performance Evaluation',
                'predictions_file': 'model_predictions.csv',
                'question': 'Assess the quality of our causal model predictions.'
            }
        ]
    
    def simulate_llm_interaction(self):
        """Simulate how an LLM would interact with CANS MCP tools."""
        
        print("🤖 LLM SIMULATION: Analyzing causal inference tasks")
        print("="*70)
        
        for i, request in enumerate(self.analysis_requests, 1):
            print(f"\n📝 Task {i}: {request['task']}")
            print(f"Question: {request['question']}")
            
            if 'data_file' in request:
                # Simulate assumption validation call
                print(f"\n🔍 LLM calls: validate_causal_assumptions_tool")
                print(f"   Parameters:")
                print(f"   - data_path: {request['data_file']}")
                print(f"   - treatment_column: {request['treatment']}")
                print(f"   - outcome_column: {request['outcome']}")
                if 'features' in request:
                    print(f"   - feature_columns: {request['features']}")
                
                print(f"\n📊 Expected MCP Response:")
                self._simulate_validation_response(request)
                
                # Simulate quick analysis call
                print(f"\n🚀 LLM calls: quick_causal_analysis")
                print(f"   Parameters: (same as above)")
                
                print(f"\n📈 Expected MCP Response:")
                self._simulate_analysis_response(request)
            
            elif 'predictions_file' in request:
                # Simulate evaluation call
                print(f"\n📊 LLM calls: evaluate_predictions")
                print(f"   Parameters:")
                print(f"   - predictions_path: {request['predictions_file']}")
                
                print(f"\n📈 Expected MCP Response:")
                self._simulate_evaluation_response()
    
    def _simulate_validation_response(self, request):
        """Simulate MCP validation response."""
        print(f"""
Causal Assumption Validation Results:
=====================================

Dataset: {request['data_file']}
Sample Size: 1,000
Treatment Rate: 45.0%
Features Used: 3

VALIDATION SUMMARY:
✅ Overall Causal Identification: VALID

DETAILED TESTS:
📊 Unconfoundedness Test:
   - Valid: ✅
   - P-value: 0.23
   - Method: backdoor_criterion

🎯 Positivity Test:
   - Valid: ✅
   - Overlap Score: 0.85
   - Min Propensity: 0.05

🔗 SUTVA Test:
   - Valid: ✅
   - Interference Score: 0.02

RECOMMENDATIONS:
✅ Dataset appears suitable for causal inference!
        """)
    
    def _simulate_analysis_response(self, request):
        """Simulate MCP analysis response."""
        if 'marketing' in request['data_file']:
            ate = 5.2
            effect_type = "conversion rate"
            interpretation = "marketing campaign increases conversions"
        else:
            ate = 8.5
            effect_type = "recovery score"
            interpretation = "treatment improves patient recovery"
            
        print(f"""
CANS Quick Causal Analysis Report
=================================

📊 DATASET OVERVIEW:
   • File: {request['data_file']}
   • Sample Size: 1,000
   • Treatment Rate: 45% (450 treated, 550 control)
   • Features: 3
   • Text Column: No

🔍 CAUSAL ASSUMPTIONS:
   Overall Valid: ✅ YES
   
   Unconfoundedness: ✅
   Positivity: ✅
   SUTVA: ✅

📈 PRELIMINARY RESULTS:
   Treatment Group Mean: {75.2:.3f} (±{8.5:.3f})
   Control Group Mean: {67.4:.3f} (±{7.8:.3f})
   
   Naive Treatment Effect: {ate:.3f}
   ✅ Positive effect detected

⚡ NEXT STEPS:
   1. ✅ Proceed with full CANS modeling
   2. 🏗️  Train GNN+Transformer model for robust estimates  
   3. 📊 Generate individual treatment effect predictions
   4. 🎯 Validate with holdout test set
   
   💡 The {interpretation} by approximately {ate:.1f} points.
        """)
    
    def _simulate_evaluation_response(self):
        """Simulate MCP evaluation response.""" 
        print(f"""
CANS Model Evaluation Report
============================

📊 DATASET:
   • Predictions File: model_predictions.csv
   • Sample Size: 500
   • Treatment Rate: 40%

🎯 CAUSAL EFFECT ESTIMATES:
   Average Treatment Effect (ATE): 2.340 ± 0.180
   95% Confidence Interval: [1.980, 2.700]
   
   Effect Significance: ✅ Significant

📈 MODEL PERFORMANCE:
   Factual MSE: 0.0450
   ✅ Good prediction accuracy
   
   PEHE (Heterogeneous Effects): 0.1200
   ✅ Good CATE estimation
   
   CATE R²: 0.730
   ✅ Good effect prediction

💡 INTERPRETATION:
   • The estimated treatment effect is 2.340 units
   • Positive effect on the outcome
   • Model prediction quality: Excellent
   • Individual effect estimation: Strong

✨ Overall Assessment: Excellent
        """)


def demonstrate_mcp_tools():
    """Demonstrate the available MCP tools."""
    print("\n🛠️  CANS MCP Tools Demonstration")
    print("="*50)
    
    tools = [
        {
            'name': 'validate_causal_assumptions_tool',
            'description': 'Validate causal assumptions for a dataset',
            'use_case': 'Check if data is suitable for causal inference before modeling',
            'parameters': [
                'data_path (required): Path to CSV file',
                'treatment_column (required): Name of treatment column',
                'outcome_column (required): Name of outcome column',
                'feature_columns (optional): Comma-separated feature columns'
            ]
        },
        {
            'name': 'quick_causal_analysis',
            'description': 'Perform quick causal analysis including validation and basic modeling',
            'use_case': 'Get rapid insights into treatment effects with assumption checking',
            'parameters': [
                'data_path (required): Path to CSV file',
                'treatment_column (required): Name of treatment column',
                'outcome_column (required): Name of outcome column',
                'text_column (optional): Name of text column for NLP features',
                'feature_columns (optional): Comma-separated feature columns'
            ]
        },
        {
            'name': 'evaluate_predictions',
            'description': 'Evaluate causal model predictions',
            'use_case': 'Assess quality of causal model predictions and treatment effect estimates',
            'parameters': [
                'predictions_path (required): Path to CSV with mu0, mu1, treatments, outcomes columns'
            ]
        },
        {
            'name': 'get_analysis_history',
            'description': 'Get history of all causal analyses performed',
            'use_case': 'Track and review previous analyses for reproducibility',
            'parameters': [
                'No parameters required'
            ]
        }
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"\n{i}. {tool['name']}")
        print(f"   📝 Description: {tool['description']}")
        print(f"   🎯 Use Case: {tool['use_case']}")
        print(f"   ⚙️  Parameters:")
        for param in tool['parameters']:
            print(f"      • {param}")


def demonstrate_mcp_resources():
    """Demonstrate the available MCP resources."""
    print("\n📚 CANS MCP Resources")
    print("="*30)
    
    resources = [
        {
            'uri': 'cans://analysis-history',
            'name': 'CANS Analysis History',
            'description': 'JSON history of all causal analyses performed',
            'use_case': 'Track analysis progress, review past results, ensure reproducibility'
        },
        {
            'uri': 'cans://best-practices',
            'name': 'CANS Best Practices Guide',
            'description': 'Markdown guide with guidelines for effective causal inference',
            'use_case': 'Learn proper methodology, avoid common pitfalls, optimize results'
        }
    ]
    
    for resource in resources:
        print(f"\n📋 {resource['name']}")
        print(f"   🔗 URI: {resource['uri']}")
        print(f"   📝 Description: {resource['description']}")
        print(f"   🎯 Use Case: {resource['use_case']}")


def simulate_llm_conversation():
    """Simulate a conversation between an LLM and user using CANS MCP."""
    print("\n💬 LLM Conversation Simulation")
    print("="*40)
    
    conversation = [
        {
            'user': 'I have a marketing dataset with treatment assignments and conversion rates. Can you help me analyze if our campaign was effective?',
            'llm_thinking': 'User wants causal analysis. I should validate assumptions first, then run analysis.',
            'llm_actions': [
                'validate_causal_assumptions_tool(marketing_campaign_data.csv, treatment, conversion_rate, age,income,education)',
                'quick_causal_analysis(marketing_campaign_data.csv, treatment, conversion_rate, text_column=None, feature_columns=age,income,education)'
            ],
            'llm_response': """Based on my analysis of your marketing campaign data:

✅ **Data Quality**: Your dataset passes all causal inference tests with 1,000 samples and balanced treatment groups (45% treated).

📈 **Campaign Effectiveness**: The marketing campaign shows a significant positive effect:
- **Treatment Effect**: +5.2 percentage points in conversion rate
- **Confidence**: High confidence (95% CI: [4.1, 6.3])
- **Significance**: Statistically significant (p < 0.01)

🎯 **Key Insights**:
- Treated customers convert at 75.2% vs 67.4% for control group
- Effect is consistent across different age and income groups
- No evidence of confounding or selection bias

💡 **Recommendation**: The campaign is effective and should be continued. Consider expanding to similar customer segments."""
        },
        {
            'user': 'Great! I also have predictions from a previous model. Can you evaluate how good they are?',
            'llm_thinking': 'User has model predictions to evaluate. I should use the evaluation tool.',
            'llm_actions': [
                'evaluate_predictions(model_predictions.csv)'
            ],
            'llm_response': """I've evaluated your model predictions and here's the assessment:

📊 **Model Performance**: Excellent overall quality
- **Prediction Accuracy**: Very good (MSE: 0.045)
- **Treatment Effect Estimation**: Strong (ATE: 2.34 ± 0.18)
- **Individual Effects**: Well-calibrated (CATE R²: 0.73)

✅ **Key Strengths**:
- Low prediction error indicates model learns patterns well
- Treatment effects are statistically significant
- Good at predicting individual-level effects

🎯 **Model Reliability**: Your model appears highly reliable for:
- Policy decisions (strong ATE estimates)
- Personalization (good individual effect prediction)
- Production deployment (consistent performance)

💡 **Next Steps**: This model is ready for production use!"""
        }
    ]
    
    for i, turn in enumerate(conversation, 1):
        print(f"\n🗣️  Turn {i}")
        print(f"👤 User: {turn['user']}")
        print(f"\n🧠 LLM Internal Reasoning: {turn['llm_thinking']}")
        print(f"\n⚡ LLM Actions:")
        for action in turn['llm_actions']:
            print(f"   • {action}")
        print(f"\n🤖 LLM Response:\n{turn['llm_response']}")


def cleanup_files():
    """Clean up generated files."""
    files_to_remove = [
        'marketing_campaign_data.csv',
        'medical_treatment_data.csv', 
        'model_predictions.csv'
    ]
    
    for file in files_to_remove:
        if Path(file).exists():
            Path(file).unlink()
    
    print("🧹 Cleaned up temporary files")


def main():
    """Main demonstration function."""
    print("🚀 CANS MCP Integration Demonstration")
    print("="*60)
    
    try:
        # Create sample datasets
        print("📊 Creating sample datasets...")
        datasets = save_datasets()
        
        # Demonstrate MCP tools
        demonstrate_mcp_tools()
        
        # Demonstrate MCP resources  
        demonstrate_mcp_resources()
        
        # Simulate LLM interactions
        print("\n" + "="*60)
        simulator = MCPClientSimulator()
        simulator.simulate_llm_interaction()
        
        # Simulate realistic conversation
        simulate_llm_conversation()
        
        print(f"\n{'='*60}")
        print("🎉 MCP Integration Demonstration Complete!")
        
        print(f"\n💡 To use CANS MCP Server:")
        print(f"1. Start MCP server: python -m cans.api.mcp_server")
        print(f"2. Configure LLM to use MCP transport")
        print(f"3. LLM can call tools: validate_causal_assumptions_tool, quick_causal_analysis, etc.")
        print(f"4. LLM receives structured responses for analysis")
        
        print(f"\n📚 Benefits of MCP Integration:")
        print(f"• LLMs can perform causal analysis autonomously")
        print(f"• Structured tool calls ensure correct usage") 
        print(f"• Rich responses enable detailed interpretation")
        print(f"• History tracking for reproducible research")
        
    except Exception as e:
        print(f"❌ Error in demonstration: {str(e)}")
    finally:
        cleanup_files()


if __name__ == "__main__":
    main()