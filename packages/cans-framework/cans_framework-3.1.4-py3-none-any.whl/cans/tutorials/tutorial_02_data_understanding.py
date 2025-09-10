#!/usr/bin/env python3
"""
CANS Framework - Tutorial 2: Understanding Your Data

Target Audience: Beginners with own datasets
Time: 20 minutes
Prerequisites: Tutorial 1 completed

This tutorial will teach you:
- Prepare real data for CANS
- Understand data quality requirements
- Handle common data issues
"""

import pandas as pd
import numpy as np
from pathlib import Path

def print_header():
    """Print tutorial header."""
    print("🎓 CANS Tutorial 2: Understanding Your Data")
    print("=" * 45)
    print("⏱️  Estimated time: 20 minutes")
    print("🎯 Learning goals: Data preparation, quality checks, issue handling")
    print()

def create_sample_datasets():
    """Create various sample datasets for practice."""
    print("📊 Step 1: Creating Practice Datasets")
    print("-" * 35)
    
    # Dataset 1: Clean marketing data
    np.random.seed(42)
    n = 1500
    
    clean_data = {
        'customer_id': range(1, n+1),
        'age': np.random.normal(35, 12, n).astype(int),
        'income': np.random.normal(55000, 18000, n),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n),
        'email_campaign': np.random.binomial(1, 0.45, n),
        'conversion_rate': np.random.beta(2, 5, n)
    }
    
    # Add treatment effect
    for i in range(n):
        if clean_data['email_campaign'][i] == 1:
            clean_data['conversion_rate'][i] += 0.05
    
    clean_df = pd.DataFrame(clean_data)
    
    # Dataset 2: Messy real-world data
    messy_data = clean_data.copy()
    
    # Add missing values
    missing_indices = np.random.choice(n, size=int(0.1 * n), replace=False)
    for idx in missing_indices[:50]:
        messy_data['income'][idx] = np.nan
    for idx in missing_indices[50:]:
        messy_data['region'][idx] = None
    
    # Add outliers
    outlier_indices = np.random.choice(n, size=20, replace=False)
    for idx in outlier_indices:
        messy_data['income'][idx] = np.random.choice([5000, 500000])  # Extreme values
    
    # Add inconsistent categories
    region_typos = ['NORTH', 'north', 'N', 'Northern', 'South', 'SOUTH', 'E', 'Eastern']
    typo_indices = np.random.choice(n, size=30, replace=False)
    for idx in typo_indices:
        messy_data['region'][idx] = np.random.choice(region_typos)
    
    messy_df = pd.DataFrame(messy_data)
    
    print("✅ Created two practice datasets:")
    print(f"   📈 Clean dataset: {clean_df.shape}")
    print(f"   🔧 Messy dataset: {messy_df.shape} (with real-world issues)")
    print()
    
    return clean_df, messy_df

