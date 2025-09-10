# 🧠 CANS: Causal Adaptive Neural System

> **Production-ready causal inference at scale with deep learning, APIs, and LLM integration**

**CANS (Causal Adaptive Neural System)** is the most comprehensive **production-ready framework** for **causal inference** using deep learning. It combines **Graph Neural Networks (GNNs)**, **Transformers**, **Counterfactual Regression Networks (CFRNet)**, and **advanced causal methods** with enterprise-grade **APIs** and **LLM integration**.

🎯 **Perfect for**: Healthcare, Finance, Marketing, Legal, Social Media, E-commerce, and any domain requiring **rigorous causal analysis**

## 🌟 What Makes CANS Unique

- 🧠 **Hybrid AI Architecture**: GNNs + Transformers + CFRNet for complex data
- 🔬 **Rigorous Causal Science**: Automated assumption testing, multiple identification strategies
- 🌐 **Production APIs**: REST API + MCP server for seamless integration
- 🤖 **LLM Integration**: Enable AI assistants to perform causal analysis autonomously
- ⚡ **Enterprise Ready**: Authentication, monitoring, scalable deployment
- 📊 **Comprehensive Toolkit**: CLI, Python API, web integration, notebooks

## 🚀 Choose Your Interface

| Interface | Best For | Getting Started |
|-----------|----------|-----------------|
| 🖥️ **CLI Tools** | Quick analysis, data scientists | `cans-validate --data data.csv --treatment T --outcome Y` |
| 🐍 **Python API** | Research, notebooks, pipelines | `from cans import CANS, validate_causal_assumptions` |
| 🌐 **REST API** | Web apps, microservices | `POST /validate` → JSON response |
| 🤖 **MCP Server** | LLMs, AI assistants | Claude/GPT calls `validate_causal_assumptions_tool` |

## 📊 Usage Matrix

| Task | CLI | Python | REST API | MCP/LLM |
|------|-----|--------|----------|---------|
| **Assumption Validation** | `cans-validate` | `validate_causal_assumptions()` | `POST /validate` | `validate_causal_assumptions_tool` |
| **Complete Analysis** | `cans-analyze` | `CANSRunner.fit()` | `POST /analyze` | `quick_causal_analysis` |
| **Model Evaluation** | `cans-evaluate` | `CausalEvaluator.evaluate()` | `POST /evaluate` | `evaluate_predictions` |
| **Batch Processing** | Shell scripting | `for` loops | HTTP requests | LLM automation |
| **Production Deployment** | Cron jobs | Python services | Kubernetes | AI workflows |

## 🚀 What's New in v3.0 - Production-Ready Causal AI

### 🔬 Advanced Causal Methods
- **Assumption Testing**: Automated unconfoundedness, positivity, and SUTVA validation
- **Multiple Identification**: Backdoor criterion, IPW, doubly robust estimation
- **CATE Estimation**: X-Learner, T-Learner, S-Learner, Neural CATE, Causal Forest
- **Uncertainty Quantification**: Bayesian methods, ensemble approaches, conformal prediction

### 🌐 Enterprise Integration
- **REST API**: Complete HTTP API with authentication and rate limiting
- **MCP Server**: Model Context Protocol for seamless LLM integration
- **Production Tools**: Docker, Kubernetes, monitoring, logging
- **Multi-language**: Python, JavaScript, R, cURL examples

### 🧠 Enhanced AI Architecture
- **Advanced Graph Construction**: Multi-node, temporal, and global architectures
- **Causal-Specific Losses**: CFR, IPW, DragonNet, TARNet with representation balancing
- **Memory Efficiency**: Lazy loading and batch processing for large datasets
- **GPU Optimization**: CUDA support with automatic device selection

