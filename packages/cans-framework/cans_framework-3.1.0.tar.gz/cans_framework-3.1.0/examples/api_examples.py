"""
CANS API Integration Examples

This file contains practical examples of using the CANS API for various
causal inference tasks.
"""

import pandas as pd
import numpy as np
import json
import time
from pathlib import Path

# Import CANS API client
from cans.api.client import CANSAPIClient, CANSAPIException


def create_sample_data():
    """Create sample dataset for examples."""
    np.random.seed(42)
    n = 1000
    
    # Features
    age = np.random.normal(35, 10, n)
    income = np.random.normal(50000, 15000, n)
    education = np.random.choice([12, 14, 16, 18], n)
    
    # Treatment assignment (with some confounding)
    treatment_prob = 1 / (1 + np.exp(-(0.01 * income + 0.02 * education - 2)))
    treatment = np.random.binomial(1, treatment_prob)
    
    # Outcome (with treatment effect)
    treatment_effect = 5 + 0.1 * education  # Heterogeneous effect
    outcome = (30 + 0.5 * age + 0.0001 * income + 2 * education + 
              treatment * treatment_effect + np.random.normal(0, 5, n))
    
    # Text descriptions
    descriptions = []
    for i in range(n):
        if treatment[i]:
            desc = f"Customer aged {age[i]:.0f} with high engagement and income ${income[i]:.0f}"
        else:
            desc = f"Customer aged {age[i]:.0f} with standard profile and income ${income[i]:.0f}"
        descriptions.append(desc)
    
    df = pd.DataFrame({
        'customer_id': range(1, n+1),
        'age': age,
        'income': income,
        'education': education,
        'treatment': treatment,
        'outcome': outcome,
        'description': descriptions
    })
    
    return df


def example_1_basic_validation():
    """Example 1: Basic causal assumption validation."""
    print("=" * 60)
    print("Example 1: Basic Causal Assumption Validation")
    print("=" * 60)
    
    # Create sample data
    df = create_sample_data()
    print(f"Created dataset with {len(df)} samples")
    print(f"Treatment rate: {df['treatment'].mean():.1%}")
    print(f"Average outcome: {df['outcome'].mean():.2f}")
    
    # Initialize API client
    client = CANSAPIClient(base_url="http://localhost:8000")
    
    try:
        # Validate assumptions
        print("\nValidating causal assumptions...")
        result = client.validate_assumptions(
            data=df,
            treatment_column='treatment',
            outcome_column='outcome',
            feature_columns=['age', 'income', 'education'],
            verbose=True
        )
        
        print(f"\n✅ Validation Results:")
        print(f"Overall valid: {result['causal_identification_valid']}")
        print(f"Sample size: {result['summary']['sample_size']:,}")
        print(f"Treatment rate: {result['summary']['treatment_rate']:.1%}")
        
        # Check specific tests
        if result['unconfoundedness_test']['valid']:
            print("✅ Unconfoundedness test passed")
        else:
            print("❌ Unconfoundedness test failed")
            
        if result['positivity_test']['valid']:
            print("✅ Positivity test passed")
        else:
            print("❌ Positivity test failed")
            
        if result['sutva_test']['valid']:
            print("✅ SUTVA test passed")  
        else:
            print("❌ SUTVA test failed")
        
        # Show recommendations
        if result['recommendations']:
            print(f"\n📋 Recommendations:")
            for rec in result['recommendations']:
                print(f"• {rec}")
        else:
            print("\n🎉 No issues detected - proceed with causal analysis!")
            
    except CANSAPIException as e:
        print(f"❌ API Error: {e.message}")
        return None
    
    return result


