"""
Uncertainty quantification for causal inference in CANS framework.
Implements Bayesian methods, ensemble approaches, and conformal prediction.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from scipy import stats
from sklearn.model_selection import KFold
from sklearn.isotonic import IsotonicRegression
import warnings

from ..exceptions import ValidationError


class BayesianCANS(nn.Module):
    """Bayesian version of CANS model with uncertainty quantification"""
    
    def __init__(self, base_model, prior_std: float = 1.0, n_samples: int = 10):
        super().__init__()
        self.base_model = base_model
        self.prior_std = prior_std
        self.n_samples = n_samples
        
        # Convert base model parameters to Bayesian parameters
        self._setup_bayesian_layers()
    
    def _setup_bayesian_layers(self):
        """Convert deterministic layers to Bayesian layers"""
        # This is a simplified implementation
        # In practice, would replace all Linear layers with BayesianLinear
        self.bayesian_params = {}
        
        for name, param in self.base_model.named_parameters():
            if param.requires_grad:
                # Mean parameter (initialize with original weights)
                mean = nn.Parameter(param.data.clone())
                # Log variance parameter (initialize to give std=prior_std)
                log_var = nn.Parameter(torch.full_like(param.data, np.log(self.prior_std**2)))
                
                self.bayesian_params[f'{name}_mean'] = mean
                self.bayesian_params[f'{name}_log_var'] = log_var
                
                # Register as parameters
                self.register_parameter(f'{name}_mean', mean)
                self.register_parameter(f'{name}_log_var', log_var)
    
    def sample_parameters(self) -> Dict[str, torch.Tensor]:
        """Sample parameters from posterior distributions"""
        sampled_params = {}
        
        for name in self.bayesian_params:
            if name.endswith('_mean'):
                base_name = name[:-5]  # Remove '_mean'
                mean = self.bayesian_params[name]
                log_var = self.bayesian_params[f'{base_name}_log_var']
                std = torch.exp(0.5 * log_var)
                
                # Sample from Gaussian
                eps = torch.randn_like(mean)
                sampled_params[base_name] = mean + std * eps
        
        return sampled_params
    
    def forward(self, *args, **kwargs) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass with uncertainty quantification
        
        Returns:
            Tuple of (mu0_mean, mu1_mean, uncertainties)
        """
        mu0_samples = []
        mu1_samples = []
        
        for _ in range(self.n_samples):
            # Sample parameters
            sampled_params = self.sample_parameters()
            
            # Temporarily replace base model parameters
            original_params = {}
            for name, param in self.base_model.named_parameters():
                original_params[name] = param.data.clone()
                if name in sampled_params:
                    param.data = sampled_params[name]
            
            # Forward pass with sampled parameters
            with torch.no_grad():
                mu0, mu1 = self.base_model(*args, **kwargs)
                mu0_samples.append(mu0)
                mu1_samples.append(mu1)
            
            # Restore original parameters
            for name, param in self.base_model.named_parameters():
                param.data = original_params[name]
        
        # Compute statistics
        mu0_samples = torch.stack(mu0_samples, dim=0)
        mu1_samples = torch.stack(mu1_samples, dim=0)
        
        mu0_mean = mu0_samples.mean(dim=0)
        mu1_mean = mu1_samples.mean(dim=0)
        
        mu0_std = mu0_samples.std(dim=0)
        mu1_std = mu1_samples.std(dim=0)
        
        # Total uncertainty (epistemic + aleatoric)
        uncertainties = torch.sqrt(mu0_std**2 + mu1_std**2)
        
        return mu0_mean, mu1_mean, uncertainties
    
    def kl_divergence(self) -> torch.Tensor:
        """Compute KL divergence for variational loss"""
        kl_div = 0.0
        
        for name in self.bayesian_params:
            if name.endswith('_mean'):
                base_name = name[:-5]
                mean = self.bayesian_params[name]
                log_var = self.bayesian_params[f'{base_name}_log_var']
                
                # KL divergence from standard normal prior
                kl_div += -0.5 * torch.sum(1 + log_var - mean.pow(2) - log_var.exp())
        
        return kl_div