### Previous v2.0 Features:
- 🔧 **Configuration Management**: Centralized, validated configs with JSON/YAML support
- 🛡️ **Enhanced Error Handling**: Comprehensive validation with informative error messages  
- 📊 **Logging & Checkpointing**: Built-in experiment tracking with automatic model saving
- 🧪 **Comprehensive Testing**: 100+ unit tests ensuring production reliability
- 📈 **Advanced Data Pipeline**: Multi-format loading (CSV, JSON) with automatic preprocessing
- ⚡ **Enhanced Training**: Early stopping, gradient clipping, multiple loss functions

## 🔧 Key Features

### Core Architecture
- ✅ **Hybrid Neural Architecture**: GNNs + Transformers + CFRNet for multi-modal causal inference
- ✅ **Gated Fusion Layer**: Adaptive mixing of graph and textual representations
- ✅ **Flexible Graph Construction**: Single-node, multi-node, temporal, and global graphs
- ✅ **Production-Ready**: Comprehensive error handling, logging, and testing

### Causal Inference Capabilities  
- ✅ **Rigorous Assumption Testing**: Automated validation of causal identification conditions
- ✅ **Multiple Identification Methods**: Backdoor, IPW, doubly robust, with sensitivity analysis
- ✅ **Heterogeneous Treatment Effects**: CATE estimation with 5+ methods (X/T/S-Learners, etc.)
- ✅ **Advanced Loss Functions**: CFR, DragonNet, TARNet with representation balancing
- ✅ **Uncertainty Quantification**: Bayesian, ensemble, conformal prediction approaches

### Data Processing & Evaluation
- ✅ **Smart Data Loading**: CSV, JSON, synthetic data with automatic graph construction
- ✅ **Comprehensive Evaluation**: PEHE, ATE, policy value, calibration metrics
- ✅ **Memory Efficiency**: Lazy loading, batch processing for large-scale datasets
- ✅ **Easy Configuration**: JSON/YAML configs with validation and experiment tracking



## 🏗️ Architecture

```
 +-----------+     +-----------+
 |  GNN Emb  |     |  BERT Emb |
 +-----------+     +-----------+
        \             /
         \ Fusion Layer /
          \     /
         +-----------+
         |  Fused Rep |
         +-----------+
               |
           CFRNet
        /          \
   mu_0(x)       mu_1(x)
```

## 🚀 Enhanced Causal Analysis Workflow

### Complete Example with Assumption Testing & CATE Estimation

```python
from cans import (
    CANSConfig, CANS, GCN, CANSRunner,
    create_sample_dataset, get_data_loaders,
    CausalAssumptionTester, CausalLossManager, 
    CATEManager, UncertaintyManager,
    advanced_counterfactual_analysis
)

# 1. Configuration with enhanced causal features
config = CANSConfig()
config.model.gnn_type = "GCN"
config.training.loss_type = "cfr"  # Causal loss function
config.data.graph_construction = "global"  # Multi-node graphs

# 2. Test causal assumptions BEFORE modeling
assumption_tester = CausalAssumptionTester()
results = assumption_tester.comprehensive_test(X, T, Y)
print(f"Causal assumptions valid: {results['causal_identification_valid']}")

# 3. Create datasets with enhanced graph construction
datasets = create_sample_dataset(n_samples=1000, config=config.data)
train_loader, val_loader, test_loader = get_data_loaders(datasets)

# 4. Setup model with causal loss functions
from transformers import BertModel
gnn = GCN(in_dim=64, hidden_dim=128, output_dim=256)
bert = BertModel.from_pretrained("distilbert-base-uncased")
model = CANS(gnn, bert, fusion_dim=256)

loss_manager = CausalLossManager("cfr", alpha=1.0, beta=0.5)

# 5. Train with causal-aware pipeline
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
runner = CANSRunner(model, optimizer, config)
history = runner.fit(train_loader, val_loader)

# 6. Multiple counterfactual identification methods
cf_results = advanced_counterfactual_analysis(
    model, test_loader, 
    methods=['backdoor', 'ipw', 'doubly_robust']
)

# 7. CATE estimation with multiple learners
cate_manager = CATEManager(method="x_learner")
cate_manager.fit(X, T, Y)
individual_effects = cate_manager.estimate_cate(X_test)

# 8. Uncertainty quantification
uncertainty_manager = UncertaintyManager(method="conformal")
uncertainty_manager.setup(model)
intervals = uncertainty_manager.estimate_uncertainty(test_loader)

print(f"ATE: {cf_results['backdoor']['ate']:.3f}")
print(f"Coverage: {intervals['coverage_rate']:.3f}")
```

