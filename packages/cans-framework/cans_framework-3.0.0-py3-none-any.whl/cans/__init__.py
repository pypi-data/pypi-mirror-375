"""
CANS: Causal Adaptive Neural System

A production-ready deep learning framework for causal inference on structured,
textual, and heterogeneous data. Seamlessly integrates Graph Neural Networks,
Transformers, and Counterfactual Regression Networks.

Key Features:
- Rigorous causal assumption testing
- Multiple identification strategies (Backdoor, IPW, Doubly Robust)
- CATE estimation with 5+ methods
- Uncertainty quantification approaches
- Advanced graph construction methods
- Causal-specific loss functions
"""

__version__ = "3.0.0"
__author__ = "Durai Rajamanickam"
__email__ = "durai@infinidatum.net"
__license__ = "MIT"

# Core imports
from .models import CANS
from .models.gnn_modules import GCN, GAT
from .models.cate_models import CATEManager, XLearner, TLearner, SLearner
from .pipeline import CANSRunner
from .config import CANSConfig

# Data utilities
from .utils.data import (
    load_pheme_graphs, 
    load_csv_dataset, 
    create_sample_dataset,
    get_data_loaders
)

# Causal inference
from .utils.causal import (
    simulate_counterfactual, 
    CounterfactualSimulator, 
    advanced_counterfactual_analysis
)

# Assumption testing
from .utils.causal_assumptions import (
    CausalAssumptionTester, 
    validate_causal_assumptions
)

# Loss functions
from .utils.causal_losses import (
    CausalLossManager, 
    CFRLoss, 
    IPWLoss, 
    DoublyRobustLoss,
    TARNetLoss,
    DragonNetLoss
)

# Evaluation
from .utils.causal_evaluation import (
    CausalEvaluator, 
    CausalMetrics,
    bootstrap_ate_confidence_interval,
    permutation_test_ate
)

# Uncertainty quantification
from .utils.uncertainty import (
    UncertaintyManager, 
    ConformalPredictor, 
    EnsembleCANS,
    BayesianCANS,
    UncertaintyCalibrator,
    evaluate_uncertainty_quality
)

__all__ = [
    # Version and metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # Core models
    "CANS", 
    "GCN", 
    "GAT",
    
    # CATE estimation
    "CATEManager", 
    "XLearner", 
    "TLearner", 
    "SLearner",
    
    # Training and pipeline
    "CANSRunner",
    
    # Configuration
    "CANSConfig",
    
    # Data utilities
    "load_pheme_graphs", 
    "load_csv_dataset", 
    "create_sample_dataset",
    "get_data_loaders",
    
    # Causal inference
    "simulate_counterfactual", 
    "CounterfactualSimulator", 
    "advanced_counterfactual_analysis",
    
    # Assumption testing
    "CausalAssumptionTester", 
    "validate_causal_assumptions",
    
    # Loss functions
    "CausalLossManager", 
    "CFRLoss", 
    "IPWLoss", 
    "DoublyRobustLoss",
    "TARNetLoss",
    "DragonNetLoss",
    
    # Evaluation
    "CausalEvaluator", 
    "CausalMetrics",
    "bootstrap_ate_confidence_interval",
    "permutation_test_ate",
    
    # Uncertainty quantification
    "UncertaintyManager", 
    "ConformalPredictor", 
    "EnsembleCANS",
    "BayesianCANS",
    "UncertaintyCalibrator",
    "evaluate_uncertainty_quality",
]

# Package-level configuration
import logging
import warnings

# Configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Filter specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

def get_version() -> str:
    """Get the package version."""
    return __version__

def citation() -> str:
    """Get citation information for the CANS framework."""
    return """
    @software{rajamanickam2024cans,
      author = {Rajamanickam, Durai},
      title = {CANS: Causal Adaptive Neural System},
      url = {https://github.com/rdmurugan/cans-framework},
      version = {3.0.0},
      year = {2024},
    }
    """

def show_versions() -> None:
    """Show versions of key dependencies."""
    import sys
    import torch
    import transformers
    import sklearn
    import pandas
    import numpy
    
    print(f"CANS version: {__version__}")
    print(f"Python version: {sys.version}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Transformers version: {transformers.__version__}")
    print(f"Scikit-learn version: {sklearn.__version__}")
    print(f"Pandas version: {pandas.__version__}")
    print(f"NumPy version: {numpy.__version__}")
    
    try:
        import torch_geometric
        print(f"PyTorch Geometric version: {torch_geometric.__version__}")
    except ImportError:
        print("PyTorch Geometric: Not installed")
    
    try:
        import networkx
        print(f"NetworkX version: {networkx.__version__}")
    except ImportError:
        print("NetworkX: Not installed")