class EnsembleCANS:
    """Ensemble approach for uncertainty quantification"""
    
    def __init__(self, model_class, ensemble_size: int = 5, **model_kwargs):
        """
        Initialize ensemble
        
        Args:
            model_class: Class to instantiate models
            ensemble_size: Number of models in ensemble
            **model_kwargs: Arguments for model initialization
        """
        self.ensemble_size = ensemble_size
        self.models = []
        
        for i in range(ensemble_size):
            # Add slight variation to initialization
            kwargs = model_kwargs.copy()
            if 'random_seed' in kwargs:
                kwargs['random_seed'] = kwargs['random_seed'] + i
            
            model = model_class(**kwargs)
            self.models.append(model)
    
    def fit(self, train_loaders: List, val_loaders: List, **train_kwargs):
        """Train ensemble on different data splits or with different initialization"""
        if len(train_loaders) != self.ensemble_size:
            # Use bootstrap sampling if not enough data splits provided
            train_loaders = self._create_bootstrap_loaders(train_loaders[0])
        
        for i, (model, train_loader) in enumerate(zip(self.models, train_loaders)):
            print(f"Training ensemble model {i+1}/{self.ensemble_size}")
            
            # Would need to adapt based on actual training interface
            # model.fit(train_loader, val_loaders[i] if i < len(val_loaders) else None, **train_kwargs)
    
    def predict_with_uncertainty(self, dataloader) -> Dict[str, torch.Tensor]:
        """Make predictions with uncertainty estimates"""
        all_mu0_preds = []
        all_mu1_preds = []
        
        for model in self.models:
            model.eval()
            mu0_preds = []
            mu1_preds = []
            
            with torch.no_grad():
                for batch in dataloader:
                    mu0, mu1 = model(batch['graph'], batch['text'], batch['treatment'])
                    mu0_preds.append(mu0)
                    mu1_preds.append(mu1)
            
            all_mu0_preds.append(torch.cat(mu0_preds, dim=0))
            all_mu1_preds.append(torch.cat(mu1_preds, dim=0))
        
        # Stack predictions from all models
        mu0_ensemble = torch.stack(all_mu0_preds, dim=0)  # [n_models, n_samples, 1]
        mu1_ensemble = torch.stack(all_mu1_preds, dim=0)
        
        # Compute statistics
        mu0_mean = mu0_ensemble.mean(dim=0)
        mu1_mean = mu1_ensemble.mean(dim=0)
        
        mu0_std = mu0_ensemble.std(dim=0)
        mu1_std = mu1_ensemble.std(dim=0)
        
        # CATE predictions and uncertainty
        cate_ensemble = mu1_ensemble - mu0_ensemble
        cate_mean = cate_ensemble.mean(dim=0)
        cate_std = cate_ensemble.std(dim=0)
        
        return {
            'mu0_mean': mu0_mean,
            'mu1_mean': mu1_mean,
            'mu0_std': mu0_std,
            'mu1_std': mu1_std,
            'cate_mean': cate_mean,
            'cate_std': cate_std,
            'epistemic_uncertainty': (mu0_std + mu1_std) / 2  # Average epistemic uncertainty
        }
    
    def _create_bootstrap_loaders(self, original_loader):
        """Create bootstrap samples from original data loader"""
        # Simplified implementation - would need proper bootstrap sampling
        return [original_loader] * self.ensemble_size