## 🚀 Quick Start

> 🎯 **New to CANS?** Start with our [**Getting Started Guide**](GETTING_STARTED.md) for a 5-minute tutorial!

### Installation

```bash
# Install from PyPI (Recommended)  
pip install cans-framework

# Verify installation
cans --version
```

### Alternative Installation Methods

```bash
# Development installation
git clone https://github.com/rdmurugan/cans-framework.git
cd cans-framework
pip install -r requirements.txt
pip install -e .

# With conda (for dependency management)
conda create -n cans python=3.9
conda activate cans
pip install cans-framework
```

**Core Dependencies:**
- `torch>=2.0.0`
- `transformers>=4.38.0`
- `torch-geometric>=2.3.0`
- `scikit-learn>=1.3.0`
- `pandas>=2.0.0`

### Basic Usage (30 seconds to results)

```python
from cans.config import CANSConfig
from cans.utils.data import create_sample_dataset, get_data_loaders
from cans.models import CANS
from cans.models.gnn_modules import GCN
from cans.pipeline.runner import CANSRunner
from transformers import BertModel
import torch

# 1. Create configuration
config = CANSConfig()
config.training.epochs = 10

# 2. Load data (or create sample data)
datasets = create_sample_dataset(n_samples=1000, n_features=64)
train_loader, val_loader, test_loader = get_data_loaders(datasets, batch_size=32)

# 3. Create model
gnn = GCN(in_dim=64, hidden_dim=128, output_dim=256)
bert = BertModel.from_pretrained("bert-base-uncased")
model = CANS(gnn, bert, fusion_dim=256)

# 4. Train
optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
runner = CANSRunner(model, optimizer, config)
history = runner.fit(train_loader, val_loader)

# 5. Evaluate
results = runner.evaluate(test_loader)
print(f"Test MSE: {results['mse']:.4f}")
print(f"Average Treatment Effect: {results['ate']:.4f}")
```

## 🖥️ Command Line Interface (CLI)

CANS provides three powerful CLI commands for quick causal analysis:

> 💡 **New to CANS?** Check out our comprehensive [User Guide](USER_GUIDE.md) for step-by-step tutorials, troubleshooting, and best practices!

### 1. Validate Causal Assumptions (`cans-validate`)

Test critical causal assumptions before modeling:

```bash
# Basic usage
cans-validate --data data.csv --treatment intervention --outcome conversion_rate

# Specify features explicitly  
cans-validate --data marketing_data.csv \
              --treatment campaign_type \
              --outcome revenue \
              --features age,income,education,region \
              --output validation_results.json \
              --verbose

# Example output:
# {
#   "unconfoundedness_test": {
#     "valid": true,
#     "p_value": 0.23,
#     "method": "backdoor_criterion"
#   },
#   "positivity_test": {
#     "valid": true,
#     "overlap_score": 0.85,
#     "min_propensity": 0.05
#   },
#   "sutva_test": {
#     "valid": true,
#     "interference_score": 0.02
#   }
# }
```

### 2. Evaluate Model Performance (`cans-evaluate`)

Assess causal model predictions:

```bash
# Evaluate predictions file with columns: mu0, mu1, treatments, outcomes
cans-evaluate --predictions model_predictions.csv --format json

# Save detailed evaluation report
cans-evaluate --predictions predictions.csv \
              --output evaluation_report.txt \
              --format text

# Example output metrics:
# - Average Treatment Effect (ATE): 2.34 ± 0.18
# - Factual MSE: 0.045
# - PEHE (Precision in Estimation of Heterogeneous Effects): 0.12
# - Individual Treatment Effect R²: 0.73
```

