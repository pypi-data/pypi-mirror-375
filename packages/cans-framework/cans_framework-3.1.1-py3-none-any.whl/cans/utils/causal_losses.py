"""
Causal-specific loss functions for CANS framework.
Implements advanced loss functions for causal inference and representation learning.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, Optional, Tuple


class CausalLossFunction(nn.Module):
    """Base class for causal loss functions"""
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    
    def forward(self, predictions: Dict[str, torch.Tensor], 
                targets: Dict[str, torch.Tensor], 
                **kwargs) -> torch.Tensor:
        raise NotImplementedError


class CFRLoss(CausalLossFunction):
    """
    Counterfactual Regression (CFR) Loss from Shalit et al. (2017)
    Combines factual loss with representation balancing
    """
    
    def __init__(self, 
                 alpha: float = 1.0, 
                 beta: float = 1.0,
                 distance_metric: str = 'mmd'):
        super().__init__("CFR")
        self.alpha = alpha  # Weight for factual loss
        self.beta = beta    # Weight for representation balance
        self.distance_metric = distance_metric
    
    def forward(self, predictions: Dict[str, torch.Tensor], 
                targets: Dict[str, torch.Tensor],
                representations: Optional[torch.Tensor] = None,
                **kwargs) -> Dict[str, torch.Tensor]:
        """
        Compute CFR loss
        
        Args:
            predictions: {'mu0': potential_outcomes_control, 'mu1': potential_outcomes_treated}
            targets: {'y': outcomes, 't': treatments}
            representations: Learned representations for balancing
            
        Returns:
            Dictionary with loss components
        """
        mu0, mu1 = predictions['mu0'], predictions['mu1']
        y, t = targets['y'], targets['t']
        
        # Factual loss - only use observed outcomes
        y_pred = torch.where(t.unsqueeze(-1) == 1, mu1, mu0)
        factual_loss = F.mse_loss(y_pred.squeeze(), y)
        
        # Representation balancing loss
        if representations is not None:
            balance_loss = self._compute_balance_loss(representations, t)
        else:
            balance_loss = torch.tensor(0.0, device=y.device)
        
        # Total loss
        total_loss = self.alpha * factual_loss + self.beta * balance_loss
        
        return {
            'total_loss': total_loss,
            'factual_loss': factual_loss,
            'balance_loss': balance_loss
        }
    
    def _compute_balance_loss(self, representations: torch.Tensor, treatments: torch.Tensor) -> torch.Tensor:
        """Compute representation balancing loss"""
        treated_mask = treatments == 1
        control_mask = treatments == 0
        
        if not treated_mask.any() or not control_mask.any():
            return torch.tensor(0.0, device=representations.device)
        
        treated_reps = representations[treated_mask]
        control_reps = representations[control_mask]
        
        if self.distance_metric == 'mmd':
            return self._mmd_loss(treated_reps, control_reps)
        elif self.distance_metric == 'wasserstein':
            return self._wasserstein_loss(treated_reps, control_reps)
        else:
            return F.mse_loss(treated_reps.mean(0), control_reps.mean(0))
    
    def _mmd_loss(self, x: torch.Tensor, y: torch.Tensor, sigma: float = 1.0) -> torch.Tensor:
        """Maximum Mean Discrepancy loss"""
        def gaussian_kernel(x1, x2, sigma):
            x1_norm = x1.pow(2).sum(dim=-1, keepdim=True)
            x2_norm = x2.pow(2).sum(dim=-1, keepdim=True)
            dist = x1_norm + x2_norm.t() - 2.0 * torch.mm(x1, x2.t())
            return torch.exp(-dist / (2 * sigma ** 2))
        
        k_xx = gaussian_kernel(x, x, sigma)
        k_yy = gaussian_kernel(y, y, sigma)
        k_xy = gaussian_kernel(x, y, sigma)
        
        return k_xx.mean() + k_yy.mean() - 2 * k_xy.mean()
    
    def _wasserstein_loss(self, x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        """Approximate Wasserstein distance"""
        # Simplified implementation - sort and compute L2 distance
        x_sorted, _ = torch.sort(x.view(-1))
        y_sorted, _ = torch.sort(y.view(-1))
        
        # Pad shorter tensor
        if len(x_sorted) < len(y_sorted):
            x_sorted = F.pad(x_sorted, (0, len(y_sorted) - len(x_sorted)), value=x_sorted[-1])
        elif len(y_sorted) < len(x_sorted):
            y_sorted = F.pad(y_sorted, (0, len(x_sorted) - len(y_sorted)), value=y_sorted[-1])
        
        return F.mse_loss(x_sorted, y_sorted)


class IPWLoss(CausalLossFunction):
    """Inverse Propensity Weighting Loss"""
    
    def __init__(self, clip_weights: bool = True, max_weight: float = 10.0):
        super().__init__("IPW")
        self.clip_weights = clip_weights
        self.max_weight = max_weight
    
    def forward(self, predictions: Dict[str, torch.Tensor], 
                targets: Dict[str, torch.Tensor],
                propensity_scores: torch.Tensor,
                **kwargs) -> Dict[str, torch.Tensor]:
        """
        Compute IPW loss
        
        Args:
            predictions: {'mu0': control_outcomes, 'mu1': treated_outcomes}
            targets: {'y': outcomes, 't': treatments}
            propensity_scores: Estimated propensity scores P(T=1|X)
            
        Returns:
            Dictionary with loss components
        """
        mu0, mu1 = predictions['mu0'], predictions['mu1']
        y, t = targets['y'], targets['t']
        
        # Compute IPW weights
        weights = torch.where(
            t == 1,
            1.0 / propensity_scores,
            1.0 / (1.0 - propensity_scores)
        )
        
        if self.clip_weights:
            weights = torch.clamp(weights, max=self.max_weight)
        
        # Weighted factual loss
        y_pred = torch.where(t.unsqueeze(-1) == 1, mu1, mu0)
        weighted_loss = weights.unsqueeze(-1) * (y_pred.squeeze() - y) ** 2
        ipw_loss = weighted_loss.mean()
        
        return {
            'total_loss': ipw_loss,
            'ipw_loss': ipw_loss,
            'avg_weight': weights.mean(),
            'max_weight': weights.max()
        }


class DoublyRobustLoss(CausalLossFunction):
    """Doubly Robust Loss combining outcome regression and propensity weighting"""
    
    def __init__(self, lambda_reg: float = 0.1):
        super().__init__("DoublyRobust")
        self.lambda_reg = lambda_reg
    
    def forward(self, predictions: Dict[str, torch.Tensor], 
                targets: Dict[str, torch.Tensor],
                propensity_scores: torch.Tensor,
                **kwargs) -> Dict[str, torch.Tensor]:
        """
        Compute doubly robust loss
        
        Args:
            predictions: {'mu0': control_outcomes, 'mu1': treated_outcomes}
            targets: {'y': outcomes, 't': treatments}
            propensity_scores: Estimated propensity scores
            
        Returns:
            Dictionary with loss components
        """
        mu0, mu1 = predictions['mu0'], predictions['mu1']
        y, t = targets['y'], targets['t']
        
        # Regression loss
        y_pred = torch.where(t.unsqueeze(-1) == 1, mu1, mu0)
        reg_loss = F.mse_loss(y_pred.squeeze(), y)
        
        # IPW correction terms
        ipw_weights = torch.where(
            t == 1,
            1.0 / torch.clamp(propensity_scores, min=1e-6),
            1.0 / torch.clamp(1.0 - propensity_scores, min=1e-6)
        )
        
        # Doubly robust terms
        treated_correction = (t == 1).float() * ipw_weights * (y - mu1.squeeze())
        control_correction = (t == 0).float() * ipw_weights * (y - mu0.squeeze())
        
        dr_loss = reg_loss + self.lambda_reg * (
            treated_correction.abs().mean() + control_correction.abs().mean()
        )
        
        return {
            'total_loss': dr_loss,
            'regression_loss': reg_loss,
            'ipw_correction': self.lambda_reg * (treated_correction.abs().mean() + control_correction.abs().mean())
        }


class TARNetLoss(CausalLossFunction):
    """TARNet Loss with shared and treatment-specific representations"""
    
    def __init__(self, alpha: float = 1.0):
        super().__init__("TARNet")
        self.alpha = alpha
    
    def forward(self, predictions: Dict[str, torch.Tensor], 
                targets: Dict[str, torch.Tensor],
                **kwargs) -> Dict[str, torch.Tensor]:
        """
        Compute TARNet loss - simple factual loss with regularization
        
        Args:
            predictions: {'mu0': control_outcomes, 'mu1': treated_outcomes}
            targets: {'y': outcomes, 't': treatments}
            
        Returns:
            Dictionary with loss components
        """
        mu0, mu1 = predictions['mu0'], predictions['mu1']
        y, t = targets['y'], targets['t']
        
        # Factual loss
        y_pred = torch.where(t.unsqueeze(-1) == 1, mu1, mu0)
        factual_loss = F.mse_loss(y_pred.squeeze(), y)
        
        # Simple regularization on potential outcomes
        reg_loss = torch.mean(torch.abs(mu1 - mu0))
        
        total_loss = factual_loss + self.alpha * reg_loss
        
        return {
            'total_loss': total_loss,
            'factual_loss': factual_loss,
            'regularization_loss': reg_loss
        }


class DragonNetLoss(CausalLossFunction):
    """DragonNet Loss with targeted regularization"""
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        super().__init__("DragonNet")
        self.alpha = alpha  # Weight for propensity loss
        self.beta = beta    # Weight for targeted regularization
    
    def forward(self, predictions: Dict[str, torch.Tensor], 
                targets: Dict[str, torch.Tensor],
                propensity_logits: torch.Tensor,
                **kwargs) -> Dict[str, torch.Tensor]:
        """
        Compute DragonNet loss
        
        Args:
            predictions: {'mu0': control_outcomes, 'mu1': treated_outcomes}
            targets: {'y': outcomes, 't': treatments}
            propensity_logits: Logits from propensity head
            
        Returns:
            Dictionary with loss components
        """
        mu0, mu1 = predictions['mu0'], predictions['mu1']
        y, t = targets['y'], targets['t']
        
        # Outcome loss
        y_pred = torch.where(t.unsqueeze(-1) == 1, mu1, mu0)
        outcome_loss = F.mse_loss(y_pred.squeeze(), y)
        
        # Propensity loss
        propensity_loss = F.binary_cross_entropy_with_logits(
            propensity_logits.squeeze(), t.float()
        )
        
        # Targeted regularization
        propensity_scores = torch.sigmoid(propensity_logits.squeeze())
        weights = 1.0 / torch.clamp(
            torch.where(t == 1, propensity_scores, 1 - propensity_scores),
            min=1e-6
        )
        
        targeted_reg = torch.mean(weights * (y_pred.squeeze() - y) ** 2)
        
        total_loss = (outcome_loss + 
                     self.alpha * propensity_loss + 
                     self.beta * targeted_reg)
        
        return {
            'total_loss': total_loss,
            'outcome_loss': outcome_loss,
            'propensity_loss': propensity_loss,
            'targeted_regularization': targeted_reg
        }


class CausalLossManager:
    """Manages different causal loss functions"""
    
    def __init__(self, loss_type: str = "cfr", **loss_kwargs):
        """
        Initialize causal loss manager
        
        Args:
            loss_type: Type of loss function
            **loss_kwargs: Arguments for loss function
        """
        self.loss_type = loss_type
        
        if loss_type == "cfr":
            self.loss_fn = CFRLoss(**loss_kwargs)
        elif loss_type == "ipw":
            self.loss_fn = IPWLoss(**loss_kwargs)
        elif loss_type == "dr" or loss_type == "doubly_robust":
            self.loss_fn = DoublyRobustLoss(**loss_kwargs)
        elif loss_type == "tarnet":
            self.loss_fn = TARNetLoss(**loss_kwargs)
        elif loss_type == "dragonnet":
            self.loss_fn = DragonNetLoss(**loss_kwargs)
        else:
            raise ValueError(f"Unknown loss type: {loss_type}")
    
    def compute_loss(self, predictions: Dict[str, torch.Tensor], 
                    targets: Dict[str, torch.Tensor],
                    **kwargs) -> Dict[str, torch.Tensor]:
        """Compute loss using selected loss function"""
        return self.loss_fn(predictions, targets, **kwargs)
    
    @staticmethod
    def get_available_losses() -> Dict[str, str]:
        """Get available loss functions with descriptions"""
        return {
            "cfr": "Counterfactual Regression with representation balancing",
            "ipw": "Inverse Propensity Weighting",
            "doubly_robust": "Doubly Robust estimation",
            "tarnet": "TARNet with shared representations",
            "dragonnet": "DragonNet with targeted regularization"
        }


# Utility functions for computing auxiliary losses
def compute_propensity_regularization(representations: torch.Tensor, 
                                    treatments: torch.Tensor,
                                    lambda_reg: float = 0.01) -> torch.Tensor:
    """Compute regularization term to prevent perfect treatment prediction"""
    treated_reps = representations[treatments == 1]
    control_reps = representations[treatments == 0]
    
    if len(treated_reps) == 0 or len(control_reps) == 0:
        return torch.tensor(0.0, device=representations.device)
    
    # Encourage similar representations between treatment groups
    treated_mean = treated_reps.mean(0)
    control_mean = control_reps.mean(0)
    
    return lambda_reg * F.mse_loss(treated_mean, control_mean)


def compute_outcome_regularization(mu0: torch.Tensor, 
                                  mu1: torch.Tensor,
                                  lambda_reg: float = 0.01) -> torch.Tensor:
    """Compute regularization on potential outcome predictions"""
    # Encourage smooth treatment effects
    treatment_effects = mu1 - mu0
    return lambda_reg * torch.var(treatment_effects.squeeze())


def compute_gradient_penalty(model: nn.Module, 
                           real_data: torch.Tensor,
                           fake_data: torch.Tensor,
                           lambda_gp: float = 10.0) -> torch.Tensor:
    """Compute gradient penalty for stable training"""
    batch_size = real_data.size(0)
    
    # Random interpolation
    alpha = torch.rand(batch_size, 1, device=real_data.device)
    interpolates = alpha * real_data + ((1 - alpha) * fake_data)
    interpolates.requires_grad_(True)
    
    # Forward pass
    disc_interpolates = model(interpolates)
    
    # Compute gradients
    gradients = torch.autograd.grad(
        outputs=disc_interpolates,
        inputs=interpolates,
        grad_outputs=torch.ones_like(disc_interpolates),
        create_graph=True,
        retain_graph=True,
        only_inputs=True
    )[0]
    
    gradient_penalty = lambda_gp * ((gradients.norm(2, dim=1) - 1) ** 2).mean()
    return gradient_penalty