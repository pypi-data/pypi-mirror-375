"""
CANS Framework Tutorial System

This module provides tutorial installation and management capabilities.
After installing CANS, users can run `cans-tutorials` to set up interactive tutorials.
"""

import os
import shutil
import argparse
import sys
from pathlib import Path
from typing import Optional

__version__ = "3.1.0"

def get_tutorials_source_path() -> Path:
    """Get the path to tutorials in the installed package."""
    package_dir = Path(__file__).parent.parent
    return package_dir / "tutorials"

def setup_tutorials(target_dir: Optional[str] = None) -> None:
    """
    Set up CANS tutorials in a target directory.
    
    Args:
        target_dir: Target directory path. If None, uses current directory + 'cans-tutorials'
    """
    if target_dir is None:
        target_dir = os.path.join(os.getcwd(), "cans-tutorials")
    
    target_path = Path(target_dir)
    
    print(f"🎓 Setting up CANS tutorials in: {target_path}")
    
    # Check if directory exists
    if target_path.exists():
        response = input(f"Directory {target_path} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return
        shutil.rmtree(target_path)
    
    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Copy tutorial files from package
        source_path = get_tutorials_source_path()
        
        if not source_path.exists():
            print(f"❌ Error: Tutorial source path not found: {source_path}")
            return
            
        # Copy all tutorial files
        for item in source_path.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(source_path)
                target_file = target_path / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target_file)
        
        # Create a welcome file
        welcome_content = f"""# 🎓 Welcome to CANS Framework Tutorials!

You've successfully set up the CANS tutorial environment.

## 📚 Available Tutorials

### Beginner Level (15-25 minutes each)
1. **tutorial_01_first_steps.py** - Get started with CANS basics
2. **tutorial_02_data_understanding.py** - Learn data preparation
3. **tutorial_03_first_analysis.py** - Run your first causal analysis

### Intermediate Level (30-40 minutes each)
4. **tutorial_04_advanced_config.py** - Custom model configuration
5. **tutorial_05_api_integration.py** - API and web integration
6. **tutorial_06_custom_workflows.py** - Advanced workflow patterns

### Advanced Level (45+ minutes each)
7. **tutorial_07_custom_models.py** - Build custom architectures
8. **tutorial_08_production_deployment.py** - Deploy at scale
9. **tutorial_09_llm_integration.py** - LLM and AI agent integration

### Domain-Specific Tutorials
10. **tutorial_10_healthcare.py** - Medical and clinical applications
11. **tutorial_11_marketing.py** - Marketing analytics and A/B testing
12. **tutorial_12_finance.py** - Financial analysis and risk modeling

## 🚀 Getting Started

1. **Install dependencies** (if you haven't already):
   ```bash
   pip install cans-framework[all]
   ```

2. **Start with Tutorial 1**:
   ```bash
   python tutorial_01_first_steps.py
   ```

3. **Or open in Jupyter**:
   ```bash
   jupyter lab tutorial_01_first_steps.ipynb
   ```

## 📖 Documentation

- **Main Documentation**: See TUTORIALS.md for comprehensive guide
- **API Reference**: Check API_GUIDE.md for REST API details  
- **LLM Integration**: See LLM_USAGE_GUIDE.md for AI assistant setup
- **Deployment**: Read DEPLOYMENT_GUIDE.md for production deployment

## 💡 Need Help?

- **GitHub Issues**: https://github.com/rdmurugan/cans-framework/issues
- **Email Support**: durai@infinidatum.net
- **Documentation**: https://github.com/rdmurugan/cans-framework

## 📋 Tutorial Progress Tracking

Create a file called `tutorial_progress.txt` to track your completion:

```
✅ Tutorial 1: First Steps - Completed
✅ Tutorial 2: Data Understanding - Completed  
🔄 Tutorial 3: First Analysis - In Progress
⏳ Tutorial 4: Advanced Config - Not Started
...
```

Happy learning! 🚀

---
CANS Framework v{__version__} - Causal Adaptive Neural System
"""
        
        welcome_file = target_path / "README.md"
        welcome_file.write_text(welcome_content)
        
        print(f"✅ Tutorials successfully set up in: {target_path}")
        print(f"📚 Found {len(list(target_path.rglob('*.py')))} Python tutorial files")
        print(f"📖 Found {len(list(target_path.rglob('*.md')))} documentation files")
        print()
        print("🚀 Next steps:")
        print(f"   1. cd {target_path}")
        print(f"   2. python tutorial_01_first_steps.py")
        print(f"   3. Or: jupyter lab tutorial_01_first_steps.ipynb")
        
    except Exception as e:
        print(f"❌ Error setting up tutorials: {e}")
        if target_path.exists():
            shutil.rmtree(target_path)

def list_tutorials() -> None:
    """List available tutorials."""
    print("🎓 Available CANS Framework Tutorials:")
    print("=" * 40)
    
    tutorials = [
        ("1", "First Steps with CANS", "Beginner", "15 min"),
        ("2", "Understanding Your Data", "Beginner", "20 min"),  
        ("3", "Running Your First Analysis", "Beginner", "25 min"),
        ("4", "Advanced Configuration", "Intermediate", "30 min"),
        ("5", "API Integration", "Intermediate", "35 min"),
        ("6", "Custom Workflows", "Intermediate", "40 min"),
        ("7", "Custom Models", "Advanced", "45 min"),
        ("8", "Production Deployment", "Advanced", "50 min"),
        ("9", "LLM Integration", "Advanced", "35 min"),
        ("10", "Healthcare Applications", "Domain", "40 min"),
        ("11", "Marketing Analytics", "Domain", "35 min"),
        ("12", "Financial Analysis", "Domain", "45 min"),
    ]
    
    for num, title, level, duration in tutorials:
        level_icon = "🟢" if level == "Beginner" else "🟡" if level == "Intermediate" else "🔴" if level == "Advanced" else "🔵"
        print(f"  {level_icon} Tutorial {num:2}: {title:<30} ({level}, {duration})")
    
    print()
    print("Run 'cans-tutorials' to set up interactive tutorials in your workspace!")

def main():
    """Main CLI entry point for tutorial setup."""
    parser = argparse.ArgumentParser(
        description="CANS Framework Tutorial Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cans-tutorials                    # Set up in ./cans-tutorials/
  cans-tutorials --dir my-tutorials # Set up in ./my-tutorials/
  cans-tutorials --list            # List available tutorials
  cans-tutorials --help            # Show this help
        """
    )
    
    parser.add_argument(
        "--dir", "-d", 
        type=str, 
        help="Target directory for tutorials (default: ./cans-tutorials/)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available tutorials"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version", 
        version=f"CANS Framework Tutorials v{__version__}"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_tutorials()
    else:
        setup_tutorials(args.dir)

if __name__ == "__main__":
    main()