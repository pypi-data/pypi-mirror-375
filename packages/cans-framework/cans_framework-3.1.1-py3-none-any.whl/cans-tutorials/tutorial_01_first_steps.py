#!/usr/bin/env python3
"""
CANS Framework - Tutorial 1: First Steps with CANS

Target Audience: Complete beginners
Time: 15 minutes
Prerequisites: Basic Python knowledge

This tutorial will teach you:
- Install CANS framework
- Understand causal inference basics
- Run your first causal analysis
"""

import sys
import pandas as pd
import numpy as np

def print_header():
    """Print tutorial header."""
    print("🎓 CANS Tutorial 1: First Steps with CANS")
    print("=" * 45)
    print("⏱️  Estimated time: 15 minutes")
    print("🎯 Learning goals: Installation, basics, first analysis")
    print()

def check_installation():
    """Check if CANS is properly installed."""
    print("📦 Step 1: Checking CANS Installation")
    print("-" * 35)
    
    try:
        import cans
        print(f"✅ CANS Framework v{cans.__version__} installed successfully!")
        
        # Check key components
        from cans import validate_causal_assumptions, CANSConfig
        print("✅ Core components available")
        
        # Check CLI tools
        import subprocess
        result = subprocess.run(['cans', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CLI tools working")
        else:
            print("⚠️  CLI tools may not be in PATH")
            
    except ImportError as e:
        print(f"❌ CANS not installed: {e}")
        print("💡 Install with: pip install cans-framework")
        return False
    
    print("✅ Installation check complete!\n")
    return True

def explain_causal_inference():
    """Explain causal inference concepts."""
    print("🧠 Step 2: Understanding Causal Inference")
    print("-" * 40)
    
    print("What is Causal Inference?")
    print("• Causal inference answers 'what if' questions")
    print("• What if we give this treatment to patients?")
    print("• What if we change our marketing strategy?")
    print("• What if we implement this policy?")
    print()
    
    print("Key Concepts:")
    print("• Treatment: The intervention you want to study (e.g., medication, ad campaign)")
    print("• Outcome: What you want to measure (e.g., recovery rate, sales)")  
    print("• Confounders: Other factors that might affect both treatment and outcome")
    print()
    
    print("CANS Architecture:")
    print("Data Input → [GNN + BERT] → Fusion Layer → CFRNet → Treatment Effects")
    print()

def create_sample_data():
    """Create sample marketing data for analysis."""
    print("📊 Step 3: Creating Sample Data")
    print("-" * 30)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    n = 1000
    
    print(f"Creating sample marketing dataset with {n} customers...")
    
    data = {
        'customer_id': range(1, n+1),
        'age': np.random.normal(35, 10, n),
        'income': np.random.normal(50000, 15000, n),
        'email_campaign': np.random.binomial(1, 0.4, n),  # Treatment: 40% get emails
        'monthly_spend': np.random.normal(200, 50, n)     # Outcome: monthly spending
    }
    
    # Add treatment effect (people who got emails spend more)
    for i in range(n):
        if data['email_campaign'][i] == 1:
            data['monthly_spend'][i] += 30  # $30 campaign effect
    
    df = pd.DataFrame(data)
    
    print("✅ Sample data created!")
    print(f"📊 Dataset shape: {df.shape}")
    print(f"📈 Campaign rate: {df['email_campaign'].mean():.1%}")
    print("\nFirst 5 rows:")
    print(df.head())
    print()
    
    return df

def validate_assumptions(df):
    """Validate causal assumptions."""
    print("🔍 Step 4: Validating Causal Assumptions")
    print("-" * 40)
    
    try:
        from cans import validate_causal_assumptions
        
        print("Running assumption validation...")
        
        results = validate_causal_assumptions(
            X=df[['age', 'income']].values,
            T=df['email_campaign'].values,
            Y=df['monthly_spend'].values
        )
        
        print(f"🔍 Causal assumptions valid: {results['causal_identification_valid']}")
        
        if results['causal_identification_valid']:
            print("✅ Great! Your data is suitable for causal analysis")
        else:
            print("⚠️  Warning: Some assumptions may not be met")
        
        print()
        return results
        
    except ImportError:
        print("⚠️  Validation function not available, continuing with basic analysis...")
        return {'causal_identification_valid': True}

def calculate_treatment_effect(df):
    """Calculate simple treatment effect."""
    print("📈 Step 5: Calculating Treatment Effect")
    print("-" * 38)
    
    treated = df[df['email_campaign'] == 1]['monthly_spend']
    control = df[df['email_campaign'] == 0]['monthly_spend']
    
    effect = treated.mean() - control.mean()
    
    print(f"📊 Campaign Effect: ${effect:.2f}")
    print(f"💰 Treated group spends: ${treated.mean():.2f}")
    print(f"💰 Control group spends: ${control.mean():.2f}")
    print()
    
    # Business interpretation
    if effect > 10:
        print("🎉 Strong positive effect! Consider scaling the campaign.")
    elif effect > 0:
        print("✅ Positive effect detected. Campaign appears beneficial.")
    elif effect < -10:
        print("⚠️  Strong negative effect. Consider stopping the campaign.")
    else:
        print("🤔 Effect is small or unclear. May need more data or analysis.")
    
    print()
    return effect

def key_takeaways():
    """Print key takeaways."""
    print("🎯 Key Takeaways")
    print("-" * 16)
    print("1. Always validate assumptions first - this ensures reliable results")
    print("2. Treatment effect = Treated average - Control average (in simple cases)")  
    print("3. CANS validates your analysis to ensure scientific rigor")
    print("4. Causal inference helps make better decisions with data")
    print()

def whats_next():
    """Show next steps."""
    print("📚 What's Next?")
    print("-" * 15)
    print("• Tutorial 2: Learn to analyze your own data files")
    print("• Tutorial 3: Use CANS advanced features for better results")
    print("• Tutorial 4: Advanced configuration and model customization")
    print()
    print("Run: python tutorial_02_data_understanding.py")
    print()

def main():
    """Run the complete tutorial."""
    print_header()
    
    # Check installation
    if not check_installation():
        return
    
    # Explain concepts
    explain_causal_inference()
    
    # Create sample data
    df = create_sample_data()
    
    # Validate assumptions
    validation_results = validate_assumptions(df)
    
    # Calculate treatment effect
    effect = calculate_treatment_effect(df)
    
    # Summary
    key_takeaways()
    whats_next()
    
    print("✅ Tutorial 1 Complete!")
    print("🎓 You've learned the basics of CANS and causal inference!")

if __name__ == "__main__":
    main()