class ConformalPredictor:
    """Conformal prediction for distribution-free uncertainty quantification"""
    
    def __init__(self, model, alpha: float = 0.1):
        """
        Initialize conformal predictor
        
        Args:
            model: Trained model for point predictions
            alpha: Miscoverage rate (1-alpha is target coverage)
        """
        self.model = model
        self.alpha = alpha
        self.quantiles = None
        self.calibrated = False
    
    def calibrate(self, cal_loader) -> 'ConformalPredictor':
        """
        Calibrate predictor using calibration set
        
        Args:
            cal_loader: Calibration data loader
            
        Returns:
            Self for method chaining
        """
        self.model.eval()
        residuals = []
        
        with torch.no_grad():
            for batch in cal_loader:
                mu0, mu1 = self.model(batch['graph'], batch['text'], batch['treatment'])
                
                # Compute residuals (non-conformity scores)
                y_pred = torch.where(batch['treatment'].unsqueeze(-1) == 1, mu1, mu0)
                residual = torch.abs(batch['outcome'] - y_pred.squeeze())
                residuals.extend(residual.cpu().numpy())
        
        residuals = np.array(residuals)
        
        # Compute quantile
        n = len(residuals)
        q_level = np.ceil((n + 1) * (1 - self.alpha)) / n
        self.quantiles = np.quantile(residuals, q_level)
        
        self.calibrated = True
        return self
    
    def predict_with_intervals(self, test_loader, return_residuals: bool = False) -> Dict[str, torch.Tensor]:
        """
        Make predictions with prediction intervals
        
        Args:
            test_loader: Test data loader
            return_residuals: Whether to return residuals for diagnostics
            
        Returns:
            Dictionary with predictions and intervals
        """
        if not self.calibrated:
            raise ValidationError("Conformal predictor not calibrated. Call calibrate() first.")
        
        self.model.eval()
        predictions = []
        intervals_lower = []
        intervals_upper = []
        residuals = [] if return_residuals else None
        
        with torch.no_grad():
            for batch in test_loader:
                mu0, mu1 = self.model(batch['graph'], batch['text'], batch['treatment'])
                
                # Point predictions
                y_pred = torch.where(batch['treatment'].unsqueeze(-1) == 1, mu1, mu0)
                predictions.extend(y_pred.squeeze().cpu().numpy())
                
                # Prediction intervals
                pred_np = y_pred.squeeze().cpu().numpy()
                lower = pred_np - self.quantiles
                upper = pred_np + self.quantiles
                
                intervals_lower.extend(lower)
                intervals_upper.extend(upper)
                
                # Residuals for diagnostics
                if return_residuals:
                    residual = torch.abs(batch['outcome'] - y_pred.squeeze())
                    residuals.extend(residual.cpu().numpy())
        
        result = {
            'predictions': np.array(predictions),
            'intervals_lower': np.array(intervals_lower),
            'intervals_upper': np.array(intervals_upper),
            'quantiles': self.quantiles,
            'coverage_target': 1 - self.alpha
        }
        
        if return_residuals:
            result['residuals'] = np.array(residuals)
        
        return result


class UncertaintyCalibrator:
    """Calibrate uncertainty estimates for better reliability"""
    
    def __init__(self, method: str = 'isotonic'):
        """
        Initialize calibrator
        
        Args:
            method: Calibration method ('isotonic', 'platt', 'temperature')
        """
        self.method = method
        self.calibrator = None
        self.fitted = False
    
    def fit(self, uncertainties: np.ndarray, residuals: np.ndarray) -> 'UncertaintyCalibrator':
        """
        Fit calibrator
        
        Args:
            uncertainties: Predicted uncertainties
            residuals: Actual residuals/errors
            
        Returns:
            Self for method chaining
        """
        if self.method == 'isotonic':
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
            self.calibrator.fit(uncertainties, residuals)
        elif self.method == 'platt':
            # Simplified Platt scaling
            from sklearn.linear_model import LogisticRegression
            
            # Convert to binary classification problem (high/low error)
            high_error = (residuals > np.median(residuals)).astype(int)
            self.calibrator = LogisticRegression()
            self.calibrator.fit(uncertainties.reshape(-1, 1), high_error)
        else:
            raise ValueError(f"Unknown calibration method: {self.method}")
        
        self.fitted = True
        return self
    
    def transform(self, uncertainties: np.ndarray) -> np.ndarray:
        """
        Apply calibration to uncertainties
        
        Args:
            uncertainties: Raw uncertainties
            
        Returns:
            Calibrated uncertainties
        """
        if not self.fitted:
            raise ValidationError("Calibrator not fitted. Call fit() first.")
        
        if self.method == 'isotonic':
            return self.calibrator.predict(uncertainties)
        elif self.method == 'platt':
            # Convert back to uncertainty estimates
            probs = self.calibrator.predict_proba(uncertainties.reshape(-1, 1))[:, 1]
            return probs
        
        return uncertainties