### 3. Complete Causal Analysis (`cans-analyze`)

Run end-to-end causal inference workflow:

```bash
# Quick analysis with default configuration
cans-analyze --data patient_data.csv --output-dir results/

# Use custom configuration
cans-analyze --data social_media.csv \
             --config custom_config.json \
             --output-dir social_analysis/

# Creates structured output:
# results/
# ├── assumptions_validation.json
# ├── model_performance.json  
# ├── causal_effects_summary.json
# ├── individual_effects.csv
# └── analysis_report.html
```

### CLI Configuration Files

Create reusable configuration files for complex analyses:

```json
{
  "model": {
    "gnn_type": "GCN",
    "gnn_hidden_dim": 128,
    "fusion_dim": 256,
    "text_model": "distilbert-base-uncased"
  },
  "training": {
    "learning_rate": 0.001,
    "batch_size": 64,
    "epochs": 50,
    "loss_type": "cfr"
  },
  "data": {
    "graph_construction": "knn",
    "knn_k": 5,
    "scale_node_features": true
  }
}
```

## 📊 Usage Examples

### Example 1: CSV Data with Real Causal Inference

```python
from cans.utils.data import load_csv_dataset
from cans.config import CANSConfig, DataConfig

# Configure data processing
config = CANSConfig()
config.data.graph_construction = "knn"  # or "similarity" 
config.data.knn_k = 5
config.data.scale_node_features = True

# Load your CSV data
datasets = load_csv_dataset(
    csv_path="your_data.csv",
    text_column="review_text",        # Column with text data
    treatment_column="intervention",   # Binary treatment (0/1)
    outcome_column="conversion_rate",  # Continuous outcome  
    feature_columns=["age", "income", "education"],  # Numerical features
    config=config.data
)

train_dataset, val_dataset, test_dataset = datasets

# Check data quality
stats = train_dataset.get_statistics()
print(f"Treatment proportion: {stats['treatment_proportion']:.3f}")
print(f"Propensity overlap valid: {stats['propensity_overlap_valid']}")
```

### Example 2: Advanced Configuration & Experiment Tracking

```python
from cans.config import CANSConfig

# Create detailed configuration
config = CANSConfig()

# Model configuration
config.model.gnn_type = "GCN"
config.model.gnn_hidden_dim = 256
config.model.fusion_dim = 512
config.model.text_model = "distilbert-base-uncased"  # Faster BERT variant

# Training configuration  
config.training.learning_rate = 0.001
config.training.batch_size = 64
config.training.epochs = 50
config.training.early_stopping_patience = 10
config.training.gradient_clip_norm = 1.0
config.training.loss_type = "huber"  # Robust to outliers

# Experiment tracking
config.experiment.experiment_name = "healthcare_causal_analysis"
config.experiment.save_every_n_epochs = 5
config.experiment.log_level = "INFO"

# Save configuration for reproducibility
config.save("experiment_config.json")

# Later: load and use
loaded_config = CANSConfig.load("experiment_config.json")
```

### Example 3: Counterfactual Analysis & Treatment Effects

```python
from cans.utils.causal import simulate_counterfactual
import numpy as np

# After training your model...
runner = CANSRunner(model, optimizer, config)
runner.fit(train_loader, val_loader)

# Comprehensive evaluation
test_metrics = runner.evaluate(test_loader)
print("Performance Metrics:")
for metric, value in test_metrics.items():
    print(f"  {metric}: {value:.4f}")

# Counterfactual analysis
cf_control = simulate_counterfactual(model, test_loader, intervention=0)
cf_treatment = simulate_counterfactual(model, test_loader, intervention=1)

# Calculate causal effects
ate = np.mean(cf_treatment) - np.mean(cf_control)
print(f"\nCausal Analysis:")
print(f"Average Treatment Effect (ATE): {ate:.4f}")
print(f"Expected outcome under control: {np.mean(cf_control):.4f}")
print(f"Expected outcome under treatment: {np.mean(cf_treatment):.4f}")

# Individual treatment effects
individual_effects = np.array(cf_treatment) - np.array(cf_control)
print(f"Treatment effect std: {np.std(individual_effects):.4f}")
print(f"% benefiting from treatment: {(individual_effects > 0).mean()*100:.1f}%")
```