def example_2_complete_workflow():
    """Example 2: Complete causal analysis workflow."""
    print("\n" + "=" * 60)
    print("Example 2: Complete Causal Analysis Workflow")
    print("=" * 60)
    
    # Create and save sample data
    df = create_sample_data()
    data_path = "sample_marketing_data.csv"
    df.to_csv(data_path, index=False)
    print(f"Saved sample data to {data_path}")
    
    # Initialize client
    client = CANSAPIClient(base_url="http://localhost:8000")
    
    try:
        print("\n🔍 Step 1: Validating assumptions...")
        validation = client.validate_assumptions(
            data=data_path,
            treatment_column='treatment',
            outcome_column='outcome',
            feature_columns=['age', 'income', 'education']
        )
        
        if not validation['causal_identification_valid']:
            print("⚠️  Assumptions not met, but proceeding for demonstration...")
        else:
            print("✅ Assumptions validated successfully!")
        
        print("\n🏗️  Step 2: Training causal model...")
        training = client.train_model(
            data=data_path,
            treatment_column='treatment',
            outcome_column='outcome', 
            feature_columns=['age', 'income', 'education'],
            text_column='description',
            model_config={
                'gnn_type': 'GCN',
                'gnn_hidden_dim': 128,
                'fusion_dim': 256,
                'text_model': 'distilbert-base-uncased'
            },
            training_config={
                'learning_rate': 0.001,
                'batch_size': 32,
                'epochs': 20,  # Reduced for demo
                'loss_type': 'cfr'
            },
            experiment_name='marketing_campaign_analysis'
        )
        
        model_id = training['model_id']
        print(f"✅ Model trained successfully! ID: {model_id[:8]}...")
        print(f"Training time: {training['training_time']:.1f} seconds")
        print(f"Final ATE: {training['final_performance']['ate']:.3f}")
        
        print("\n🔮 Step 3: Generating predictions...")
        test_data = df.sample(100)  # Use subset for prediction
        predictions = client.predict(
            model_id=model_id,
            data=test_data,
            return_counterfactuals=True,
            return_uncertainty=False
        )
        
        ate_estimated = predictions['summary_stats']['ate']
        ate_std = predictions['summary_stats']['ate_std']
        print(f"✅ Predictions generated for {len(test_data)} samples")
        print(f"Estimated ATE: {ate_estimated:.3f} ± {ate_std:.3f}")
        
        print("\n📊 Step 4: Evaluating model performance...")
        # Prepare evaluation data
        eval_data = []
        for i, (_, row) in enumerate(test_data.iterrows()):
            eval_data.append({
                'mu0': predictions['predictions'][i]['mu0'],
                'mu1': predictions['predictions'][i]['mu1'], 
                'treatment': row['treatment'],
                'outcome': row['outcome']
            })
        
        evaluation = client.evaluate_predictions(eval_data)
        
        print(f"📈 Evaluation Results:")
        print(f"ATE: {evaluation['ate']:.3f} ± {evaluation['ate_std']:.3f}")
        print(f"95% CI: [{evaluation['ate_confidence_interval'][0]:.3f}, {evaluation['ate_confidence_interval'][1]:.3f}]")
        print(f"Factual MSE: {evaluation['factual_mse']:.4f}")
        print(f"PEHE: {evaluation.get('pehe', 'N/A')}")
        
        # Interpretation
        if abs(evaluation['ate']) > 2 * evaluation['ate_std']:
            print("✅ Treatment effect is statistically significant!")
        else:
            print("⚠️  Treatment effect may not be statistically significant")
        
        return {
            'validation': validation,
            'training': training, 
            'predictions': predictions,
            'evaluation': evaluation,
            'model_id': model_id
        }
        
    except CANSAPIException as e:
        print(f"❌ API Error: {e.message}")
        return None
    finally:
        # Clean up
        if Path(data_path).exists():
            Path(data_path).unlink()