class BootstrapUncertainty:
    """Bootstrap-based uncertainty estimation"""
    
    def __init__(self, n_bootstrap: int = 100, confidence_level: float = 0.95):
        """
        Initialize bootstrap uncertainty estimator
        
        Args:
            n_bootstrap: Number of bootstrap samples
            confidence_level: Confidence level for intervals
        """
        self.n_bootstrap = n_bootstrap
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    def estimate_uncertainty(self, 
                           model,
                           dataloader,
                           prediction_fn: Optional[Callable] = None) -> Dict[str, np.ndarray]:
        """
        Estimate uncertainty using bootstrap sampling
        
        Args:
            model: Model to use for predictions
            dataloader: Data loader
            prediction_fn: Custom prediction function
            
        Returns:
            Dictionary with bootstrap estimates
        """
        # Collect data
        all_data = []
        for batch in dataloader:
            all_data.append(batch)
        
        if not all_data:
            raise ValueError("Empty dataloader")
        
        bootstrap_predictions = []
        
        for _ in range(self.n_bootstrap):
            # Bootstrap sample
            bootstrap_batches = np.random.choice(all_data, size=len(all_data), replace=True)
            
            batch_predictions = []
            model.eval()
            
            with torch.no_grad():
                for batch in bootstrap_batches:
                    if prediction_fn is not None:
                        pred = prediction_fn(model, batch)
                    else:
                        mu0, mu1 = model(batch['graph'], batch['text'], batch['treatment'])
                        pred = torch.where(batch['treatment'].unsqueeze(-1) == 1, mu1, mu0)
                    
                    batch_predictions.extend(pred.squeeze().cpu().numpy())
            
            bootstrap_predictions.append(batch_predictions)
        
        bootstrap_predictions = np.array(bootstrap_predictions)  # [n_bootstrap, n_samples]
        
        # Compute statistics
        mean_pred = np.mean(bootstrap_predictions, axis=0)
        std_pred = np.std(bootstrap_predictions, axis=0)
        
        # Confidence intervals
        lower_percentile = (self.alpha / 2) * 100
        upper_percentile = (1 - self.alpha / 2) * 100
        
        ci_lower = np.percentile(bootstrap_predictions, lower_percentile, axis=0)
        ci_upper = np.percentile(bootstrap_predictions, upper_percentile, axis=0)
        
        return {
            'mean': mean_pred,
            'std': std_pred,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'all_predictions': bootstrap_predictions
        }


class UncertaintyManager:
    """Unified interface for different uncertainty quantification methods"""
    
    def __init__(self, method: str = 'ensemble', **method_kwargs):
        """
        Initialize uncertainty manager
        
        Args:
            method: Uncertainty method ('bayesian', 'ensemble', 'conformal', 'bootstrap')
            **method_kwargs: Method-specific arguments
        """
        self.method = method
        self.uncertainty_estimator = None
        self.method_kwargs = method_kwargs
    
    def setup(self, model, **setup_kwargs):
        """Setup uncertainty estimator"""
        if self.method == 'bayesian':
            self.uncertainty_estimator = BayesianCANS(model, **self.method_kwargs)
        elif self.method == 'ensemble':
            self.uncertainty_estimator = EnsembleCANS(type(model), **self.method_kwargs)
        elif self.method == 'conformal':
            self.uncertainty_estimator = ConformalPredictor(model, **self.method_kwargs)
        elif self.method == 'bootstrap':
            self.uncertainty_estimator = BootstrapUncertainty(**self.method_kwargs)
        else:
            raise ValueError(f"Unknown uncertainty method: {self.method}")
    
    def estimate_uncertainty(self, *args, **kwargs) -> Dict[str, Any]:
        """Estimate uncertainty using selected method"""
        if self.uncertainty_estimator is None:
            raise ValidationError("Uncertainty estimator not setup. Call setup() first.")
        
        if hasattr(self.uncertainty_estimator, 'estimate_uncertainty'):
            return self.uncertainty_estimator.estimate_uncertainty(*args, **kwargs)
        elif hasattr(self.uncertainty_estimator, 'predict_with_uncertainty'):
            return self.uncertainty_estimator.predict_with_uncertainty(*args, **kwargs)
        elif hasattr(self.uncertainty_estimator, 'predict_with_intervals'):
            return self.uncertainty_estimator.predict_with_intervals(*args, **kwargs)
        else:
            raise NotImplementedError(f"Method {self.method} not implemented properly")
    
    @staticmethod
    def get_available_methods() -> Dict[str, str]:
        """Get available uncertainty quantification methods"""
        return {
            'bayesian': 'Bayesian neural networks with variational inference',
            'ensemble': 'Deep ensemble approach with multiple models',
            'conformal': 'Conformal prediction for distribution-free intervals',
            'bootstrap': 'Bootstrap sampling for uncertainty estimation'
        }