### Example 4: Custom Data Pipeline

```python
from cans.utils.preprocessing import DataPreprocessor, GraphBuilder
from cans.config import DataConfig
import pandas as pd

# Custom preprocessing pipeline
config = DataConfig()
config.graph_construction = "similarity"
config.similarity_threshold = 0.7
config.scale_node_features = True

preprocessor = DataPreprocessor(config)

# Process your DataFrame  
df = pd.read_csv("social_media_posts.csv")
dataset = preprocessor.process_tabular_data(
    data=df,
    text_column="post_content",
    treatment_column="fact_check_label",
    outcome_column="share_count",
    feature_columns=["user_followers", "post_length", "sentiment_score"],
    text_model="bert-base-uncased",
    max_text_length=256
)

# Split with custom ratios
train_ds, val_ds, test_ds = preprocessor.split_dataset(
    dataset, 
    train_size=0.7, 
    val_size=0.2, 
    test_size=0.1
)
```

## 🧪 Testing & Development

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories  
pytest tests/test_models.py -v        # Model tests
pytest tests/test_validation.py -v    # Validation tests
pytest tests/test_pipeline.py -v      # Training pipeline tests

# Run with coverage
pytest tests/ --cov=cans --cov-report=html

# Run example scripts
python examples/enhanced_usage_example.py
python examples/enhanced_causal_analysis_example.py
```


## 📁 Framework Structure

```
cans-framework/
├── cans/
│   ├── __init__.py              # Main imports
│   ├── config.py                # ✨ Configuration management
│   ├── exceptions.py            # ✨ Custom exceptions
│   ├── validation.py            # ✨ Data validation utilities
│   ├── models/
│   │   ├── cans.py             # Core CANS model (enhanced)
│   │   └── gnn_modules.py      # GNN implementations
│   ├── pipeline/
│   │   └── runner.py           # ✨ Enhanced training pipeline
│   └── utils/
│       ├── causal.py           # Counterfactual simulation
│       ├── data.py             # ✨ Enhanced data loading
│       ├── preprocessing.py     # ✨ Advanced preprocessing
│       ├── logging.py          # ✨ Structured logging
│       └── checkpointing.py    # ✨ Model checkpointing
├── tests/                       # ✨ Comprehensive test suite
├── examples/                    # Usage examples
└── CLAUDE.md                   # Development guide
```
**✨ = New/Enhanced in v2.0**

## 🎯 Use Cases & Applications

### Healthcare & Medical
```python
# Analyze treatment effectiveness with patient records + clinical notes
datasets = load_csv_dataset(
    csv_path="patient_outcomes.csv",
    text_column="clinical_notes",
    treatment_column="medication_type", 
    outcome_column="recovery_score",
    feature_columns=["age", "bmi", "comorbidities"]
)
```

### Marketing & A/B Testing  
```python
# Marketing campaign effectiveness with customer profiles + ad content
datasets = load_csv_dataset(
    csv_path="campaign_data.csv", 
    text_column="ad_content",
    treatment_column="campaign_variant",
    outcome_column="conversion_rate",
    feature_columns=["customer_ltv", "demographics", "behavior_score"]
)
```

### Social Media & Content Moderation
```python  
# Impact of content moderation on engagement
datasets = load_csv_dataset(
    csv_path="posts_data.csv",
    text_column="post_text", 
    treatment_column="moderation_action",
    outcome_column="engagement_score",
    feature_columns=["user_followers", "post_length", "sentiment"]
)
```

## 🔬 Research & Methodology

CANS implements state-of-the-art causal inference techniques:

- **Counterfactual Regression Networks (CFRNet)**: Learn representations that minimize treatment assignment bias
- **Gated Fusion**: Adaptively combine graph-structured and textual information  
- **Balanced Representation**: Minimize distributional differences between treatment groups
- **Propensity Score Validation**: Automatic overlap checking for reliable causal estimates

**Key Papers:**
- Shalit et al. "Estimating individual treatment effect: generalization bounds and algorithms" (ICML 2017)
- Yao et al. "Representation learning for treatment effect estimation from observational data" (NeurIPS 2018)

## 🚀 Performance & Scalability

- **Memory Efficient**: Optimized batch processing and gradient checkpointing
- **GPU Acceleration**: Full CUDA support with automatic device selection
- **Parallel Processing**: Multi-core data loading and preprocessing
- **Production Ready**: Comprehensive error handling and logging

**Benchmarks** (approximate, hardware-dependent):
- **Small**: 1K samples, 32 features → ~30 sec training  
- **Medium**: 100K samples, 128 features → ~10 min training
- **Large**: 1M+ samples → Scales with batch size and hardware

## 🌐 API & Integration

CANS provides comprehensive API access for integration with web applications, services, and AI systems:

### REST API Server
```bash
# Start REST API server
cans-server
# or
uvicorn cans.api.server:app --host 0.0.0.0 --port 8000

