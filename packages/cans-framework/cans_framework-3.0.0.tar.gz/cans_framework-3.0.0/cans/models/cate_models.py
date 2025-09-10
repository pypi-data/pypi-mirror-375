"""
Conditional Average Treatment Effect (CATE) models for heterogeneous treatment effects.
Implements various approaches for estimating personalized treatment effects.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple, Optional, List
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_predict

from ..exceptions import ModelError


class CATEEstimator(nn.Module):
    """Base class for CATE estimation models"""
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    
    def estimate_cate(self, X: torch.Tensor, **kwargs) -> torch.Tensor:
        """Estimate conditional average treatment effect"""
        raise NotImplementedError
    
    def estimate_ate(self, X: torch.Tensor, **kwargs) -> torch.Tensor:
        """Estimate average treatment effect"""
        cate = self.estimate_cate(X, **kwargs)
        return cate.mean()


class XLearner(CATEEstimator):
    """X-Learner for CATE estimation (Künzel et al., 2019)"""
    
    def __init__(self, 
                 base_model_class=None,
                 propensity_model_class=None,
                 **model_kwargs):
        super().__init__("X-Learner")
        
        # Use RandomForest as default base models
        if base_model_class is None:
            self.base_model_class = lambda: RandomForestRegressor(n_estimators=100, **model_kwargs)
        else:
            self.base_model_class = base_model_class
        
        if propensity_model_class is None:
            from sklearn.ensemble import RandomForestClassifier
            self.propensity_model_class = lambda: RandomForestClassifier(n_estimators=100, **model_kwargs)
        else:
            self.propensity_model_class = propensity_model_class
        
        # Initialize models (will be fit during training)
        self.mu0_model = None  # E[Y|X, T=0]
        self.mu1_model = None  # E[Y|X, T=1]
        self.tau0_model = None  # E[τ|X, T=0]  
        self.tau1_model = None  # E[τ|X, T=1]
        self.propensity_model = None  # P(T=1|X)
    
    def fit(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray) -> 'XLearner':
        """
        Fit X-Learner models
        
        Args:
            X: Covariates [n_samples, n_features]
            T: Treatment assignments [n_samples]
            Y: Outcomes [n_samples]
            
        Returns:
            Self for method chaining
        """
        # Split data by treatment
        treated_mask = T == 1
        control_mask = T == 0
        
        X_treated, Y_treated = X[treated_mask], Y[treated_mask]
        X_control, Y_control = X[control_mask], Y[control_mask]
        
        # Stage 1: Train outcome models on each treatment group
        self.mu0_model = self.base_model_class()
        self.mu1_model = self.base_model_class()
        
        if len(X_control) > 0:
            self.mu0_model.fit(X_control, Y_control)
        if len(X_treated) > 0:
            self.mu1_model.fit(X_treated, Y_treated)
        
        # Stage 2: Compute imputed treatment effects
        if self.mu0_model is not None and self.mu1_model is not None:
            # For treated units: τ = Y - μ₀(X)
            mu0_treated = self.mu0_model.predict(X_treated)
            tau_treated = Y_treated - mu0_treated
            
            # For control units: τ = μ₁(X) - Y  
            mu1_control = self.mu1_model.predict(X_control)
            tau_control = mu1_control - Y_control
            
            # Stage 3: Train CATE models on imputed effects
            self.tau0_model = self.base_model_class()
            self.tau1_model = self.base_model_class()
            
            if len(X_control) > 0:
                self.tau0_model.fit(X_control, tau_control)
            if len(X_treated) > 0:
                self.tau1_model.fit(X_treated, tau_treated)
            
            # Train propensity model
            self.propensity_model = self.propensity_model_class()
            self.propensity_model.fit(X, T)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict CATE using X-Learner"""
        if (self.tau0_model is None or self.tau1_model is None or 
            self.propensity_model is None):
            raise ModelError("Models not fitted. Call fit() first.")
        
        # Get propensity scores
        propensity_scores = self.propensity_model.predict_proba(X)[:, 1]
        
        # Get CATE predictions from both models
        tau0_pred = self.tau0_model.predict(X)  # CATE from control model
        tau1_pred = self.tau1_model.predict(X)  # CATE from treated model
        
        # Weighted combination based on propensity scores
        cate = propensity_scores * tau0_pred + (1 - propensity_scores) * tau1_pred
        
        return cate
    
    def estimate_cate(self, X: torch.Tensor, **kwargs) -> torch.Tensor:
        """Estimate CATE for PyTorch tensors"""
        X_np = X.detach().cpu().numpy()
        cate_np = self.predict(X_np)
        return torch.tensor(cate_np, device=X.device, dtype=X.dtype)