def evaluate_uncertainty_quality(predictions: np.ndarray,
                                targets: np.ndarray,
                                uncertainties: np.ndarray,
                                confidence_level: float = 0.95) -> Dict[str, float]:
    """
    Evaluate quality of uncertainty estimates
    
    Args:
        predictions: Point predictions
        targets: True values
        uncertainties: Uncertainty estimates
        confidence_level: Confidence level for intervals
        
    Returns:
        Dictionary with evaluation metrics
    """
    residuals = np.abs(targets - predictions)
    
    metrics = {}
    
    # Correlation between uncertainty and error
    if len(uncertainties) > 1 and np.var(uncertainties) > 0:
        correlation, p_value = stats.pearsonr(uncertainties, residuals)
        metrics['uncertainty_correlation'] = correlation
        metrics['uncertainty_correlation_p'] = p_value
    else:
        metrics['uncertainty_correlation'] = 0.0
        metrics['uncertainty_correlation_p'] = 1.0
    
    # Uncertainty calibration (using quantile-based intervals)
    z_score = stats.norm.ppf(1 - (1 - confidence_level) / 2)
    intervals_lower = predictions - z_score * uncertainties
    intervals_upper = predictions + z_score * uncertainties
    
    coverage = np.mean((targets >= intervals_lower) & (targets <= intervals_upper))
    metrics['coverage_rate'] = coverage
    metrics['coverage_error'] = abs(coverage - confidence_level)
    
    # Interval width
    interval_widths = intervals_upper - intervals_lower
    metrics['mean_interval_width'] = np.mean(interval_widths)
    metrics['median_interval_width'] = np.median(interval_widths)
    
    # Sharpness (narrower intervals are better, given good coverage)
    if coverage >= confidence_level - 0.05:  # Within 5% of target
        metrics['sharpness'] = 1.0 / np.mean(interval_widths)
    else:
        metrics['sharpness'] = 0.0
    
    # Reliability diagram data (for plotting)
    n_bins = 10
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    
    # Convert uncertainties to confidence scores
    confidence_scores = 1 / (1 + uncertainties)  # Higher uncertainty -> lower confidence
    confidence_scores = (confidence_scores - confidence_scores.min()) / (confidence_scores.max() - confidence_scores.min())
    
    accuracies = []
    confidences = []
    
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = (confidence_scores > bin_lower) & (confidence_scores <= bin_upper)
        prop_in_bin = in_bin.mean()
        
        if prop_in_bin > 0:
            accuracy_in_bin = (residuals[in_bin] <= np.median(residuals)).mean()
            avg_confidence_in_bin = confidence_scores[in_bin].mean()
            
            accuracies.append(accuracy_in_bin)
            confidences.append(avg_confidence_in_bin)
    
    if accuracies:
        # Expected Calibration Error
        ece = np.mean([abs(acc - conf) for acc, conf in zip(accuracies, confidences)])
        metrics['expected_calibration_error'] = ece
    
    return metrics