def data_quality_checker(df, treatment_col, outcome_col, name="Dataset"):
    """Comprehensive data quality check."""
    print(f"🔍 Step 2: Data Quality Report - {name}")
    print("-" * 50)
    
    # Basic info
    print(f"📊 Sample size: {len(df):,}")
    print(f"📝 Number of features: {len(df.columns)}")
    
    # Missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"⚠️  Missing values found:")
        for col, count in missing[missing > 0].items():
            print(f"   • {col}: {count} ({count/len(df)*100:.1f}%)")
    else:
        print("✅ No missing values")
    
    # Treatment column check
    if treatment_col in df.columns:
        unique_treatments = df[treatment_col].unique()
        print(f"🎯 Treatment '{treatment_col}':")
        print(f"   • Values: {unique_treatments}")
        
        if len(unique_treatments) == 2 and set([0, 1]).issubset(set(unique_treatments)):
            print("   • ✅ Binary treatment (0/1) - perfect!")
            treatment_rate = df[treatment_col].mean()
            print(f"   • Treatment rate: {treatment_rate:.1%}")
            
            if 0.05 <= treatment_rate <= 0.95:
                print("   • ✅ Good treatment balance")
            else:
                print("   • ⚠️  Imbalanced treatment groups")
        else:
            print("   • ⚠️  Treatment should be binary (0/1)")
    else:
        print(f"❌ Treatment column '{treatment_col}' not found")
    
    # Outcome column check
    if outcome_col in df.columns:
        print(f"📈 Outcome '{outcome_col}':")
        if df[outcome_col].dtype in ['int64', 'float64']:
            print(f"   • ✅ Numerical outcome")
            print(f"   • Range: {df[outcome_col].min():.2f} to {df[outcome_col].max():.2f}")
            print(f"   • Mean: {df[outcome_col].mean():.2f}")
            
            # Check for extreme outliers
            Q1 = df[outcome_col].quantile(0.25)
            Q3 = df[outcome_col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[outcome_col] < Q1 - 3*IQR) | (df[outcome_col] > Q3 + 3*IQR)).sum()
            if outliers > 0:
                print(f"   • ⚠️  {outliers} extreme outliers detected")
            else:
                print("   • ✅ No extreme outliers")
                
        else:
            print("   • ⚠️  Outcome should be numerical")
    else:
        print(f"❌ Outcome column '{outcome_col}' not found")
    
    # Feature columns analysis
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    feature_cols = [col for col in numeric_cols 
                   if col not in [treatment_col, outcome_col, 'customer_id']]
    
    print(f"🔢 Available features:")
    print(f"   • Numerical: {len(feature_cols)}")
    print(f"   • Categorical: {len(categorical_cols) - (1 if treatment_col in categorical_cols else 0)}")
    
    if len(feature_cols) >= 3:
        print("   • ✅ Good number of features for analysis")
    else:
        print("   • ⚠️  Consider adding more features to control for confounding")
    
    # Categorical variable cardinality check
    for col in categorical_cols:
        if col != treatment_col:
            unique_count = df[col].nunique()
            if unique_count > 50:
                print(f"   • ⚠️  {col} has {unique_count} categories (consider grouping)")
    
    print()
    return {
        'ready_for_analysis': (
            treatment_col in df.columns and 
            outcome_col in df.columns and
            len(feature_cols) >= 1 and
            missing.sum() == 0
        ),
        'feature_columns': feature_cols,
        'issues': missing.sum()
    }

def fix_common_issues(df, treatment_col, outcome_col):
    """Fix common data preparation issues."""
    print("🔧 Step 3: Fixing Common Data Issues")
    print("-" * 35)
    
    df_fixed = df.copy()
    
    # Fix 1: Handle missing values
    missing_before = df_fixed.isnull().sum().sum()
    if missing_before > 0:
        print(f"📝 Handling {missing_before} missing values...")
        
        # Fill numerical columns with median
        numeric_cols = df_fixed.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            if df_fixed[col].isnull().any():
                median_val = df_fixed[col].median()
                df_fixed[col].fillna(median_val, inplace=True)
        
        # Fill categorical columns with mode
        cat_cols = df_fixed.select_dtypes(include=['object']).columns
        for col in cat_cols:
            if df_fixed[col].isnull().any():
                mode_val = df_fixed[col].mode()[0] if not df_fixed[col].mode().empty else 'Unknown'
                df_fixed[col].fillna(mode_val, inplace=True)
        
        print(f"   ✅ Fixed {missing_before} missing values")
    
    # Fix 2: Standardize categorical variables
    if 'region' in df_fixed.columns:
        print("📝 Standardizing categorical variables...")
        
        # Clean region names
        region_mapping = {
            'NORTH': 'North', 'north': 'North', 'N': 'North', 'Northern': 'North',
            'SOUTH': 'South', 'south': 'South', 'S': 'South', 'Southern': 'South', 
            'EAST': 'East', 'east': 'East', 'E': 'East', 'Eastern': 'East',
            'WEST': 'West', 'west': 'West', 'W': 'West', 'Western': 'West'
        }
        
        before_unique = df_fixed['region'].nunique()
        df_fixed['region'] = df_fixed['region'].replace(region_mapping)
        after_unique = df_fixed['region'].nunique()
        
        print(f"   ✅ Standardized categories: {before_unique} → {after_unique} unique values")
    
    # Fix 3: Handle extreme outliers (cap at 1st and 99th percentiles)
    if outcome_col in df_fixed.columns:
        print("📝 Handling extreme outliers...")
        
        before_outliers = ((df_fixed[outcome_col] < df_fixed[outcome_col].quantile(0.01)) | 
                          (df_fixed[outcome_col] > df_fixed[outcome_col].quantile(0.99))).sum()
        
        if before_outliers > 0:
            lower_cap = df_fixed[outcome_col].quantile(0.01)
            upper_cap = df_fixed[outcome_col].quantile(0.99)
            df_fixed[outcome_col] = df_fixed[outcome_col].clip(lower=lower_cap, upper=upper_cap)
            print(f"   ✅ Capped {before_outliers} extreme outliers")
    
    # Fix 4: Convert treatment to binary if needed
    if treatment_col in df_fixed.columns:
        unique_vals = df_fixed[treatment_col].unique()
        
        if len(unique_vals) == 2 and not set([0, 1]).issubset(set(unique_vals)):
            print(f"📝 Converting treatment to 0/1...")
            val_map = {unique_vals[0]: 0, unique_vals[1]: 1}
            df_fixed[treatment_col] = df_fixed[treatment_col].map(val_map)
            print(f"   ✅ Converted {unique_vals[0]}→0, {unique_vals[1]}→1")
    
    print(f"\n✅ Data cleaning complete!")
    print(f"📊 Final dataset: {len(df_fixed)} rows, {len(df_fixed.columns)} columns")
    
    return df_fixed