class TLearner(CATEEstimator):
    """T-Learner for CATE estimation"""
    
    def __init__(self, base_model_class=None, **model_kwargs):
        super().__init__("T-Learner")
        
        if base_model_class is None:
            self.base_model_class = lambda: RandomForestRegressor(n_estimators=100, **model_kwargs)
        else:
            self.base_model_class = base_model_class
        
        self.mu0_model = None
        self.mu1_model = None
    
    def fit(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray) -> 'TLearner':
        """Fit T-Learner models"""
        treated_mask = T == 1
        control_mask = T == 0
        
        # Train separate models for each treatment group
        if control_mask.any():
            self.mu0_model = self.base_model_class()
            self.mu0_model.fit(X[control_mask], Y[control_mask])
        
        if treated_mask.any():
            self.mu1_model = self.base_model_class()
            self.mu1_model.fit(X[treated_mask], Y[treated_mask])
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict CATE using T-Learner"""
        if self.mu0_model is None or self.mu1_model is None:
            raise ModelError("Models not fitted. Call fit() first.")
        
        mu0_pred = self.mu0_model.predict(X)
        mu1_pred = self.mu1_model.predict(X)
        
        return mu1_pred - mu0_pred
    
    def estimate_cate(self, X: torch.Tensor, **kwargs) -> torch.Tensor:
        """Estimate CATE for PyTorch tensors"""
        X_np = X.detach().cpu().numpy()
        cate_np = self.predict(X_np)
        return torch.tensor(cate_np, device=X.device, dtype=X.dtype)


class SLearner(CATEEstimator):
    """S-Learner for CATE estimation"""
    
    def __init__(self, base_model_class=None, **model_kwargs):
        super().__init__("S-Learner")
        
        if base_model_class is None:
            self.base_model_class = lambda: RandomForestRegressor(n_estimators=100, **model_kwargs)
        else:
            self.base_model_class = base_model_class
        
        self.model = None
    
    def fit(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray) -> 'SLearner':
        """Fit S-Learner model"""
        # Combine treatment as a feature
        X_with_T = np.column_stack([X, T])
        
        self.model = self.base_model_class()
        self.model.fit(X_with_T, Y)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict CATE using S-Learner"""
        if self.model is None:
            raise ModelError("Model not fitted. Call fit() first.")
        
        # Predict with T=1 and T=0
        X_treated = np.column_stack([X, np.ones(len(X))])
        X_control = np.column_stack([X, np.zeros(len(X))])
        
        mu1_pred = self.model.predict(X_treated)
        mu0_pred = self.model.predict(X_control)
        
        return mu1_pred - mu0_pred
    
    def estimate_cate(self, X: torch.Tensor, **kwargs) -> torch.Tensor:
        """Estimate CATE for PyTorch tensors"""
        X_np = X.detach().cpu().numpy()
        cate_np = self.predict(X_np)
        return torch.tensor(cate_np, device=X.device, dtype=X.dtype)