# Interactive docs at: http://localhost:8000/docs
```

### MCP Server for LLMs
```bash
# Start MCP server for LLM integration
cans-mcp
# Enables LLMs to directly perform causal analysis
```

### Python API Client
```python
from cans.api.client import CANSAPIClient

client = CANSAPIClient(api_key="your-key")
results = client.validate_assumptions(
    data="data.csv",
    treatment_column="treatment",
    outcome_column="outcome"
)
```

**🔗 API Features:**
- RESTful endpoints for all CANS functionality
- Model Context Protocol (MCP) server for LLM integration
- Authentication and rate limiting
- Async/await support
- Comprehensive error handling
- Interactive documentation

**📖 Learn More:** [API Guide](API_GUIDE.md)

## 📚 Documentation & Resources

### 📚 Documentation Hierarchy

1. **[Getting Started](GETTING_STARTED.md)** - 5-minute quickstart tutorial
2. **[User Guide](USER_GUIDE.md)** - Comprehensive guide with tutorials, best practices, and FAQ  
3. **[API Guide](API_GUIDE.md)** - Complete API integration guide with examples
4. **[README](README.md)** - This file with complete feature overview
5. **[Examples](examples/)** - Real-world use cases and workflows
6. **[Changelog](CHANGELOG.md)** - Version history and updates

### 🔧 For Developers
- **[Tests](tests/)** - 100+ unit tests and usage patterns
- **[Configuration](pyproject.toml)** - Project setup and dependencies
- **API Reference** - In-code documentation with detailed docstrings

### 🆘 Getting Help
- **First time?** → [Getting Started Guide](GETTING_STARTED.md)
- **Need detailed help?** → [User Guide](USER_GUIDE.md) with FAQ and troubleshooting
- **Found a bug?** → [GitHub Issues](https://github.com/rdmurugan/cans-framework/issues)
- **Have questions?** → Email durai@infinidatum.net

## 🤝 Contributing

Contributions welcome! Please:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Add tests** for new functionality  
4. **Run tests**: `pytest tests/ -v`
5. **Submit** a pull request

Areas we'd love help with:
- Additional GNN architectures (GraphSAGE, Graph Transformers)
- More evaluation metrics for causal inference
- Integration with popular ML platforms (MLflow, Weights & Biases)
- Performance optimizations

## 👨‍🔬 Authors

**Durai Rajamanickam** – [@duraimuruganr](https://github.com/rdmurugan)
reach out to durai@infinidatum.net

## 📜 License

MIT License. Free to use, modify, and distribute with attribution.

---

**Ready to get started?** Try the 30-second quick start above, or dive into the detailed examples! 🚀