def demonstrate_workflow():
    """Demonstrate complete data preparation workflow."""
    print("🔄 Step 4: Complete Data Preparation Workflow")
    print("-" * 45)
    
    # Create sample datasets
    clean_df, messy_df = create_sample_datasets()
    
    # Analysis 1: Clean dataset
    print("Analysis 1: Clean Dataset")
    clean_report = data_quality_checker(clean_df, 'email_campaign', 'conversion_rate', "Clean")
    
    if clean_report['ready_for_analysis']:
        print("✅ Clean dataset is ready for analysis!\n")
    
    # Analysis 2: Messy dataset - before cleaning
    print("Analysis 2: Messy Dataset (Before Cleaning)")
    messy_report = data_quality_checker(messy_df, 'email_campaign', 'conversion_rate', "Messy (Before)")
    
    if not messy_report['ready_for_analysis']:
        print("❌ Messy dataset needs cleaning first\n")
        
        # Clean the messy dataset
        cleaned_df = fix_common_issues(messy_df, 'email_campaign', 'conversion_rate')
        
        # Re-analyze after cleaning
        print("Analysis 3: Messy Dataset (After Cleaning)")
        final_report = data_quality_checker(cleaned_df, 'email_campaign', 'conversion_rate', "Messy (After)")
        
        if final_report['ready_for_analysis']:
            print("✅ Now ready for causal analysis!")
    
    print()

def data_preparation_checklist():
    """Show data preparation checklist."""
    print("📋 Data Preparation Checklist")
    print("-" * 30)
    
    checklist = [
        "✅ Treatment column exists and is binary (0/1)",
        "✅ Outcome column is numerical", 
        "✅ No missing values in critical columns",
        "✅ At least 3-5 feature columns for confounders",
        "✅ Sample size > 1000 (recommended)",
        "✅ Treatment balance between 10-90%",
        "✅ Outliers identified and handled",
        "✅ Categorical variables properly encoded",
        "✅ Data types are correct",
        "✅ Column names are consistent"
    ]
    
    for item in checklist:
        print(f"   {item}")
    
    print()

def key_takeaways():
    """Print key takeaways."""
    print("🎯 Key Takeaways")
    print("-" * 16)
    print("1. Data quality is crucial - bad data leads to unreliable results")
    print("2. Binary treatments (0/1) work best with CANS")
    print("3. More features = better confounder control") 
    print("4. Always check your data before analysis")
    print("5. Missing values and outliers need careful handling")
    print("6. Standardize categorical variables for consistency")
    print()

def whats_next():
    """Show next steps."""
    print("📚 What's Next?")
    print("-" * 15)
    print("• Tutorial 3: Run advanced CANS analysis with your prepared data")
    print("• Tutorial 4: Learn advanced configuration and model customization")
    print()
    print("Run: python tutorial_03_first_analysis.py")
    print()

def main():
    """Run the complete tutorial."""
    print_header()
    
    # Demonstrate workflow
    demonstrate_workflow()
    
    # Show checklist
    data_preparation_checklist()
    
    # Summary
    key_takeaways()
    whats_next()
    
    print("✅ Tutorial 2 Complete!")
    print("🎓 You now understand how to prepare data for causal analysis!")

if __name__ == "__main__":
    main()