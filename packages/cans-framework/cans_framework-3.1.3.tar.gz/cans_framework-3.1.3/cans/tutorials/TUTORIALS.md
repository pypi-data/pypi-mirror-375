# 🎓 CANS Tutorial Series

**Learn CANS step-by-step with tutorials for every skill level and use case**

## 📚 Tutorial Index

### 🚀 Beginner Tutorials
- [Tutorial 1: First Steps with CANS](#tutorial-1-first-steps-with-cans)
- [Tutorial 2: Understanding Your Data](#tutorial-2-understanding-your-data) 
- [Tutorial 3: Running Your First Analysis](#tutorial-3-running-your-first-analysis)

### 📊 Intermediate Tutorials
- [Tutorial 4: Advanced Configuration](#tutorial-4-advanced-configuration)
- [Tutorial 5: API Integration](#tutorial-5-api-integration)
- [Tutorial 6: Custom Workflows](#tutorial-6-custom-workflows)

### 🔬 Advanced Tutorials
- [Tutorial 7: Custom Models](#tutorial-7-custom-models)
- [Tutorial 8: Production Deployment](#tutorial-8-production-deployment)
- [Tutorial 9: LLM Integration](#tutorial-9-llm-integration)

### 🏢 Domain-Specific Tutorials
- [Tutorial 10: Healthcare Applications](#tutorial-10-healthcare-applications)
- [Tutorial 11: Marketing Analytics](#tutorial-11-marketing-analytics)
- [Tutorial 12: Financial Analysis](#tutorial-12-financial-analysis)

---

## Tutorial 1: First Steps with CANS

**Target Audience**: Complete beginners  
**Time**: 15 minutes  
**Prerequisites**: Basic Python knowledge

### What You'll Learn
- Install CANS framework
- Understand causal inference basics
- Run your first causal analysis

### Step 1: Installation and Setup

```bash
# Install CANS
pip install cans-framework

# Verify installation
python -c "import cans; print(f'CANS {cans.__version__} installed successfully!')"
```

### Step 2: Understanding Causal Inference

**What is Causal Inference?**

Causal inference answers "what if" questions:
- What if we give this treatment to patients?
- What if we change our marketing strategy?
- What if we implement this policy?

**Key Concepts:**
- **Treatment**: The intervention you want to study (e.g., medication, ad campaign)
- **Outcome**: What you want to measure (e.g., recovery rate, sales)
- **Confounders**: Other factors that might affect both treatment and outcome

### Step 3: Your First Analysis

Let's analyze whether a marketing campaign increases sales:

```python
# Step 3a: Create sample data
import pandas as pd
import numpy as np
from cans import validate_causal_assumptions

# Generate sample marketing data
np.random.seed(42)
n = 1000

data = {
    'customer_id': range(1, n+1),
    'age': np.random.normal(35, 10, n),
    'income': np.random.normal(50000, 15000, n),
    'email_campaign': np.random.binomial(1, 0.4, n),  # Treatment
    'monthly_spend': np.random.normal(200, 50, n)     # Outcome
}

# Add treatment effect (people who got emails spend more)
for i in range(n):
    if data['email_campaign'][i] == 1:
        data['monthly_spend'][i] += 30  # $30 campaign effect

df = pd.DataFrame(data)
print("✅ Sample data created!")
print(f"📊 Dataset shape: {df.shape}")
print(f"📈 Campaign rate: {df['email_campaign'].mean():.1%}")
```

```python
# Step 3b: Validate causal assumptions
results = validate_causal_assumptions(
    X=df[['age', 'income']].values,
    T=df['email_campaign'].values,
    Y=df['monthly_spend'].values
)

print(f"🔍 Causal assumptions valid: {results['causal_identification_valid']}")

if results['causal_identification_valid']:
    print("✅ Great! Your data is suitable for causal analysis")
else:
    print("⚠️ Warning: Some assumptions may not be met")
```

```python
# Step 3c: Calculate simple treatment effect
treated = df[df['email_campaign'] == 1]['monthly_spend']
control = df[df['email_campaign'] == 0]['monthly_spend']

effect = treated.mean() - control.mean()
print(f"📊 Campaign Effect: ${effect:.2f}")
print(f"💰 Treated group spends: ${treated.mean():.2f}")
print(f"💰 Control group spends: ${control.mean():.2f}")
```

**Expected Output:**
```
✅ Sample data created!
📊 Dataset shape: (1000, 5)
📈 Campaign rate: 40.0%
🔍 Causal assumptions valid: True
✅ Great! Your data is suitable for causal analysis
📊 Campaign Effect: $29.87
💰 Treated group spends: $229.87
💰 Control group spends: $200.00
```

### 🎯 Key Takeaways
1. **Always validate assumptions first** - this ensures reliable results
2. **Treatment effect = Treated average - Control average** (in simple cases)
3. **CANS validates your analysis** to ensure scientific rigor

### 📚 What's Next?
- **Tutorial 2**: Learn to analyze your own data files
- **Tutorial 3**: Use CANS advanced features for better results

---

## Tutorial 2: Understanding Your Data

**Target Audience**: Beginners with own datasets  
**Time**: 20 minutes  
**Prerequisites**: Tutorial 1 completed

### What You'll Learn
- Prepare real data for CANS
- Understand data quality requirements
- Handle common data issues

### Step 1: Loading Your Data

```python
import pandas as pd
from cans.utils.data import create_sample_dataset

# Option A: Load your CSV file
df = pd.read_csv("your_data.csv")

# Option B: Use CANS sample data (for practice)
datasets = create_sample_dataset(n_samples=1000)
df = datasets[0].to_pandas()  # Convert to regular DataFrame

print("📊 Data Overview:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print("\nFirst 5 rows:")
print(df.head())
```

### Step 2: Data Quality Checklist

```python
def check_data_quality(df, treatment_col, outcome_col):
    """Comprehensive data quality check."""
    
    print("🔍 Data Quality Report")
    print("=" * 30)
    
    # Basic info
    print(f"📊 Sample size: {len(df):,}")
    print(f"📝 Number of features: {len(df.columns)}")
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"⚠️ Missing values found:")
        for col, count in missing[missing > 0].items():
            print(f"   • {col}: {count} ({count/len(df)*100:.1f}%)")
    else:
        print("✅ No missing values")
    
    # Treatment column check
    if treatment_col in df.columns:
        unique_treatments = df[treatment_col].unique()
        print(f"🎯 Treatment '{treatment_col}':")
        print(f"   • Values: {unique_treatments}")
        
        if len(unique_treatments) == 2 and set(unique_treatments) == {0, 1}:
            print("   • ✅ Binary treatment (0/1) - perfect!")
            treatment_rate = df[treatment_col].mean()
            print(f"   • Treatment rate: {treatment_rate:.1%}")
            
            if 0.05 <= treatment_rate <= 0.95:
                print("   • ✅ Good treatment balance")
            else:
                print("   • ⚠️ Imbalanced treatment groups")
        else:
            print("   • ⚠️ Treatment should be binary (0/1)")
    else:
        print(f"❌ Treatment column '{treatment_col}' not found")
    
    # Outcome column check
    if outcome_col in df.columns:
        print(f"📈 Outcome '{outcome_col}':")
        if df[outcome_col].dtype in ['int64', 'float64']:
            print(f"   • ✅ Numerical outcome")
            print(f"   • Range: {df[outcome_col].min():.2f} to {df[outcome_col].max():.2f}")
            print(f"   • Mean: {df[outcome_col].mean():.2f}")
        else:
            print("   • ⚠️ Outcome should be numerical")
    else:
        print(f"❌ Outcome column '{outcome_col}' not found")
    
    # Feature columns
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    feature_cols = [col for col in numeric_cols 
                   if col not in [treatment_col, outcome_col]]
    
    print(f"🔢 Features available: {len(feature_cols)}")
    if len(feature_cols) >= 3:
        print("   • ✅ Good number of features for analysis")
    else:
        print("   • ⚠️ Consider adding more features to control for confounding")
    
    return {
        'ready_for_analysis': (
            treatment_col in df.columns and 
            outcome_col in df.columns and
            len(feature_cols) >= 1 and
            missing.sum() == 0
        ),
        'feature_columns': feature_cols
    }

# Run quality check
quality_report = check_data_quality(df, 'treatment', 'outcome')
```

### Step 3: Fixing Common Issues

```python
def fix_common_issues(df, treatment_col, outcome_col):
    """Fix common data preparation issues."""
    
    df_fixed = df.copy()
    
    print("🔧 Fixing Common Issues:")
    print("=" * 25)
    
    # Fix 1: Handle missing values
    missing_before = df_fixed.isnull().sum().sum()
    if missing_before > 0:
        print(f"📝 Handling {missing_before} missing values...")
        
        # Fill numerical columns with median
        numeric_cols = df_fixed.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            if df_fixed[col].isnull().any():
                df_fixed[col].fillna(df_fixed[col].median(), inplace=True)
        
        # Fill categorical columns with mode
        cat_cols = df_fixed.select_dtypes(include=['object']).columns
        for col in cat_cols:
            if df_fixed[col].isnull().any():
                df_fixed[col].fillna(df_fixed[col].mode()[0], inplace=True)
        
        print(f"   ✅ Fixed {missing_before} missing values")
    
    # Fix 2: Convert treatment to binary
    if treatment_col in df_fixed.columns:
        unique_vals = df_fixed[treatment_col].unique()
        
        if len(unique_vals) == 2 and not set(unique_vals) == {0, 1}:
            print(f"📝 Converting treatment to 0/1...")
            val_map = {unique_vals[0]: 0, unique_vals[1]: 1}
            df_fixed[treatment_col] = df_fixed[treatment_col].map(val_map)
            print(f"   ✅ Converted {unique_vals[0]}→0, {unique_vals[1]}→1")
    
    # Fix 3: Remove extreme outliers (beyond 3 standard deviations)
    if outcome_col in df_fixed.columns:
        outcome_mean = df_fixed[outcome_col].mean()
        outcome_std = df_fixed[outcome_col].std()
        
        outlier_threshold = 3
        outliers = (
            (df_fixed[outcome_col] > outcome_mean + outlier_threshold * outcome_std) |
            (df_fixed[outcome_col] < outcome_mean - outlier_threshold * outcome_std)
        )
        
        outlier_count = outliers.sum()
        if outlier_count > 0:
            print(f"📝 Removing {outlier_count} extreme outliers...")
            df_fixed = df_fixed[~outliers].reset_index(drop=True)
            print(f"   ✅ Removed {outlier_count} outliers")
    
    print(f"\n✅ Data preparation complete!")
    print(f"📊 Final dataset: {len(df_fixed)} rows, {len(df_fixed.columns)} columns")
    
    return df_fixed

# Apply fixes
df_clean = fix_common_issues(df, 'treatment', 'outcome')
```

### Step 4: Final Validation

```python
# Run final quality check
final_report = check_data_quality(df_clean, 'treatment', 'outcome')

if final_report['ready_for_analysis']:
    print("\n🎉 Data is ready for CANS analysis!")
    print("📚 Next: Go to Tutorial 3 to run advanced analysis")
else:
    print("\n⚠️ Data needs more preparation")
    print("💡 Consider:")
    print("   • Adding more feature columns")
    print("   • Checking treatment/outcome column names") 
    print("   • Ensuring sufficient sample size (>500)")
```

### 🎯 Key Takeaways
1. **Data quality is crucial** - bad data leads to unreliable results
2. **Binary treatments (0/1)** work best with CANS
3. **More features = better confounder control** 
4. **Always check your data before analysis**

---

## Tutorial 3: Running Your First Analysis

**Target Audience**: Beginners ready for full analysis  
**Time**: 25 minutes  
**Prerequisites**: Tutorials 1-2 completed

### What You'll Learn
- Use CANS CLI tools
- Interpret causal analysis results  
- Generate actionable insights

### Step 1: CLI Analysis (Easiest Method)

```bash
# Validate assumptions first
cans-validate --data my_data.csv \
              --treatment email_campaign \
              --outcome monthly_spend \
              --features age,income,education \
              --verbose

# Run complete analysis  
cans-analyze --data my_data.csv \
             --treatment email_campaign \
             --outcome monthly_spend \
             --features age,income,education \
             --output-dir results/ \
             --verbose
```

### Step 2: Python API Analysis (More Control)

```python
from cans.api.client import CANSAPIClient
import pandas as pd

# Setup (use local server or remote API)
client = CANSAPIClient(
    base_url="http://localhost:8000",  # Start with: cans-server
    # api_key="your-key-here"  # Only needed for remote servers
)

# Load your data
df = pd.read_csv("marketing_data.csv")

print("🚀 Starting CANS Analysis Pipeline")
print("="*40)

# Step 1: Validate assumptions
print("Step 1: 🔍 Validating causal assumptions...")
validation = client.validate_assumptions(
    data=df,
    treatment_column="email_campaign", 
    outcome_column="monthly_spend",
    feature_columns=["age", "income", "education"]
)

# Interpret validation results
def interpret_validation(results):
    print("\n📊 Validation Results:")
    
    if results['causal_identification_valid']:
        print("✅ PASSED: Data meets causal inference requirements")
        
        print(f"   📈 Sample size: {results['summary']['sample_size']:,}")
        print(f"   ⚖️  Treatment balance: {results['summary']['treatment_rate']:.1%}")
        
        # Test details
        tests = ['unconfoundedness_test', 'positivity_test', 'sutva_test']
        for test in tests:
            if test in results:
                status = "✅" if results[test]['valid'] else "❌"
                test_name = test.replace('_test', '').title()
                print(f"   {status} {test_name}")
        
        return True
    else:
        print("❌ FAILED: Causal assumptions not met")
        
        if results['recommendations']:
            print("\n💡 Recommendations:")
            for rec in results['recommendations']:
                print(f"   • {rec}")
        
        return False

validation_passed = interpret_validation(validation)
```

```python
# Step 2: Run analysis (if validation passed)
if validation_passed:
    print("\nStep 2: 🏗️ Running causal analysis...")
    
    analysis = client.complete_analysis(
        data=df,
        treatment_column="email_campaign",
        outcome_column="monthly_spend", 
        feature_columns=["age", "income", "education"],
        model_config={
            "gnn_type": "GCN",
            "epochs": 30
        },
        experiment_name="marketing_campaign_analysis"
    )
    
    # Interpret analysis results
    def interpret_analysis(results):
        print("\n📈 Analysis Results:")
        
        eval_results = results['evaluation_results']
        
        # Main findings
        ate = eval_results['ate']
        ate_std = eval_results['ate_std']
        ci_lower, ci_upper = eval_results['ate_confidence_interval']
        
        print(f"💰 Campaign Effect: ${ate:.2f}")
        print(f"📊 Standard Error: ±${ate_std:.2f}")
        print(f"🎯 95% Confidence Interval: [${ci_lower:.2f}, ${ci_upper:.2f}]")
        
        # Statistical significance
        is_significant = abs(ate) > 2 * ate_std
        print(f"📋 Statistical Significance: {'✅ Yes' if is_significant else '❌ No'}")
        
        # Model quality
        mse = eval_results['factual_mse']
        print(f"🔧 Model Quality (MSE): {mse:.4f}")
        quality = "Excellent" if mse < 0.05 else "Good" if mse < 0.2 else "Needs Improvement"
        print(f"📈 Model Assessment: {quality}")
        
        return {
            'effect': ate,
            'significant': is_significant,
            'quality_good': mse < 0.2
        }
    
    analysis_summary = interpret_analysis(analysis)
```

### Step 3: Business Interpretation

```python
def generate_business_insights(analysis_summary, validation):
    """Generate actionable business insights."""
    
    print("\n💼 Business Insights & Recommendations:")
    print("="*45)
    
    effect = analysis_summary['effect']
    significant = analysis_summary['significant']
    quality_good = analysis_summary['quality_good']
    
    sample_size = validation['summary']['sample_size']
    treatment_rate = validation['summary']['treatment_rate']
    
    # Primary recommendation
    if significant and quality_good:
        if effect > 0:
            print(f"🎉 STRONG RECOMMENDATION: Scale the email campaign!")
            print(f"   💰 Expected return: ${effect:.2f} per customer")
            
            # Calculate business impact
            total_customers = sample_size / treatment_rate  # Estimate total pool
            annual_impact = total_customers * effect * 12  # Monthly to annual
            print(f"   📈 Potential annual impact: ${annual_impact:,.0f}")
            
        else:
            print(f"⛔ STRONG RECOMMENDATION: Stop the email campaign!")
            print(f"   💸 Campaign is reducing spend by ${abs(effect):.2f} per customer")
            
    elif significant and not quality_good:
        print(f"⚠️ CAUTIOUS RECOMMENDATION:")
        print(f"   Effect detected (${effect:.2f}) but model quality needs improvement")
        print(f"   💡 Collect more data or add features before final decision")
        
    elif not significant:
        print(f"🤔 INCONCLUSIVE: No clear treatment effect detected")
        print(f"   📊 Estimated effect: ${effect:.2f} (not statistically significant)")
        print(f"   💡 Consider:")
        print(f"      • Larger sample size for more statistical power")
        print(f"      • Different campaign variations to test")
        print(f"      • Longer measurement period")
    
    # Additional insights
    print(f"\n📊 Study Details:")
    print(f"   • Sample analyzed: {sample_size:,} customers")
    print(f"   • Campaign exposure rate: {treatment_rate:.1%}")
    print(f"   • Analysis confidence: {'High' if quality_good else 'Medium'}")
    
    # Next steps
    print(f"\n🎯 Recommended Next Steps:")
    if significant and effect > 0:
        print(f"   1. 🚀 Deploy campaign to broader audience")
        print(f"   2. 📊 Monitor performance with control group") 
        print(f"   3. 🧪 Test campaign variations for optimization")
        print(f"   4. 📈 Measure long-term customer lifetime value")
    elif significant and effect < 0:
        print(f"   1. ⛔ Immediately pause current campaign")
        print(f"   2. 🔍 Investigate why campaign backfired")
        print(f"   3. 🧪 Test alternative messaging/timing")
        print(f"   4. 📊 Analyze customer feedback for insights")
    else:
        print(f"   1. 📈 Increase sample size for clearer signal")
        print(f"   2. 🎯 Test more targeted campaigns")
        print(f"   3. 📊 Add more customer features to analysis")
        print(f"   4. 🧪 Try different campaign formats")

# Generate insights
if validation_passed:
    generate_business_insights(analysis_summary, validation)
```

### Step 4: Saving and Sharing Results

```python
# Save detailed results
if validation_passed:
    # Save to JSON for programmatic use
    import json
    with open('campaign_analysis_results.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    # Create executive summary
    executive_summary = f"""
MARKETING CAMPAIGN ANALYSIS - EXECUTIVE SUMMARY
==============================================

CAMPAIGN PERFORMANCE:
• Effect: ${analysis_summary['effect']:.2f} per customer
• Statistical Significance: {'Yes' if analysis_summary['significant'] else 'No'}
• Sample Size: {validation['summary']['sample_size']:,} customers
• Campaign Reach: {validation['summary']['treatment_rate']:.1%}

RECOMMENDATION:
"""
    
    if analysis_summary['significant'] and analysis_summary['effect'] > 0:
        executive_summary += "✅ SCALE CAMPAIGN - Strong positive impact detected"
    elif analysis_summary['significant'] and analysis_summary['effect'] < 0:
        executive_summary += "❌ STOP CAMPAIGN - Negative impact on customer spend"
    else:
        executive_summary += "⚠️ INCONCLUSIVE - Collect more data before deciding"
    
    # Save executive summary
    with open('executive_summary.txt', 'w') as f:
        f.write(executive_summary)
    
    print("\n💾 Results saved:")
    print("   • campaign_analysis_results.json (detailed)")
    print("   • executive_summary.txt (for executives)")
```

### 🎯 Key Takeaways
1. **Always validate assumptions first** - ensures reliable results
2. **Statistical significance ≠ business significance** - consider practical impact
3. **Model quality matters** - poor models give unreliable estimates
4. **Business context is crucial** - translate statistics to actionable insights

### 🚀 What's Next?
- **Tutorial 4**: Learn advanced configuration options
- **Tutorial 5**: Integrate CANS into your applications
- **Domain tutorials**: See healthcare, finance, and marketing examples

---

## Tutorial 4: Advanced Configuration

**Target Audience**: Intermediate users  
**Time**: 30 minutes  
**Prerequisites**: Tutorials 1-3 completed

### What You'll Learn
- Customize CANS model architecture
- Optimize training parameters
- Handle different data types
- Configure for production use

### Step 1: Model Architecture Configuration

```python
from cans import CANSConfig

# Create custom configuration
config = CANSConfig()

print("🏗️ Customizing Model Architecture:")
print("="*35)

# Graph Neural Network settings
config.model.gnn_type = "GAT"  # Options: "GCN", "GAT", "GraphSAGE" 
config.model.gnn_hidden_dim = 256  # Increase for more complex patterns
config.model.gnn_layers = 3  # More layers for deeper analysis
config.model.gnn_dropout = 0.2  # Prevent overfitting

print(f"🧠 GNN: {config.model.gnn_type} with {config.model.gnn_layers} layers")
print(f"📏 Hidden dimension: {config.model.gnn_hidden_dim}")

# Text model settings (for datasets with text)
config.model.text_model = "bert-base-uncased"  # More powerful than distilbert
config.model.max_text_length = 256  # Longer text support
config.model.text_pooling = "cls"  # Options: "cls", "mean", "max"

print(f"📝 Text model: {config.model.text_model}")
print(f"📏 Max text length: {config.model.max_text_length}")

# Fusion layer settings
config.model.fusion_dim = 512  # Larger fusion for rich representations
config.model.fusion_type = "gated"  # Options: "concat", "gated", "attention"

print(f"🔗 Fusion: {config.model.fusion_type} with dim {config.model.fusion_dim}")

# Treatment effect estimation
config.model.num_treatments = 2  # Binary treatment
config.model.outcome_dim = 1     # Single outcome
config.model.cfr_alpha = 1.0     # Representation balancing weight

print(f"🎯 CFR alpha (balancing): {config.model.cfr_alpha}")
```

### Step 2: Training Optimization

```python
print("\n⚡ Training Optimization:")
print("="*25)

# Learning rate scheduling
config.training.learning_rate = 0.001
config.training.lr_scheduler = "cosine"  # Options: "step", "cosine", "plateau"
config.training.lr_warmup_steps = 100   # Gradual learning rate increase

# Batch and epoch settings
config.training.batch_size = 64         # Larger batches for stability
config.training.epochs = 100            # More training for better results
config.training.gradient_clip_norm = 1.0  # Prevent gradient explosion

# Early stopping
config.training.early_stopping_patience = 15
config.training.early_stopping_min_delta = 0.001

print(f"📚 Epochs: {config.training.epochs}")
print(f"🎯 Batch size: {config.training.batch_size}")
print(f"🔄 Learning rate: {config.training.learning_rate} ({config.training.lr_scheduler})")

# Loss function configuration
config.training.loss_type = "cfr"  # Causal loss for treatment effects
config.training.cfr_beta = 0.5     # IPW loss weight
config.training.cfr_gamma = 0.1    # Balancing regularization

print(f"💰 Loss: {config.training.loss_type}")
print(f"⚖️  CFR beta (IPW): {config.training.cfr_beta}")
print(f"🎨 CFR gamma (balance): {config.training.cfr_gamma}")

# Advanced training features
config.training.mixed_precision = True    # Faster training with FP16
config.training.gradient_accumulation_steps = 2  # Effective larger batches
config.training.weight_decay = 0.01       # L2 regularization

print(f"🚀 Mixed precision: {config.training.mixed_precision}")
print(f"📊 Weight decay: {config.training.weight_decay}")
```

### Step 3: Data Processing Configuration

```python
print("\n📊 Data Processing Setup:")
print("="*25)

# Graph construction
config.data.graph_construction = "global"  # Options: "knn", "similarity", "global"
config.data.knn_k = 10                     # For KNN graphs
config.data.similarity_threshold = 0.8     # For similarity graphs
config.data.graph_self_loops = True        # Add self-connections

print(f"🌐 Graph type: {config.data.graph_construction}")
if config.data.graph_construction == "knn":
    print(f"🔗 KNN neighbors: {config.data.knn_k}")

# Feature preprocessing
config.data.scale_node_features = True     # Normalize features
config.data.scale_method = "standard"      # Options: "standard", "minmax", "robust"
config.data.handle_missing = "median"      # Options: "drop", "mean", "median"

print(f"📏 Feature scaling: {config.data.scale_method}")
print(f"❓ Missing values: {config.data.handle_missing}")

# Text preprocessing (if applicable)
config.data.text_preprocessing = True
config.data.lowercase_text = True
config.data.remove_stopwords = False  # Keep for context
config.data.text_augmentation = False # Advanced: synonym replacement

print(f"📝 Text preprocessing: {config.data.text_preprocessing}")

# Data splitting
config.data.train_ratio = 0.7
config.data.val_ratio = 0.15  
config.data.test_ratio = 0.15
config.data.stratify = True    # Maintain treatment balance

print(f"📊 Split: {config.data.train_ratio:.0%}/{config.data.val_ratio:.0%}/{config.data.test_ratio:.0%}")
print(f"⚖️ Stratified: {config.data.stratify}")
```

### Step 4: Experiment Tracking

```python
print("\n🧪 Experiment Configuration:")
print("="*27)

# Experiment metadata
config.experiment.experiment_name = "advanced_marketing_analysis_v2"
config.experiment.description = "Testing advanced config with GAT and larger model"
config.experiment.tags = ["marketing", "email_campaign", "advanced_config"]

# Checkpointing
config.experiment.save_checkpoints = True
config.experiment.checkpoint_every_n_epochs = 10
config.experiment.keep_best_checkpoint = True

# Logging
config.experiment.log_level = "INFO"
config.experiment.log_metrics_every_n_steps = 50
config.experiment.save_training_plots = True

print(f"📋 Experiment: {config.experiment.experiment_name}")
print(f"🏷️ Tags: {config.experiment.tags}")
print(f"💾 Checkpoints every: {config.experiment.checkpoint_every_n_epochs} epochs")

# Reproducibility
config.experiment.random_seed = 42
config.experiment.deterministic = True  # Reproducible results (may be slower)

print(f"🎲 Random seed: {config.experiment.random_seed}")
print(f"🔒 Deterministic: {config.experiment.deterministic}")
```

### Step 5: Using Advanced Configuration

```python
# Save configuration for reuse
config.save("advanced_config.json")
print(f"\n💾 Configuration saved to: advanced_config.json")

# Use configuration in training
from cans import CANS, CANSRunner
from cans.models.gnn_modules import GAT
from cans.utils.data import load_csv_dataset, get_data_loaders
from transformers import AutoModel
import torch

# Load data with advanced config
datasets = load_csv_dataset(
    csv_path="marketing_data.csv",
    text_column="customer_feedback",  # Now we use text!
    treatment_column="email_campaign",
    outcome_column="monthly_spend", 
    feature_columns=["age", "income", "education", "previous_purchases"],
    config=config.data
)

train_loader, val_loader, test_loader = get_data_loaders(
    datasets, 
    batch_size=config.training.batch_size
)

print(f"\n📊 Data loaded with advanced preprocessing")
print(f"🚂 Training batches: {len(train_loader)}")
print(f"✅ Validation batches: {len(val_loader)}")

# Create advanced model
gnn = GAT(
    in_dim=datasets[0].num_node_features,
    hidden_dim=config.model.gnn_hidden_dim,
    output_dim=config.model.fusion_dim,
    num_layers=config.model.gnn_layers,
    dropout=config.model.gnn_dropout
)

bert = AutoModel.from_pretrained(config.model.text_model)

model = CANS(
    gnn=gnn,
    transformer=bert,
    fusion_dim=config.model.fusion_dim,
    num_treatments=config.model.num_treatments
)

print(f"\n🏗️ Advanced model created:")
print(f"   • GNN: {config.model.gnn_type} ({model.gnn.num_parameters():,} params)")
print(f"   • Text: {config.model.text_model}")
print(f"   • Total parameters: {sum(p.numel() for p in model.parameters()):,}")

# Advanced optimizer
optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=config.training.learning_rate,
    weight_decay=config.training.weight_decay
)

# Learning rate scheduler
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
    optimizer,
    T_max=config.training.epochs
)

# Train with advanced configuration
runner = CANSRunner(model, optimizer, config, scheduler=scheduler)

print(f"\n🚀 Starting advanced training...")
print(f"⚡ Mixed precision: {config.training.mixed_precision}")
print(f"🧠 Model complexity: High")
print(f"⏱️ Expected time: 15-30 minutes")

# This would run the actual training
# history = runner.fit(train_loader, val_loader)
# print(f"✅ Training complete! Best ATE: {history['best_ate']:.3f}")
```

### Step 6: Production Configuration

```python
# Create production-optimized config
prod_config = CANSConfig()

print("\n🏭 Production Configuration:")
print("="*27)

# Optimized for speed and reliability
prod_config.model.gnn_type = "GCN"        # Faster than GAT
prod_config.model.gnn_hidden_dim = 128    # Smaller for speed
prod_config.model.text_model = "distilbert-base-uncased"  # Faster than BERT

prod_config.training.batch_size = 128     # Larger batches for throughput
prod_config.training.epochs = 50          # Fewer epochs for faster training
prod_config.training.mixed_precision = True  # Speed optimization

# Production data settings
prod_config.data.graph_construction = "knn"  # Faster than global graphs
prod_config.data.knn_k = 5                   # Fewer connections
prod_config.data.cache_preprocessed = True   # Cache for repeated use

# Production experiment settings
prod_config.experiment.save_checkpoints = True
prod_config.experiment.log_level = "WARNING"  # Reduce logging noise
prod_config.experiment.deterministic = False  # Allow non-deterministic optimizations

# Memory optimization
prod_config.training.gradient_checkpointing = True  # Trade compute for memory
prod_config.data.lazy_loading = True                # Load data on demand

prod_config.save("production_config.json")

print(f"💾 Production config optimized for:")
print(f"   • ⚡ Speed: Smaller models, efficient architectures")
print(f"   • 🧠 Memory: Gradient checkpointing, lazy loading") 
print(f"   • 🔄 Throughput: Larger batches, reduced logging")
print(f"   • 📊 Reliability: Checkpointing, error handling")

# Compare configurations
print(f"\n📊 Configuration Comparison:")
print(f"{'Setting':<25} {'Development':<15} {'Production':<15}")
print("-" * 55)
print(f"{'GNN Type':<25} {config.model.gnn_type:<15} {prod_config.model.gnn_type:<15}")
print(f"{'Hidden Dim':<25} {config.model.gnn_hidden_dim:<15} {prod_config.model.gnn_hidden_dim:<15}")
print(f"{'Epochs':<25} {config.training.epochs:<15} {prod_config.training.epochs:<15}")
print(f"{'Batch Size':<25} {config.training.batch_size:<15} {prod_config.training.batch_size:<15}")
print(f"{'Text Model':<25} {'bert-base':<15} {'distilbert':<15}")
```

### 🎯 Key Takeaways
1. **Model architecture affects both accuracy and speed** - choose based on needs
2. **Training optimization can dramatically improve results** - tune carefully
3. **Data preprocessing is crucial** - garbage in, garbage out
4. **Production configs prioritize speed and reliability** over maximum accuracy
5. **Save configurations** for reproducibility and team collaboration

---

## Tutorial 5: API Integration

**Target Audience**: Developers building applications  
**Time**: 35 minutes  
**Prerequisites**: Basic web development knowledge

### What You'll Learn
- Set up CANS REST API server
- Build applications with CANS API client
- Handle authentication and rate limiting
- Integrate with existing systems

### Step 1: Setting Up the CANS API Server

```bash
# Install API dependencies
pip install cans-framework[api]

# Start the API server
cans-server --host 0.0.0.0 --port 8000 --workers 4

# Server will start at http://localhost:8000
# API documentation available at http://localhost:8000/docs
```

### Step 2: Python API Client Integration

```python
from cans.api.client import CANSAPIClient
import pandas as pd
import asyncio

# Initialize client
client = CANSAPIClient(
    base_url="http://localhost:8000",
    api_key="your-api-key-here"  # Get from admin
)

async def analyze_customer_campaign():
    """Example: Analyze customer email campaign effectiveness."""
    
    # Load customer data
    customers = pd.read_csv("customer_data.csv")
    
    print("🚀 Starting API-based analysis...")
    
    # Step 1: Quick validation
    validation = await client.validate_assumptions_async(
        data=customers,
        treatment_column="received_email",
        outcome_column="purchase_amount",
        feature_columns=["age", "income", "loyalty_score"]
    )
    
    if validation['causal_identification_valid']:
        print("✅ Data valid for causal analysis")
        
        # Step 2: Run complete analysis
        results = await client.complete_analysis_async(
            data=customers,
            treatment_column="received_email",
            outcome_column="purchase_amount",
            feature_columns=["age", "income", "loyalty_score"],
            experiment_name="email_campaign_q4_2024"
        )
        
        # Step 3: Extract insights
        ate = results['evaluation_results']['ate']
        ci = results['evaluation_results']['ate_confidence_interval']
        
        print(f"📊 Email Campaign Effect: ${ate:.2f}")
        print(f"🎯 95% CI: [${ci[0]:.2f}, ${ci[1]:.2f}]")
        
        return results
    else:
        print("❌ Data validation failed")
        return validation

# Run analysis
results = asyncio.run(analyze_customer_campaign())
```

### Step 3: Web Application Integration (Flask)

```python
from flask import Flask, request, jsonify, render_template
from cans.api.client import CANSAPIClient
import pandas as pd
import io

app = Flask(__name__)
client = CANSAPIClient(base_url="http://localhost:8000")

@app.route('/')
def dashboard():
    """Main dashboard for causal analysis."""
    return render_template('dashboard.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_data():
    """API endpoint for running causal analysis."""
    
    try:
        # Get uploaded file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Parse form data
        treatment_col = request.form.get('treatment_column')
        outcome_col = request.form.get('outcome_column')
        feature_cols = request.form.get('feature_columns', '').split(',')
        feature_cols = [col.strip() for col in feature_cols if col.strip()]
        
        # Load data
        df = pd.read_csv(io.StringIO(file.stream.read().decode("UTF8")))
        
        # Validate assumptions
        validation = client.validate_assumptions(
            data=df,
            treatment_column=treatment_col,
            outcome_column=outcome_col,
            feature_columns=feature_cols
        )
        
        if not validation['causal_identification_valid']:
            return jsonify({
                'status': 'validation_failed',
                'validation': validation
            })
        
        # Run analysis
        analysis = client.complete_analysis(
            data=df,
            treatment_column=treatment_col,
            outcome_column=outcome_col,
            feature_columns=feature_cols,
            model_config={'epochs': 20}  # Quick training for demo
        )
        
        # Format results for frontend
        result = {
            'status': 'success',
            'validation': validation,
            'analysis': {
                'ate': analysis['evaluation_results']['ate'],
                'confidence_interval': analysis['evaluation_results']['ate_confidence_interval'],
                'sample_size': validation['summary']['sample_size'],
                'treatment_rate': validation['summary']['treatment_rate'],
                'model_quality': analysis['evaluation_results']['factual_mse']
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    try:
        # Check if CANS API is responsive
        health = client.health_check()
        return jsonify({'status': 'healthy', 'cans_api': health})
    except:
        return jsonify({'status': 'unhealthy'}), 503

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Step 4: JavaScript Frontend Integration

```javascript
// dashboard.js - Frontend for causal analysis
class CANSAnalyzer {
    constructor(apiUrl = '/api') {
        this.apiUrl = apiUrl;
    }
    
    async analyzeFile(formData) {
        const response = await fetch(`${this.apiUrl}/analyze`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    displayResults(results) {
        const resultsDiv = document.getElementById('results');
        
        if (results.status === 'validation_failed') {
            resultsDiv.innerHTML = `
                <div class="alert alert-warning">
                    <h4>⚠️ Validation Failed</h4>
                    <p>Your data doesn't meet causal inference assumptions.</p>
                    <ul>
                        ${results.validation.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
            return;
        }
        
        const { ate, confidence_interval, sample_size, treatment_rate, model_quality } = results.analysis;
        
        resultsDiv.innerHTML = `
            <div class="alert alert-success">
                <h4>✅ Analysis Complete</h4>
                
                <div class="row">
                    <div class="col-md-6">
                        <h5>📊 Treatment Effect</h5>
                        <p class="lead">$${ate.toFixed(2)}</p>
                        <small>95% CI: [$${confidence_interval[0].toFixed(2)}, $${confidence_interval[1].toFixed(2)}]</small>
                    </div>
                    
                    <div class="col-md-6">
                        <h5>📈 Study Quality</h5>
                        <p>Sample Size: ${sample_size.toLocaleString()}</p>
                        <p>Treatment Rate: ${(treatment_rate * 100).toFixed(1)}%</p>
                        <p>Model MSE: ${model_quality.toFixed(4)}</p>
                    </div>
                </div>
                
                <div class="mt-3">
                    ${this.generateRecommendation(ate, confidence_interval)}
                </div>
            </div>
        `;
        
        // Generate chart
        this.createEffectChart(ate, confidence_interval);
    }
    
    generateRecommendation(ate, ci) {
        const isSignificant = Math.abs(ate) > Math.abs(ci[1] - ci[0]) / 4;
        
        if (isSignificant && ate > 0) {
            return `
                <div class="alert alert-success">
                    <h6>💡 Recommendation: IMPLEMENT</h6>
                    <p>Strong evidence shows positive treatment effect. Consider scaling this intervention.</p>
                </div>
            `;
        } else if (isSignificant && ate < 0) {
            return `
                <div class="alert alert-danger">
                    <h6>⛔ Recommendation: AVOID</h6>
                    <p>Evidence shows negative treatment effect. Avoid this intervention.</p>
                </div>
            `;
        } else {
            return `
                <div class="alert alert-warning">
                    <h6>🤔 Recommendation: INVESTIGATE</h6>
                    <p>Effect is not statistically significant. Consider larger sample or different approach.</p>
                </div>
            `;
        }
    }
    
    createEffectChart(ate, ci) {
        const ctx = document.getElementById('effectChart').getContext('2d');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Treatment Effect'],
                datasets: [{
                    label: 'Effect Size',
                    data: [ate],
                    backgroundColor: ate > 0 ? '#28a745' : '#dc3545',
                    borderColor: ate > 0 ? '#1e7e34' : '#bd2130',
                    borderWidth: 2
                }]
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: 'Causal Treatment Effect'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Effect Size'
                        }
                    }
                }
            }
        });
    }
}

// Initialize analyzer
const analyzer = new CANSAnalyzer();

// Handle form submission
document.getElementById('analysisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const submitBtn = document.getElementById('submitBtn');
    
    try {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Analyzing...';
        
        const results = await analyzer.analyzeFile(formData);
        analyzer.displayResults(results);
        
    } catch (error) {
        document.getElementById('results').innerHTML = `
            <div class="alert alert-danger">
                <h4>❌ Error</h4>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Run Analysis';
    }
});
```

### Step 5: REST API Direct Integration

```python
# Direct REST API calls (useful for non-Python applications)
import requests
import json

class DirectAPIClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def validate_assumptions(self, data_dict, treatment_col, outcome_col, feature_cols):
        """Direct API call for assumption validation."""
        
        payload = {
            "dataset": {
                "data": data_dict,
                "treatment_column": treatment_col,
                "outcome_column": outcome_col,
                "feature_columns": feature_cols
            },
            "verbose": True
        }
        
        response = requests.post(
            f"{self.base_url}/validate",
            headers=self.headers,
            data=json.dumps(payload, default=str)
        )
        
        response.raise_for_status()
        return response.json()
    
    def run_analysis(self, data_dict, treatment_col, outcome_col, feature_cols, config=None):
        """Direct API call for complete analysis."""
        
        payload = {
            "dataset": {
                "data": data_dict,
                "treatment_column": treatment_col,
                "outcome_column": outcome_col,
                "feature_columns": feature_cols
            },
            "model_config": config or {},
            "experiment_name": f"api_analysis_{int(time.time())}"
        }
        
        response = requests.post(
            f"{self.base_url}/analyze",
            headers=self.headers,
            data=json.dumps(payload, default=str),
            timeout=300  # 5 minutes for training
        )
        
        response.raise_for_status()
        return response.json()

# Example usage
import time
import pandas as pd

# Load data and convert to dict
df = pd.read_csv("campaign_data.csv")
data_dict = df.to_dict('records')

# Initialize client
api_client = DirectAPIClient("http://localhost:8000", "your-api-key")

# Run analysis
try:
    validation = api_client.validate_assumptions(
        data_dict=data_dict,
        treatment_col="campaign",
        outcome_col="revenue", 
        feature_cols=["age", "income", "region"]
    )
    
    if validation['causal_identification_valid']:
        results = api_client.run_analysis(
            data_dict=data_dict,
            treatment_col="campaign",
            outcome_col="revenue",
            feature_cols=["age", "income", "region"],
            config={"epochs": 25}
        )
        
        print(f"Campaign Effect: ${results['evaluation_results']['ate']:.2f}")
    
except requests.exceptions.RequestException as e:
    print(f"API Error: {e}")
```

### 🎯 Key Takeaways
1. **API enables integration with any technology stack** - not just Python
2. **Async clients provide better performance** for concurrent requests
3. **Proper error handling is crucial** in production applications
4. **Authentication and rate limiting** protect your CANS API server
5. **Real-time analysis** possible through WebSocket connections

---

## Tutorial 6: Custom Workflows

**Target Audience**: Advanced users with specific needs  
**Time**: 40 minutes  
**Prerequisites**: Tutorials 4-5 completed

### What You'll Learn
- Create custom causal analysis workflows
- Implement specialized preprocessing
- Build custom evaluation metrics
- Handle complex experimental designs

### Step 1: Custom Preprocessing Pipeline

```python
from cans.utils.data import BaseDataProcessor
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import KNNImputer

class CustomDataProcessor(BaseDataProcessor):
    """Custom preprocessing for complex experimental data."""
    
    def __init__(self, config):
        super().__init__(config)
        self.scalers = {}
        self.encoders = {}
        self.imputer = KNNImputer(n_neighbors=5)
        
    def preprocess_features(self, df, feature_columns):
        """Advanced feature preprocessing."""
        
        processed_df = df.copy()
        
        # 1. Handle categorical variables with frequency encoding
        categorical_cols = processed_df[feature_columns].select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            # Frequency encoding for high cardinality
            if processed_df[col].nunique() > 10:
                freq_map = processed_df[col].value_counts(normalize=True).to_dict()
                processed_df[f'{col}_frequency'] = processed_df[col].map(freq_map)
                feature_columns.remove(col)
                feature_columns.append(f'{col}_frequency')
            else:
                # Standard label encoding for low cardinality
                encoder = LabelEncoder()
                processed_df[col] = encoder.fit_transform(processed_df[col].astype(str))
                self.encoders[col] = encoder
        
        # 2. Create interaction features
        numerical_cols = processed_df[feature_columns].select_dtypes(include=[np.number]).columns[:3]  # Top 3
        for i, col1 in enumerate(numerical_cols):
            for col2 in numerical_cols[i+1:]:
                interaction_name = f'{col1}_x_{col2}'
                processed_df[interaction_name] = processed_df[col1] * processed_df[col2]
                feature_columns.append(interaction_name)
        
        # 3. Advanced imputation using KNN
        if processed_df[feature_columns].isnull().any().any():
            imputed_features = self.imputer.fit_transform(processed_df[feature_columns])
            processed_df[feature_columns] = imputed_features
        
        # 4. Outlier handling using IQR method
        for col in processed_df[feature_columns].select_dtypes(include=[np.number]).columns:
            Q1 = processed_df[col].quantile(0.25)
            Q3 = processed_df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Cap outliers instead of removing
            processed_df[col] = np.clip(processed_df[col], lower_bound, upper_bound)
        
        # 5. Feature scaling
        scaler = StandardScaler()
        processed_df[feature_columns] = scaler.fit_transform(processed_df[feature_columns])
        self.scalers['features'] = scaler
        
        return processed_df, feature_columns
    
    def create_temporal_features(self, df, date_column):
        """Extract temporal features for time-series experiments."""
        
        if date_column not in df.columns:
            return df, []
        
        df[date_column] = pd.to_datetime(df[date_column])
        
        temporal_features = []
        
        # Basic temporal features
        df['day_of_week'] = df[date_column].dt.dayofweek
        df['month'] = df[date_column].dt.month
        df['quarter'] = df[date_column].dt.quarter
        df['is_weekend'] = (df[date_column].dt.dayofweek >= 5).astype(int)
        
        temporal_features.extend(['day_of_week', 'month', 'quarter', 'is_weekend'])
        
        # Cyclical encoding for temporal features
        df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        temporal_features.extend(['day_of_week_sin', 'day_of_week_cos', 'month_sin', 'month_cos'])
        
        return df, temporal_features

# Usage example
def custom_preprocessing_workflow():
    """Example of custom preprocessing workflow."""
    
    # Load complex experimental data
    df = pd.read_csv("complex_experiment_data.csv")
    
    # Initialize custom processor
    from cans import CANSConfig
    config = CANSConfig()
    processor = CustomDataProcessor(config)
    
    print("🔧 Starting custom preprocessing...")
    
    # Step 1: Create temporal features if date column exists
    if 'experiment_date' in df.columns:
        df, temporal_features = processor.create_temporal_features(df, 'experiment_date')
        print(f"📅 Created {len(temporal_features)} temporal features")
    else:
        temporal_features = []
    
    # Step 2: Advanced feature preprocessing
    feature_columns = ["age", "income", "region", "product_category", "previous_purchases"]
    feature_columns.extend(temporal_features)
    
    df_processed, final_features = processor.preprocess_features(df, feature_columns)
    
    print(f"✅ Preprocessing complete:")
    print(f"   Original features: {len(feature_columns)}")
    print(f"   Final features: {len(final_features)}")
    print(f"   Shape: {df_processed.shape}")
    
    return df_processed, final_features
```

### Step 2: Custom Evaluation Metrics

```python
from cans.evaluation import BaseEvaluator
import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_curve

class CustomEvaluator(BaseEvaluator):
    """Custom evaluation for domain-specific metrics."""
    
    def __init__(self):
        super().__init__()
        
    def evaluate_policy_value(self, predictions, treatments, outcomes, costs=None):
        """Evaluate policy value with cost considerations."""
        
        mu0, mu1 = predictions[:, 0], predictions[:, 1]
        
        # Basic treatment effects
        ate = np.mean(mu1 - mu0)
        
        # Policy value: expected outcome under optimal policy
        optimal_treatments = (mu1 > mu0).astype(int)
        policy_value = np.mean(optimal_treatments * mu1 + (1 - optimal_treatments) * mu0)
        
        # Cost-adjusted policy value
        if costs is not None:
            treatment_costs = np.array(costs)
            cost_adjusted_value = policy_value - np.mean(optimal_treatments * treatment_costs)
        else:
            cost_adjusted_value = policy_value
        
        # Treatment assignment quality (how well we identify who should get treatment)
        if len(np.unique(treatments)) == 2:
            true_treatment_benefit = mu1 - mu0
            auc_score = roc_auc_score(
                (true_treatment_benefit > 0).astype(int),
                optimal_treatments
            )
        else:
            auc_score = None
        
        return {
            'ate': ate,
            'policy_value': policy_value,
            'cost_adjusted_policy_value': cost_adjusted_value,
            'treatment_assignment_auc': auc_score,
            'percent_assigned_treatment': np.mean(optimal_treatments) * 100
        }
    
    def evaluate_subgroup_effects(self, predictions, treatments, outcomes, subgroup_column, data):
        """Evaluate treatment effects by subgroups."""
        
        mu0, mu1 = predictions[:, 0], predictions[:, 1]
        subgroups = data[subgroup_column].unique()
        
        subgroup_results = {}
        
        for subgroup in subgroups:
            mask = data[subgroup_column] == subgroup
            
            if mask.sum() < 10:  # Skip small subgroups
                continue
                
            subgroup_ate = np.mean((mu1 - mu0)[mask])
            subgroup_size = mask.sum()
            
            # Statistical significance within subgroup
            subgroup_effects = (mu1 - mu0)[mask]
            std_error = np.std(subgroup_effects) / np.sqrt(len(subgroup_effects))
            
            subgroup_results[subgroup] = {
                'ate': subgroup_ate,
                'std_error': std_error,
                'sample_size': subgroup_size,
                'significant': abs(subgroup_ate) > 2 * std_error
            }
        
        return subgroup_results
    
    def evaluate_robustness(self, model, test_loader, perturbation_levels=[0.1, 0.2, 0.3]):
        """Test model robustness to input perturbations."""
        
        original_predictions = model.predict(test_loader)
        original_ate = np.mean(original_predictions[:, 1] - original_predictions[:, 0])
        
        robustness_results = {'original_ate': original_ate}
        
        for noise_level in perturbation_levels:
            # Add noise to features
            perturbed_predictions = []
            
            for batch in test_loader:
                features, treatments, outcomes = batch
                
                # Add Gaussian noise
                noise = torch.randn_like(features) * noise_level
                perturbed_features = features + noise
                
                with torch.no_grad():
                    pred = model(perturbed_features, treatments)
                    perturbed_predictions.append(pred.cpu().numpy())
            
            perturbed_predictions = np.concatenate(perturbed_predictions)
            perturbed_ate = np.mean(perturbed_predictions[:, 1] - perturbed_predictions[:, 0])
            
            ate_change = abs(perturbed_ate - original_ate) / abs(original_ate) * 100
            
            robustness_results[f'noise_{noise_level}'] = {
                'ate': perturbed_ate,
                'percent_change': ate_change,
                'robust': ate_change < 10  # Less than 10% change
            }
        
        return robustness_results

# Custom workflow with advanced evaluation
def advanced_evaluation_workflow():
    """Complete workflow with custom evaluation."""
    
    # Assume model is trained
    # model, test_loader, test_data = train_custom_model()
    
    evaluator = CustomEvaluator()
    
    print("🔍 Running advanced evaluation...")
    
    # Get predictions
    # predictions = model.predict(test_loader)
    # treatments = test_data['treatment'].values
    # outcomes = test_data['outcome'].values
    
    # Example evaluation (with dummy data)
    predictions = np.random.randn(1000, 2)  # [mu0, mu1]
    treatments = np.random.binomial(1, 0.5, 1000)
    outcomes = np.random.randn(1000)
    
    # Dummy data for subgroup analysis
    test_data = pd.DataFrame({
        'treatment': treatments,
        'outcome': outcomes,
        'age_group': np.random.choice(['young', 'middle', 'senior'], 1000),
        'region': np.random.choice(['north', 'south', 'east', 'west'], 1000)
    })
    
    # 1. Policy value evaluation
    policy_results = evaluator.evaluate_policy_value(
        predictions, treatments, outcomes,
        costs=[10, 0]  # Treatment costs $10, control costs $0
    )
    
    print("📊 Policy Evaluation Results:")
    print(f"   ATE: {policy_results['ate']:.3f}")
    print(f"   Policy Value: {policy_results['policy_value']:.3f}")
    print(f"   Cost-Adjusted Value: {policy_results['cost_adjusted_policy_value']:.3f}")
    print(f"   % Assigned Treatment: {policy_results['percent_assigned_treatment']:.1f}%")
    
    # 2. Subgroup analysis
    subgroup_results = evaluator.evaluate_subgroup_effects(
        predictions, treatments, outcomes, 'age_group', test_data
    )
    
    print("\n👥 Subgroup Analysis:")
    for group, results in subgroup_results.items():
        significance = "✅" if results['significant'] else "❌"
        print(f"   {group}: ATE={results['ate']:.3f} (n={results['sample_size']}) {significance}")
    
    return policy_results, subgroup_results
```

### Step 3: Multi-Stage Experimental Design

```python
class MultiStageExperiment:
    """Handle complex multi-stage experimental designs."""
    
    def __init__(self, config):
        self.config = config
        self.stages = []
        self.stage_results = {}
    
    def add_stage(self, name, treatment_col, outcome_col, feature_cols, 
                  selection_criteria=None, sample_ratio=1.0):
        """Add an experimental stage."""
        
        stage = {
            'name': name,
            'treatment_column': treatment_col,
            'outcome_column': outcome_col, 
            'feature_columns': feature_cols,
            'selection_criteria': selection_criteria,
            'sample_ratio': sample_ratio
        }
        
        self.stages.append(stage)
        
    def run_sequential_analysis(self, data):
        """Run analysis across multiple stages."""
        
        current_data = data.copy()
        
        for i, stage in enumerate(self.stages):
            print(f"\n🎬 Stage {i+1}: {stage['name']}")
            print("="*40)
            
            # Apply selection criteria
            if stage['selection_criteria']:
                mask = self.apply_selection_criteria(current_data, stage['selection_criteria'])
                stage_data = current_data[mask].copy()
                print(f"📊 Selected {len(stage_data)} samples from {len(current_data)}")
            else:
                stage_data = current_data.copy()
            
            # Sample if needed
            if stage['sample_ratio'] < 1.0:
                n_sample = int(len(stage_data) * stage['sample_ratio'])
                stage_data = stage_data.sample(n=n_sample, random_state=42)
                print(f"📊 Sampled {n_sample} records")
            
            # Run CANS analysis for this stage
            stage_results = self.analyze_stage(stage_data, stage)
            
            # Store results
            self.stage_results[stage['name']] = stage_results
            
            # Update data for next stage (e.g., exclude treated units)
            if i < len(self.stages) - 1:  # Not the last stage
                treated_mask = stage_data[stage['treatment_column']] == 1
                treated_ids = stage_data[treated_mask].index
                current_data = current_data.drop(treated_ids)
                print(f"📤 Removed {len(treated_ids)} treated units for next stage")
        
        return self.stage_results
    
    def apply_selection_criteria(self, data, criteria):
        """Apply selection criteria to filter data."""
        
        mask = pd.Series(True, index=data.index)
        
        for criterion in criteria:
            if criterion['type'] == 'threshold':
                col, op, value = criterion['column'], criterion['operator'], criterion['value']
                
                if op == '>':
                    mask &= data[col] > value
                elif op == '<':
                    mask &= data[col] < value
                elif op == '>=':
                    mask &= data[col] >= value
                elif op == '<=':
                    mask &= data[col] <= value
                elif op == '==':
                    mask &= data[col] == value
                    
            elif criterion['type'] == 'percentile':
                col, percentile = criterion['column'], criterion['percentile']
                threshold = data[col].quantile(percentile / 100)
                mask &= data[col] >= threshold
                
        return mask
    
    def analyze_stage(self, data, stage):
        """Run CANS analysis for a single stage."""
        
        from cans.api.client import CANSAPIClient
        
        client = CANSAPIClient(base_url="http://localhost:8000")
        
        try:
            # Validate assumptions
            validation = client.validate_assumptions(
                data=data,
                treatment_column=stage['treatment_column'],
                outcome_column=stage['outcome_column'],
                feature_columns=stage['feature_columns']
            )
            
            if not validation['causal_identification_valid']:
                return {
                    'status': 'validation_failed',
                    'validation': validation
                }
            
            # Run analysis
            analysis = client.complete_analysis(
                data=data,
                treatment_column=stage['treatment_column'],
                outcome_column=stage['outcome_column'],
                feature_columns=stage['feature_columns'],
                experiment_name=f"multi_stage_{stage['name']}"
            )
            
            return {
                'status': 'success',
                'validation': validation,
                'analysis': analysis,
                'sample_size': len(data)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_multi_stage_report(self):
        """Generate comprehensive report across all stages."""
        
        print("\n📋 Multi-Stage Experiment Report")
        print("="*35)
        
        total_effect = 0
        successful_stages = 0
        
        for stage_name, results in self.stage_results.items():
            print(f"\n🎬 Stage: {stage_name}")
            print("-"*20)
            
            if results['status'] == 'success':
                ate = results['analysis']['evaluation_results']['ate']
                sample_size = results['sample_size']
                
                print(f"✅ Status: Success")
                print(f"📊 Sample Size: {sample_size:,}")
                print(f"💰 ATE: {ate:.3f}")
                
                total_effect += ate
                successful_stages += 1
                
            elif results['status'] == 'validation_failed':
                print(f"⚠️ Status: Validation Failed")
                print(f"📋 Recommendations:")
                for rec in results['validation']['recommendations']:
                    print(f"   • {rec}")
                    
            else:
                print(f"❌ Status: Error - {results['error']}")
        
        print(f"\n🎯 Overall Results:")
        print(f"   Successful Stages: {successful_stages}/{len(self.stages)}")
        print(f"   Cumulative Effect: {total_effect:.3f}")
        print(f"   Average Effect per Stage: {total_effect/max(successful_stages,1):.3f}")

# Example multi-stage experiment
def run_multi_stage_experiment():
    """Example: Sequential marketing campaign experiment."""
    
    # Load customer data
    customers = pd.read_csv("customer_database.csv")
    
    # Initialize multi-stage experiment
    experiment = MultiStageExperiment(CANSConfig())
    
    # Stage 1: Target high-value customers with premium campaign
    experiment.add_stage(
        name="premium_campaign",
        treatment_col="received_premium_email",
        outcome_col="monthly_spend",
        feature_cols=["age", "income", "loyalty_score"],
        selection_criteria=[
            {'type': 'percentile', 'column': 'customer_lifetime_value', 'percentile': 80}
        ],
        sample_ratio=0.3
    )
    
    # Stage 2: Target remaining customers with standard campaign
    experiment.add_stage(
        name="standard_campaign", 
        treatment_col="received_standard_email",
        outcome_col="monthly_spend",
        feature_cols=["age", "income", "loyalty_score"],
        sample_ratio=0.5
    )
    
    # Stage 3: Re-engagement campaign for inactive customers
    experiment.add_stage(
        name="reengagement_campaign",
        treatment_col="received_reengagement_email", 
        outcome_col="monthly_spend",
        feature_cols=["age", "income", "loyalty_score", "days_since_purchase"],
        selection_criteria=[
            {'type': 'threshold', 'column': 'days_since_purchase', 'operator': '>', 'value': 90}
        ]
    )
    
    # Run sequential analysis
    results = experiment.run_sequential_analysis(customers)
    
    # Generate report
    experiment.generate_multi_stage_report()
    
    return results
```

### 🎯 Key Takeaways
1. **Custom preprocessing can significantly improve results** - domain knowledge matters
2. **Advanced evaluation provides deeper insights** than basic metrics
3. **Multi-stage experiments** handle complex real-world scenarios  
4. **Robustness testing** ensures reliable deployment
5. **Custom workflows** enable specialized use cases

---

## Tutorial 7: Custom Models

**Target Audience**: ML researchers and advanced practitioners  
**Time**: 45 minutes  
**Prerequisites**: Deep learning experience, PyTorch knowledge

### What You'll Learn
- Extend CANS architecture with custom components
- Implement domain-specific models
- Create custom loss functions
- Handle specialized data types

### Step 1: Custom GNN Architecture

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import MessagePassing
from cans.models.gnn_modules import BaseGNN

class MultiHeadGATLayer(MessagePassing):
    """Custom multi-head Graph Attention Network layer."""
    
    def __init__(self, in_dim, out_dim, num_heads=8, dropout=0.1, residual=True):
        super().__init__(aggr='add')
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.num_heads = num_heads
        self.residual = residual
        
        # Multi-head attention parameters
        self.W = nn.Linear(in_dim, out_dim * num_heads)
        self.a_src = nn.Parameter(torch.randn(num_heads, out_dim))
        self.a_dst = nn.Parameter(torch.randn(num_heads, out_dim))
        
        self.dropout = nn.Dropout(dropout)
        self.leaky_relu = nn.LeakyReLU(0.2)
        
        if residual:
            self.residual_linear = nn.Linear(in_dim, out_dim) if in_dim != out_dim else None
        
    def forward(self, x, edge_index):
        """Forward pass with multi-head attention."""
        
        # Linear transformation
        h = self.W(x).view(-1, self.num_heads, self.out_dim)  # [N, heads, out_dim]
        
        # Propagate messages
        out = self.propagate(edge_index, x=h)  # [N, heads, out_dim]
        
        # Average across heads
        out = out.mean(dim=1)  # [N, out_dim]
        
        # Residual connection
        if self.residual:
            if self.residual_linear is not None:
                residual = self.residual_linear(x)
            else:
                residual = x
            out = out + residual
        
        return out
    
    def message(self, x_i, x_j, edge_index_i, edge_index_j):
        """Compute attention-weighted messages."""
        
        # Attention scores
        alpha = (x_i * self.a_src).sum(dim=-1) + (x_j * self.a_dst).sum(dim=-1)  # [E, heads]
        alpha = self.leaky_relu(alpha)
        
        # Apply dropout to attention scores
        alpha = self.dropout(alpha)
        
        # Attention-weighted messages
        return alpha.unsqueeze(-1) * x_j  # [E, heads, out_dim]
    
    def aggregate(self, inputs, index):
        """Aggregate messages with softmax attention."""
        
        # Softmax normalization per node
        alpha = inputs.sum(dim=-1)  # [E, heads]
        alpha = F.softmax(alpha, dim=0)
        
        # Apply attention weights
        return (alpha.unsqueeze(-1) * inputs).sum(dim=0)  # [N, heads, out_dim]

class HierarchicalGNN(BaseGNN):
    """Custom hierarchical GNN for complex causal structures."""
    
    def __init__(self, in_dim, hidden_dim, output_dim, num_layers=3, num_heads=8):
        super().__init__(in_dim, hidden_dim, output_dim)
        
        self.num_layers = num_layers
        self.layers = nn.ModuleList()
        self.norms = nn.ModuleList()
        
        # Input layer
        self.layers.append(
            MultiHeadGATLayer(in_dim, hidden_dim, num_heads, dropout=0.1)
        )
        self.norms.append(nn.LayerNorm(hidden_dim))
        
        # Hidden layers
        for _ in range(num_layers - 2):
            self.layers.append(
                MultiHeadGATLayer(hidden_dim, hidden_dim, num_heads, dropout=0.1)
            )
            self.norms.append(nn.LayerNorm(hidden_dim))
        
        # Output layer
        self.layers.append(
            MultiHeadGATLayer(hidden_dim, output_dim, num_heads=1, dropout=0.0)
        )
        self.norms.append(nn.LayerNorm(output_dim))
        
        # Hierarchical pooling
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.local_pool = nn.AdaptiveMaxPool1d(1)
        
    def forward(self, x, edge_index, batch=None):
        """Hierarchical forward pass."""
        
        # Store intermediate representations
        representations = [x]
        
        # Forward through layers
        for i, (layer, norm) in enumerate(zip(self.layers, self.norms)):
            x = layer(x, edge_index)
            x = norm(x)
            
            if i < len(self.layers) - 1:  # Not the last layer
                x = F.relu(x)
                x = F.dropout(x, training=self.training)
            
            representations.append(x)
        
        # Hierarchical aggregation
        if batch is not None:
            # Graph-level representations
            graph_reps = []
            for rep in representations[1:]:  # Skip input
                global_rep = torch_geometric.nn.global_mean_pool(rep, batch)
                local_rep = torch_geometric.nn.global_max_pool(rep, batch)
                graph_reps.append(torch.cat([global_rep, local_rep], dim=1))
            
            # Combine hierarchical representations
            final_rep = torch.cat(graph_reps, dim=1)
            return final_rep
        
        return x
    
    def num_parameters(self):
        """Count number of parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

# Usage example
def create_custom_gnn():
    """Create and test custom GNN."""
    
    # Model parameters
    in_dim = 64
    hidden_dim = 256
    output_dim = 128
    
    # Create custom GNN
    gnn = HierarchicalGNN(
        in_dim=in_dim,
        hidden_dim=hidden_dim,
        output_dim=output_dim,
        num_layers=4,
        num_heads=8
    )
    
    print(f"🧠 Custom GNN created:")
    print(f"   Parameters: {gnn.num_parameters():,}")
    print(f"   Architecture: Hierarchical GAT")
    print(f"   Layers: 4 with 8 attention heads")
    
    return gnn
```

### Step 2: Specialized Text Encoders

```python
from transformers import AutoModel, AutoConfig
import torch.nn as nn

class ClinicalBERTEncoder(nn.Module):
    """Specialized BERT encoder for clinical/medical text."""
    
    def __init__(self, model_name="emilyalsentzer/Bio_ClinicalBERT", max_length=512):
        super().__init__()
        
        self.max_length = max_length
        
        # Load clinical BERT
        config = AutoConfig.from_pretrained(model_name)
        config.attention_probs_dropout_prob = 0.1
        config.hidden_dropout_prob = 0.1
        
        self.bert = AutoModel.from_pretrained(model_name, config=config)
        
        # Clinical-specific layers
        hidden_size = self.bert.config.hidden_size
        
        # Medical entity attention
        self.entity_attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=8,
            dropout=0.1
        )
        
        # Clinical domain projection
        self.clinical_projection = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size, hidden_size)
        )
        
    def forward(self, input_ids, attention_mask=None):
        """Forward pass with clinical specialization."""
        
        # Get BERT representations
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True
        )
        
        # Sequence representations
        sequence_output = outputs.last_hidden_state  # [batch, seq_len, hidden]
        pooled_output = outputs.pooler_output        # [batch, hidden]
        
        # Apply entity attention
        attended_output, attention_weights = self.entity_attention(
            sequence_output.transpose(0, 1),  # [seq_len, batch, hidden]
            sequence_output.transpose(0, 1),
            sequence_output.transpose(0, 1),
            key_padding_mask=~attention_mask.bool() if attention_mask is not None else None
        )
        
        # Pool attended representations
        if attention_mask is not None:
            attended_pooled = (attended_output.transpose(0, 1) * attention_mask.unsqueeze(-1)).sum(1) / attention_mask.sum(1, keepdim=True)
        else:
            attended_pooled = attended_output.mean(0)
        
        # Clinical domain projection
        clinical_features = self.clinical_projection(attended_pooled)
        
        # Combine representations
        final_representation = pooled_output + clinical_features
        
        return {
            'pooled_output': final_representation,
            'sequence_output': sequence_output,
            'attention_weights': attention_weights
        }

class MultiModalEncoder(nn.Module):
    """Multi-modal encoder for text + numerical features."""
    
    def __init__(self, text_encoder, numerical_dim, fusion_dim=512):
        super().__init__()
        
        self.text_encoder = text_encoder
        self.numerical_dim = numerical_dim
        self.fusion_dim = fusion_dim
        
        # Numerical feature processing
        self.numerical_encoder = nn.Sequential(
            nn.Linear(numerical_dim, fusion_dim // 2),
            nn.ReLU(),
            nn.BatchNorm1d(fusion_dim // 2),
            nn.Dropout(0.1),
            nn.Linear(fusion_dim // 2, fusion_dim // 2)
        )
        
        # Cross-modal attention
        text_hidden = text_encoder.bert.config.hidden_size
        
        self.cross_attention = nn.MultiheadAttention(
            embed_dim=fusion_dim,
            num_heads=8,
            dropout=0.1
        )
        
        # Projection layers
        self.text_proj = nn.Linear(text_hidden, fusion_dim)
        self.numerical_proj = nn.Linear(fusion_dim // 2, fusion_dim)
        
        # Final fusion
        self.fusion_layer = nn.Sequential(
            nn.Linear(fusion_dim * 2, fusion_dim),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(fusion_dim, fusion_dim)
        )
        
    def forward(self, text_inputs, numerical_features):
        """Multi-modal forward pass."""
        
        # Encode text
        text_outputs = self.text_encoder(**text_inputs)
        text_features = self.text_proj(text_outputs['pooled_output'])
        
        # Encode numerical features
        numerical_features = self.numerical_encoder(numerical_features)
        numerical_features = self.numerical_proj(numerical_features)
        
        # Cross-modal attention
        text_query = text_features.unsqueeze(0)  # [1, batch, dim]
        num_key_value = numerical_features.unsqueeze(0)  # [1, batch, dim]
        
        attended_text, _ = self.cross_attention(text_query, num_key_value, num_key_value)
        attended_text = attended_text.squeeze(0)  # [batch, dim]
        
        # Combine modalities
        combined = torch.cat([attended_text, numerical_features], dim=1)
        fused_features = self.fusion_layer(combined)
        
        return fused_features
```

### Step 3: Custom Loss Functions

```python
class CausalLossWithUncertainty(nn.Module):
    """Custom causal loss with uncertainty quantification."""
    
    def __init__(self, alpha=1.0, beta=0.5, gamma=0.1, uncertainty_weight=0.1):
        super().__init__()
        self.alpha = alpha  # Factual loss weight
        self.beta = beta    # IPW loss weight  
        self.gamma = gamma  # Balancing loss weight
        self.uncertainty_weight = uncertainty_weight
        
    def forward(self, predictions, targets, treatments, propensity_scores, 
                uncertainty_estimates=None):
        """
        Custom causal loss with uncertainty.
        
        Args:
            predictions: [batch_size, 2] - [mu0, mu1] predictions
            targets: [batch_size] - actual outcomes
            treatments: [batch_size] - treatment indicators
            propensity_scores: [batch_size] - propensity scores
            uncertainty_estimates: [batch_size, 2] - uncertainty for [mu0, mu1]
        """
        
        mu0, mu1 = predictions[:, 0], predictions[:, 1]
        
        # 1. Factual loss (standard MSE for observed outcomes)
        treated_mask = treatments == 1
        control_mask = treatments == 0
        
        factual_loss = 0
        if treated_mask.any():
            factual_loss += F.mse_loss(mu1[treated_mask], targets[treated_mask])
        if control_mask.any():
            factual_loss += F.mse_loss(mu0[control_mask], targets[control_mask])
        
        # 2. IPW loss (inverse propensity weighted)
        ipw_weights_treated = 1.0 / (propensity_scores + 1e-8)
        ipw_weights_control = 1.0 / (1.0 - propensity_scores + 1e-8)
        
        ipw_loss = 0
        if treated_mask.any():
            ipw_loss += (ipw_weights_treated[treated_mask] * 
                        F.mse_loss(mu1[treated_mask], targets[treated_mask], reduction='none')).mean()
        if control_mask.any():
            ipw_loss += (ipw_weights_control[control_mask] * 
                        F.mse_loss(mu0[control_mask], targets[control_mask], reduction='none')).mean()
        
        # 3. Representation balancing loss
        treated_representation = predictions[treated_mask].mean(0) if treated_mask.any() else torch.zeros(2, device=predictions.device)
        control_representation = predictions[control_mask].mean(0) if control_mask.any() else torch.zeros(2, device=predictions.device)
        
        balancing_loss = F.mse_loss(treated_representation, control_representation)
        
        # 4. Uncertainty regularization
        uncertainty_loss = 0
        if uncertainty_estimates is not None:
            # Penalize high uncertainty on observed outcomes
            if treated_mask.any():
                uncertainty_loss += uncertainty_estimates[treated_mask, 1].mean()
            if control_mask.any():
                uncertainty_loss += uncertainty_estimates[control_mask, 0].mean()
        
        # Total loss
        total_loss = (self.alpha * factual_loss + 
                     self.beta * ipw_loss + 
                     self.gamma * balancing_loss +
                     self.uncertainty_weight * uncertainty_loss)
        
        return {
            'total_loss': total_loss,
            'factual_loss': factual_loss,
            'ipw_loss': ipw_loss,
            'balancing_loss': balancing_loss,
            'uncertainty_loss': uncertainty_loss
        }

class AdversarialCausalLoss(nn.Module):
    """Adversarial training for robust causal inference."""
    
    def __init__(self, base_loss_fn, discriminator_weight=0.1):
        super().__init__()
        self.base_loss_fn = base_loss_fn
        self.discriminator_weight = discriminator_weight
        
        # Treatment discriminator
        self.discriminator = nn.Sequential(
            nn.Linear(256, 128),  # Assuming 256-dim representations
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 64),
            nn.ReLU(), 
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
    def forward(self, predictions, targets, treatments, propensity_scores, 
                representations):
        """
        Adversarial causal loss.
        
        Args:
            representations: [batch_size, repr_dim] - learned representations
        """
        
        # Base causal loss
        base_losses = self.base_loss_fn(predictions, targets, treatments, propensity_scores)
        
        # Discriminator loss (can the discriminator predict treatment from representation?)
        treatment_probs = self.discriminator(representations)
        discriminator_loss = F.binary_cross_entropy(
            treatment_probs.squeeze(), 
            treatments.float()
        )
        
        # Adversarial loss (we want to fool the discriminator)
        adversarial_loss = -discriminator_loss
        
        total_loss = base_losses['total_loss'] + self.discriminator_weight * adversarial_loss
        
        return {
            **base_losses,
            'total_loss': total_loss,
            'discriminator_loss': discriminator_loss,
            'adversarial_loss': adversarial_loss
        }
```

### Step 4: Custom CANS Model

```python
from cans.models.cans_model import BaseCANS

class AdvancedCANS(BaseCANS):
    """Advanced CANS with custom components."""
    
    def __init__(self, gnn, text_encoder, numerical_dim, fusion_dim=512, 
                 num_treatments=2, uncertainty_estimation=True):
        super().__init__()
        
        self.gnn = gnn
        self.text_encoder = text_encoder
        self.numerical_dim = numerical_dim
        self.fusion_dim = fusion_dim
        self.num_treatments = num_treatments
        self.uncertainty_estimation = uncertainty_estimation
        
        # Multi-modal fusion
        self.multi_modal_encoder = MultiModalEncoder(
            text_encoder, numerical_dim, fusion_dim
        )
        
        # Treatment effect heads
        self.outcome_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(fusion_dim * 2, fusion_dim),  # GNN + text features
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(fusion_dim, fusion_dim // 2),
                nn.ReLU(),
                nn.Linear(fusion_dim // 2, 1)
            ) for _ in range(num_treatments)
        ])
        
        # Uncertainty estimation heads (if enabled)
        if uncertainty_estimation:
            self.uncertainty_heads = nn.ModuleList([
                nn.Sequential(
                    nn.Linear(fusion_dim * 2, fusion_dim // 2),
                    nn.ReLU(),
                    nn.Linear(fusion_dim // 2, 1),
                    nn.Softplus()  # Ensure positive uncertainty
                ) for _ in range(num_treatments)
            ])
        
        # Propensity score estimation
        self.propensity_head = nn.Sequential(
            nn.Linear(fusion_dim * 2, fusion_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(fusion_dim, 1),
            nn.Sigmoid()
        )
        
    def forward(self, batch):
        """Advanced forward pass."""
        
        # Unpack batch
        graph_data, text_inputs, numerical_features, treatments = batch
        
        # GNN encoding
        gnn_features = self.gnn(
            graph_data.x, 
            graph_data.edge_index,
            graph_data.batch
        )
        
        # Multi-modal text + numerical encoding
        multimodal_features = self.multi_modal_encoder(text_inputs, numerical_features)
        
        # Combine GNN and multi-modal features
        combined_features = torch.cat([gnn_features, multimodal_features], dim=1)
        
        # Predict outcomes for each treatment
        mu_predictions = []
        uncertainty_predictions = []
        
        for i, head in enumerate(self.outcome_heads):
            mu = head(combined_features)
            mu_predictions.append(mu)
            
            if self.uncertainty_estimation:
                sigma = self.uncertainty_heads[i](combined_features)
                uncertainty_predictions.append(sigma)
        
        outcomes = torch.cat(mu_predictions, dim=1)  # [batch_size, num_treatments]
        
        # Propensity score estimation
        propensity_scores = self.propensity_head(combined_features).squeeze(1)
        
        result = {
            'outcomes': outcomes,
            'propensity_scores': propensity_scores,
            'representations': combined_features
        }
        
        if self.uncertainty_estimation:
            uncertainties = torch.cat(uncertainty_predictions, dim=1)
            result['uncertainties'] = uncertainties
        
        return result
    
    def predict_with_uncertainty(self, batch, num_samples=100):
        """Monte Carlo prediction with uncertainty."""
        
        if not self.uncertainty_estimation:
            return self.forward(batch)
        
        # Enable dropout for MC sampling
        self.train()
        
        predictions = []
        for _ in range(num_samples):
            with torch.no_grad():
                pred = self.forward(batch)
                predictions.append(pred['outcomes'])
        
        # Back to eval mode
        self.eval()
        
        # Calculate statistics
        predictions = torch.stack(predictions)  # [samples, batch_size, num_treatments]
        
        mean_prediction = predictions.mean(0)
        std_prediction = predictions.std(0)
        
        return {
            'outcomes': mean_prediction,
            'uncertainties': std_prediction,
            'propensity_scores': pred['propensity_scores'],  # Use last prediction
            'representations': pred['representations']
        }

# Complete training example
def train_advanced_cans():
    """Train advanced CANS model."""
    
    # Create components
    gnn = HierarchicalGNN(in_dim=64, hidden_dim=256, output_dim=256)
    text_encoder = ClinicalBERTEncoder()
    
    # Create advanced model
    model = AdvancedCANS(
        gnn=gnn,
        text_encoder=text_encoder,
        numerical_dim=32,
        fusion_dim=512,
        uncertainty_estimation=True
    )
    
    print(f"🏗️ Advanced CANS Model:")
    print(f"   Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"   GNN: Hierarchical GAT")
    print(f"   Text: Clinical BERT")
    print(f"   Uncertainty: Enabled")
    
    # Custom loss function
    base_loss = CausalLossWithUncertainty(
        alpha=1.0, beta=0.5, gamma=0.1, uncertainty_weight=0.1
    )
    loss_fn = AdversarialCausalLoss(base_loss, discriminator_weight=0.05)
    
    # Optimizer with different learning rates
    optimizer = torch.optim.AdamW([
        {'params': model.gnn.parameters(), 'lr': 0.001},
        {'params': model.text_encoder.parameters(), 'lr': 0.0001},  # Lower LR for pre-trained
        {'params': model.multi_modal_encoder.parameters(), 'lr': 0.001},
        {'params': model.outcome_heads.parameters(), 'lr': 0.001},
        {'params': model.propensity_head.parameters(), 'lr': 0.001},
    ], weight_decay=0.01)
    
    return model, loss_fn, optimizer
```

### 🎯 Key Takeaways
1. **Custom architectures** enable domain-specific improvements
2. **Multi-modal fusion** handles complex real-world data  
3. **Uncertainty quantification** provides reliability estimates
4. **Adversarial training** improves robustness
5. **Modular design** allows mixing and matching components

---

## Tutorial 8: Production Deployment

**Target Audience**: DevOps engineers and platform developers  
**Time**: 50 minutes  
**Prerequisites**: Docker, Kubernetes, cloud platform knowledge

### What You'll Learn
- Deploy CANS API servers at scale
- Set up monitoring and logging
- Handle model updates and versioning
- Implement CI/CD pipelines

[Tutorial content continues with deployment specifics...]

---

## Tutorial 9: LLM Integration

**Target Audience**: AI application developers  
**Time**: 35 minutes  
**Prerequisites**: LLM usage experience

### What You'll Learn
- Set up MCP server for LLM integration
- Create natural language causal analysis workflows
- Build AI agents that use CANS
- Handle complex multi-turn conversations

[Tutorial content continues with LLM integration...]

---

## Tutorial 10: Healthcare Applications

**Target Audience**: Healthcare data scientists  
**Time**: 40 minutes  
**Prerequisites**: Healthcare domain knowledge

### What You'll Learn
- Analyze clinical trial data
- Handle medical text and coding systems
- Ensure privacy and compliance
- Validate medical causal claims

[Tutorial content continues with healthcare examples...]

---

## Tutorial 11: Marketing Analytics

**Target Audience**: Marketing analysts and data scientists  
**Time**: 35 minutes  
**Prerequisites**: Marketing domain knowledge

### What You'll Learn
- Measure campaign effectiveness
- Optimize marketing spend allocation
- Handle attribution modeling
- A/B test analysis and optimization

[Tutorial content continues with marketing examples...]

---

## Tutorial 12: Financial Analysis

**Target Audience**: Financial analysts and quants  
**Time**: 45 minutes  
**Prerequisites**: Finance domain knowledge

### What You'll Learn
- Risk factor analysis
- Policy impact assessment
- Market intervention effects
- Regulatory compliance considerations

[Tutorial content continues with financial examples...]

---

**🎓 Ready to master CANS?** Work through these tutorials at your own pace and become a causal inference expert!