def example_3_batch_analysis():
    """Example 3: Analyzing multiple datasets."""
    print("\n" + "=" * 60)
    print("Example 3: Batch Analysis of Multiple Datasets") 
    print("=" * 60)
    
    client = CANSAPIClient(base_url="http://localhost:8000")
    
    # Create multiple datasets with different characteristics
    datasets = []
    for i in range(3):
        df = create_sample_data()
        # Add noise to make datasets different
        df['outcome'] += np.random.normal(0, 2, len(df))
        
        dataset_name = f"dataset_{i+1}.csv"
        df.to_csv(dataset_name, index=False)
        datasets.append(dataset_name)
    
    results = []
    
    try:
        for i, dataset_path in enumerate(datasets):
            print(f"\n📊 Analyzing Dataset {i+1}: {dataset_path}")
            
            # Quick validation
            validation = client.validate_assumptions(
                data=dataset_path,
                treatment_column='treatment',
                outcome_column='outcome'
            )
            
            print(f"Valid for causal inference: {'✅' if validation['causal_identification_valid'] else '❌'}")
            print(f"Sample size: {validation['summary']['sample_size']:,}")
            print(f"Treatment rate: {validation['summary']['treatment_rate']:.1%}")
            
            results.append({
                'dataset': dataset_path,
                'validation': validation,
                'valid': validation['causal_identification_valid'],
                'sample_size': validation['summary']['sample_size'],
                'treatment_rate': validation['summary']['treatment_rate']
            })
        
        # Summary
        print(f"\n📈 Batch Analysis Summary:")
        valid_datasets = sum(1 for r in results if r['valid'])
        print(f"Valid datasets: {valid_datasets}/{len(results)}")
        
        avg_treatment_rate = np.mean([r['treatment_rate'] for r in results])
        print(f"Average treatment rate: {avg_treatment_rate:.1%}")
        
        return results
        
    except CANSAPIException as e:
        print(f"❌ API Error: {e.message}")
        return None
    finally:
        # Clean up files
        for dataset_path in datasets:
            if Path(dataset_path).exists():
                Path(dataset_path).unlink()


def example_4_error_handling():
    """Example 4: Comprehensive error handling."""
    print("\n" + "=" * 60)
    print("Example 4: Error Handling and Robustness")
    print("=" * 60)
    
    client = CANSAPIClient(base_url="http://localhost:8000")
    
    print("🧪 Testing various error conditions...")
    
    # Test 1: Invalid data format
    print("\n1. Testing invalid data format...")
    try:
        result = client.validate_assumptions(
            data=[{"invalid": "data"}],  # Missing required columns
            treatment_column='treatment',
            outcome_column='outcome'
        )
        print("❌ Should have failed but didn't")
    except CANSAPIException as e:
        print(f"✅ Correctly caught error: {e.message}")
    
    # Test 2: Nonexistent file
    print("\n2. Testing nonexistent file...")
    try:
        result = client.validate_assumptions(
            data="nonexistent_file.csv",
            treatment_column='treatment',
            outcome_column='outcome'
        )
        print("❌ Should have failed but didn't")
    except CANSAPIException as e:
        print(f"✅ Correctly caught error: {e.message}")
    
    # Test 3: Invalid model ID for prediction
    print("\n3. Testing invalid model ID...")
    try:
        result = client.predict(
            model_id="invalid-model-id",
            data=[{"age": 30, "income": 50000}]
        )
        print("❌ Should have failed but didn't")
    except CANSAPIException as e:
        print(f"✅ Correctly caught error: {e.message}")
    
    # Test 4: Server connectivity
    print("\n4. Testing server connectivity...")
    offline_client = CANSAPIClient(base_url="http://invalid-url:9999")
    try:
        result = offline_client.health_check()
        print("❌ Should have failed but didn't")
    except CANSAPIException as e:
        print(f"✅ Correctly caught connectivity error: {e.message}")
    
    print("\n✅ Error handling tests completed!")