class NeuralCATENet(CATEEstimator):
    """Neural network-based CATE estimation"""
    
    def __init__(self, 
                 input_dim: int,
                 hidden_dims: List[int] = [256, 128, 64],
                 dropout: float = 0.1,
                 activation: str = 'relu'):
        super().__init__("Neural-CATE")
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        
        # Shared representation network
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU() if activation == 'relu' else nn.Tanh(),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        self.shared_net = nn.Sequential(*layers)
        
        # Separate heads for each potential outcome
        self.mu0_head = nn.Linear(hidden_dims[-1], 1)
        self.mu1_head = nn.Linear(hidden_dims[-1], 1)
    
    def forward(self, X: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            X: Input features
            
        Returns:
            Tuple of (mu0, mu1, cate)
        """
        shared_repr = self.shared_net(X)
        
        mu0 = self.mu0_head(shared_repr)
        mu1 = self.mu1_head(shared_repr)
        cate = mu1 - mu0
        
        return mu0, mu1, cate
    
    def estimate_cate(self, X: torch.Tensor, **kwargs) -> torch.Tensor:
        """Estimate CATE"""
        _, _, cate = self.forward(X)
        return cate.squeeze()


class CausalForest(CATEEstimator):
    """Causal Forest implementation (simplified version)"""
    
    def __init__(self, 
                 n_estimators: int = 100,
                 min_samples_leaf: int = 5,
                 max_depth: Optional[int] = None,
                 subsample_ratio: float = 0.5):
        super().__init__("Causal-Forest")
        
        self.n_estimators = n_estimators
        self.min_samples_leaf = min_samples_leaf
        self.max_depth = max_depth
        self.subsample_ratio = subsample_ratio
        
        self.trees = []
    
    def fit(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray) -> 'CausalForest':
        """Fit Causal Forest"""
        from sklearn.tree import DecisionTreeRegressor
        
        n_samples = len(X)
        
        for _ in range(self.n_estimators):
            # Sample with replacement
            indices = np.random.choice(n_samples, 
                                     size=int(n_samples * self.subsample_ratio), 
                                     replace=True)
            
            X_sample = X[indices]
            T_sample = T[indices] 
            Y_sample = Y[indices]
            
            # Fit tree with treatment-outcome interaction
            # Simplified - in practice would use specialized splitting criteria
            X_with_interaction = np.column_stack([
                X_sample, 
                T_sample,
                X_sample * T_sample.reshape(-1, 1)  # Interaction terms
            ])
            
            tree = DecisionTreeRegressor(
                min_samples_leaf=self.min_samples_leaf,
                max_depth=self.max_depth,
                random_state=np.random.randint(0, 10000)
            )
            tree.fit(X_with_interaction, Y_sample)
            self.trees.append(tree)
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict CATE using Causal Forest"""
        if not self.trees:
            raise ModelError("Forest not fitted. Call fit() first.")
        
        n_samples = len(X)
        cate_predictions = np.zeros(n_samples)
        
        for tree in self.trees:
            # Predict with T=1
            X_treated = np.column_stack([X, np.ones(n_samples), X])
            mu1_pred = tree.predict(X_treated)
            
            # Predict with T=0  
            X_control = np.column_stack([X, np.zeros(n_samples), np.zeros_like(X)])
            mu0_pred = tree.predict(X_control)
            
            cate_predictions += (mu1_pred - mu0_pred) / self.n_estimators
        
        return cate_predictions
    
    def estimate_cate(self, X: torch.Tensor, **kwargs) -> torch.Tensor:
        """Estimate CATE for PyTorch tensors"""
        X_np = X.detach().cpu().numpy()
        cate_np = self.predict(X_np)
        return torch.tensor(cate_np, device=X.device, dtype=X.dtype)


class CATEManager:
    """Manager for different CATE estimation methods"""
    
    def __init__(self, method: str = "x_learner", **method_kwargs):
        """
        Initialize CATE manager
        
        Args:
            method: CATE estimation method
            **method_kwargs: Arguments for the method
        """
        self.method = method
        
        if method == "x_learner":
            self.estimator = XLearner(**method_kwargs)
        elif method == "t_learner":
            self.estimator = TLearner(**method_kwargs)
        elif method == "s_learner":
            self.estimator = SLearner(**method_kwargs)
        elif method == "neural":
            self.estimator = NeuralCATENet(**method_kwargs)
        elif method == "causal_forest":
            self.estimator = CausalForest(**method_kwargs)
        else:
            raise ValueError(f"Unknown CATE method: {method}")
    
    def fit(self, X, T, Y):
        """Fit CATE estimator"""
        if hasattr(self.estimator, 'fit'):
            return self.estimator.fit(X, T, Y)
        else:
            # For neural networks, would need proper training loop
            raise NotImplementedError(f"Training not implemented for {self.method}")
    
    def estimate_cate(self, X: torch.Tensor, **kwargs) -> torch.Tensor:
        """Estimate CATE"""
        return self.estimator.estimate_cate(X, **kwargs)
    
    def estimate_ate(self, X: torch.Tensor, **kwargs) -> torch.Tensor:
        """Estimate ATE"""
        return self.estimator.estimate_ate(X, **kwargs)
    
    @staticmethod
    def get_available_methods() -> Dict[str, str]:
        """Get available CATE estimation methods"""
        return {
            "x_learner": "X-Learner with cross-fitted models",
            "t_learner": "T-Learner with separate treatment models", 
            "s_learner": "S-Learner with single model",
            "neural": "Neural network-based CATE estimation",
            "causal_forest": "Causal Forest with specialized splitting"
        }


def evaluate_cate_performance(true_cate: np.ndarray, 
                             predicted_cate: np.ndarray) -> Dict[str, float]:
    """
    Evaluate CATE estimation performance
    
    Args:
        true_cate: True conditional treatment effects
        predicted_cate: Predicted conditional treatment effects
        
    Returns:
        Dictionary with evaluation metrics
    """
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from scipy.stats import pearsonr, spearmanr
    
    metrics = {}
    
    # Regression metrics
    metrics['mse'] = mean_squared_error(true_cate, predicted_cate)
    metrics['rmse'] = np.sqrt(metrics['mse'])
    metrics['mae'] = mean_absolute_error(true_cate, predicted_cate)
    metrics['r2'] = r2_score(true_cate, predicted_cate)
    
    # Correlation metrics
    pearson_r, pearson_p = pearsonr(true_cate, predicted_cate)
    spearman_r, spearman_p = spearmanr(true_cate, predicted_cate)
    
    metrics['pearson_r'] = pearson_r
    metrics['pearson_p'] = pearson_p
    metrics['spearman_r'] = spearman_r
    metrics['spearman_p'] = spearman_p
    
    # PEHE (Precision in Estimation of Heterogeneous Effect)
    metrics['pehe'] = np.sqrt(np.mean((true_cate - predicted_cate) ** 2))
    
    # ATE metrics
    true_ate = np.mean(true_cate)
    pred_ate = np.mean(predicted_cate)
    metrics['ate_bias'] = abs(pred_ate - true_ate)
    metrics['ate_relative_bias'] = metrics['ate_bias'] / abs(true_ate) if true_ate != 0 else np.inf
    
    return metrics