def example_5_model_management():
    """Example 5: Model lifecycle management."""
    print("\n" + "=" * 60)
    print("Example 5: Model Lifecycle Management")
    print("=" * 60)
    
    client = CANSAPIClient(base_url="http://localhost:8000")
    
    try:
        # Create sample data
        df = create_sample_data()
        
        print("🏗️  Training multiple models...")
        model_ids = []
        
        # Train different model configurations
        configs = [
            {'gnn_type': 'GCN', 'experiment_name': 'gcn_model'},
            {'gnn_type': 'GAT', 'experiment_name': 'gat_model'},
        ]
        
        for config in configs:
            print(f"Training {config['experiment_name']}...")
            training = client.train_model(
                data=df,
                treatment_column='treatment',
                outcome_column='outcome',
                feature_columns=['age', 'income', 'education'],
                model_config={'gnn_type': config['gnn_type']},
                training_config={'epochs': 5},  # Quick training
                experiment_name=config['experiment_name']
            )
            model_ids.append(training['model_id'])
            print(f"✅ Model trained: {training['model_id'][:8]}...")
        
        print(f"\n📋 Listing all models...")
        models_list = client.list_models()
        print(f"Total models: {models_list['total_count']}")
        
        for model in models_list['models']:
            print(f"• {model['experiment_name']}: {model['model_id'][:8]}... "
                 f"(Performance: {model['performance_metrics'].get('ate', 'N/A')})")
        
        # Get detailed info for first model
        if model_ids:
            print(f"\n🔍 Getting detailed info for model {model_ids[0][:8]}...")
            model_info = client.get_model_info(model_ids[0])
            print(f"Created: {model_info['created_at']}")
            print(f"Status: {model_info['status']}")
            print(f"Performance: {model_info['performance_metrics']}")
        
        # Clean up - delete models
        print(f"\n🗑️  Cleaning up models...")
        for model_id in model_ids:
            delete_result = client.delete_model(model_id)
            print(f"✅ {delete_result['message']}")
        
    except CANSAPIException as e:
        print(f"❌ API Error: {e.message}")


def example_6_async_processing():
    """Example 6: Async processing example."""
    print("\n" + "=" * 60)
    print("Example 6: Asynchronous Processing")
    print("=" * 60)
    
    import asyncio
    from cans.api.client import AsyncCANSAPIClient
    
    async def async_analysis():
        try:
            async with AsyncCANSAPIClient(base_url="http://localhost:8000") as client:
                # This would use the async client for concurrent operations
                print("✅ Async client initialized")
                print("🔄 Async operations would be implemented here")
                
        except Exception as e:
            print(f"❌ Async error: {e}")
    
    # For now, just show the structure
    print("📝 Async example structure ready")
    print("💡 Implement with: asyncio.run(async_analysis())")


def run_all_examples():
    """Run all API examples."""
    print("🚀 CANS API Integration Examples")
    print("=" * 80)
    
    # Check if server is running
    try:
        client = CANSAPIClient(base_url="http://localhost:8000")
        health = client.health_check()
        print(f"✅ CANS API Server is running (version {health['version']})")
        print(f"Uptime: {health['uptime']:.1f} seconds")
    except CANSAPIException as e:
        print(f"❌ CANS API Server not available: {e.message}")
        print("💡 Start server with: uvicorn cans.api.server:app --host 0.0.0.0 --port 8000")
        return
    
    examples = [
        example_1_basic_validation,
        example_2_complete_workflow,
        example_3_batch_analysis,
        example_4_error_handling,
        example_5_model_management,
        example_6_async_processing
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            print(f"\n{'='*20} Running Example {i} {'='*20}")
            result = example_func()
            if result is not None:
                print(f"✅ Example {i} completed successfully")
            else:
                print(f"⚠️  Example {i} completed with issues")
        except Exception as e:
            print(f"❌ Example {i} failed: {str(e)}")
        
        # Small delay between examples
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("🎉 All API examples completed!")
    print("💡 Check the API documentation at http://localhost:8000/docs")


if __name__ == "__main__":
    run_all_examples()