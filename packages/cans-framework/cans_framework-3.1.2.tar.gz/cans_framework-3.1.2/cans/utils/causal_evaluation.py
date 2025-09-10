"""
Comprehensive causal evaluation metrics and benchmarking utilities.
Implements specialized metrics for causal inference validation.
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List, Union
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy import stats
from scipy.stats import wasserstein_distance
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass

from ..exceptions import ValidationError


@dataclass
class CausalMetrics:
    """Container for causal evaluation metrics"""
    # Treatment effect metrics
    ate: float = 0.0
    ate_std: float = 0.0
    ate_ci_lower: float = 0.0
    ate_ci_upper: float = 0.0
    
    att: float = 0.0  # Average Treatment Effect on Treated
    atc: float = 0.0  # Average Treatment Effect on Controls
    
    # CATE metrics
    pehe: float = 0.0  # Precision in Estimation of Heterogeneous Effect
    pehe_normalized: float = 0.0
    cate_r2: float = 0.0
    cate_correlation: float = 0.0
    
    # Model performance
    factual_mse: float = 0.0
    factual_mae: float = 0.0
    counterfactual_mse: float = 0.0
    
    # Distribution metrics
    overlap_coefficient: float = 0.0
    energy_distance: float = 0.0
    
    # Policy evaluation
    policy_value: float = 0.0
    policy_regret: float = 0.0
    
    # Calibration metrics
    coverage_rate: float = 0.0
    interval_width: float = 0.0


class CausalEvaluator:
    """Comprehensive causal inference evaluator"""
    
    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize causal evaluator
        
        Args:
            confidence_level: Confidence level for intervals
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    def evaluate_treatment_effects(self, 
                                  y_true: np.ndarray,
                                  mu0_pred: np.ndarray, 
                                  mu1_pred: np.ndarray,
                                  t_true: np.ndarray,
                                  mu0_true: Optional[np.ndarray] = None,
                                  mu1_true: Optional[np.ndarray] = None) -> CausalMetrics:
        """
        Evaluate treatment effect predictions
        
        Args:
            y_true: Observed outcomes
            mu0_pred: Predicted control outcomes
            mu1_pred: Predicted treated outcomes
            t_true: True treatment assignments
            mu0_true: True control potential outcomes (if available)
            mu1_true: True treated potential outcomes (if available)
            
        Returns:
            CausalMetrics object with evaluation results
        """
        metrics = CausalMetrics()
        
        # Calculate treatment effects
        cate_pred = mu1_pred - mu0_pred
        
        # Average Treatment Effect (ATE)
        metrics.ate = np.mean(cate_pred)
        metrics.ate_std = np.std(cate_pred) / np.sqrt(len(cate_pred))
        
        # Confidence interval for ATE
        z_score = stats.norm.ppf(1 - self.alpha/2)
        margin = z_score * metrics.ate_std
        metrics.ate_ci_lower = metrics.ate - margin
        metrics.ate_ci_upper = metrics.ate + margin
        
        # ATT and ATC
        treated_mask = t_true == 1
        control_mask = t_true == 0
        
        if treated_mask.any():
            metrics.att = np.mean(cate_pred[treated_mask])
        if control_mask.any():
            metrics.atc = np.mean(cate_pred[control_mask])
        
        # Factual prediction performance
        y_pred_factual = np.where(t_true == 1, mu1_pred, mu0_pred)
        metrics.factual_mse = mean_squared_error(y_true, y_pred_factual)
        metrics.factual_mae = mean_absolute_error(y_true, y_pred_factual)
        
        # CATE evaluation (if true potential outcomes available)
        if mu0_true is not None and mu1_true is not None:
            cate_true = mu1_true - mu0_true
            
            # PEHE (Precision in Estimation of Heterogeneous Effect)
            metrics.pehe = np.sqrt(np.mean((cate_true - cate_pred) ** 2))
            metrics.pehe_normalized = metrics.pehe / np.std(cate_true)
            
            # CATE prediction quality
            metrics.cate_r2 = r2_score(cate_true, cate_pred)
            metrics.cate_correlation, _ = stats.pearsonr(cate_true, cate_pred)
            
            # Counterfactual MSE
            cf_mse_0 = mean_squared_error(mu0_true, mu0_pred)
            cf_mse_1 = mean_squared_error(mu1_true, mu1_pred)
            metrics.counterfactual_mse = (cf_mse_0 + cf_mse_1) / 2
        
        return metrics
    
    def evaluate_propensity_scores(self, 
                                  t_true: np.ndarray,
                                  propensity_pred: np.ndarray,
                                  X: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Evaluate propensity score predictions
        
        Args:
            t_true: True treatment assignments
            propensity_pred: Predicted propensity scores
            X: Covariates (optional, for balance evaluation)
            
        Returns:
            Dictionary with propensity evaluation metrics
        """
        from sklearn.metrics import log_loss, roc_auc_score, brier_score_loss
        from sklearn.calibration import calibration_curve
        
        metrics = {}
        
        # Classification metrics
        try:
            metrics['log_loss'] = log_loss(t_true, propensity_pred)
            metrics['auc'] = roc_auc_score(t_true, propensity_pred)
            metrics['brier_score'] = brier_score_loss(t_true, propensity_pred)
        except ValueError as e:
            # Handle edge cases (e.g., all one class)
            metrics['log_loss'] = float('inf')
            metrics['auc'] = 0.5
            metrics['brier_score'] = 0.25
        
        # Calibration evaluation
        fraction_pos, mean_pred_value = calibration_curve(
            t_true, propensity_pred, n_bins=10, strategy='quantile'
        )
        metrics['calibration_error'] = np.mean(np.abs(fraction_pos - mean_pred_value))
        
        # Overlap evaluation
        treated_scores = propensity_pred[t_true == 1]
        control_scores = propensity_pred[t_true == 0]
        
        if len(treated_scores) > 0 and len(control_scores) > 0:
            metrics['overlap_coefficient'] = self._calculate_overlap_coefficient(
                treated_scores, control_scores
            )
            
            # Extreme score violations
            metrics['extreme_scores_low'] = np.sum(propensity_pred < 0.05) / len(propensity_pred)
            metrics['extreme_scores_high'] = np.sum(propensity_pred > 0.95) / len(propensity_pred)
        
        # Balance evaluation (if covariates provided)
        if X is not None:
            balance_metrics = self._evaluate_covariate_balance(X, t_true, propensity_pred)
            metrics.update(balance_metrics)
        
        return metrics
    
    def evaluate_policy_performance(self, 
                                   cate_pred: np.ndarray,
                                   cate_true: Optional[np.ndarray] = None,
                                   treatment_cost: float = 0.0) -> Dict[str, float]:
        """
        Evaluate treatment assignment policy based on CATE predictions
        
        Args:
            cate_pred: Predicted conditional treatment effects
            cate_true: True conditional treatment effects (if available)
            treatment_cost: Cost of treatment
            
        Returns:
            Dictionary with policy evaluation metrics
        """
        metrics = {}
        
        # Optimal policy based on predictions
        optimal_policy_pred = (cate_pred > treatment_cost).astype(int)
        
        # Value of predicted policy
        policy_value_pred = np.mean(
            optimal_policy_pred * cate_pred - treatment_cost * optimal_policy_pred
        )
        metrics['predicted_policy_value'] = policy_value_pred
        
        # Treatment rate under policy
        metrics['treatment_rate'] = np.mean(optimal_policy_pred)
        
        if cate_true is not None:
            # True optimal policy
            optimal_policy_true = (cate_true > treatment_cost).astype(int)
            
            # Value of true optimal policy
            policy_value_true = np.mean(
                optimal_policy_true * cate_true - treatment_cost * optimal_policy_true
            )
            metrics['true_policy_value'] = policy_value_true
            
            # Policy regret
            regret = policy_value_true - np.mean(
                optimal_policy_pred * cate_true - treatment_cost * optimal_policy_pred
            )
            metrics['policy_regret'] = regret
            
            # Policy accuracy
            metrics['policy_accuracy'] = np.mean(optimal_policy_pred == optimal_policy_true)
            
            # Expected value of predicted policy under true CATE
            metrics['predicted_policy_true_value'] = np.mean(
                optimal_policy_pred * cate_true - treatment_cost * optimal_policy_pred
            )
        
        return metrics
    
    def evaluate_uncertainty_quantification(self, 
                                          cate_pred: np.ndarray,
                                          cate_lower: np.ndarray,
                                          cate_upper: np.ndarray,
                                          cate_true: Optional[np.ndarray] = None) -> Dict[str, float]:
        """
        Evaluate uncertainty quantification for CATE predictions
        
        Args:
            cate_pred: Point predictions for CATE
            cate_lower: Lower bounds of prediction intervals
            cate_upper: Upper bounds of prediction intervals
            cate_true: True CATE values (if available)
            
        Returns:
            Dictionary with uncertainty evaluation metrics
        """
        metrics = {}
        
        # Interval width
        interval_widths = cate_upper - cate_lower
        metrics['mean_interval_width'] = np.mean(interval_widths)
        metrics['median_interval_width'] = np.median(interval_widths)
        
        if cate_true is not None:
            # Coverage rate
            coverage = ((cate_true >= cate_lower) & (cate_true <= cate_upper)).astype(float)
            metrics['coverage_rate'] = np.mean(coverage)
            
            # Conditional coverage by prediction value
            sorted_indices = np.argsort(cate_pred)
            n_bins = 5
            bin_size = len(cate_pred) // n_bins
            
            for i in range(n_bins):
                start_idx = i * bin_size
                end_idx = (i + 1) * bin_size if i < n_bins - 1 else len(cate_pred)
                bin_indices = sorted_indices[start_idx:end_idx]
                
                bin_coverage = np.mean(coverage[bin_indices])
                metrics[f'coverage_bin_{i+1}'] = bin_coverage
            
            # Calibration error for intervals
            target_coverage = self.confidence_level
            metrics['coverage_error'] = abs(metrics['coverage_rate'] - target_coverage)
            
            # Efficiency (narrower intervals are better if coverage is maintained)
            if metrics['coverage_rate'] >= target_coverage - 0.05:  # Within 5% of target
                metrics['efficiency_score'] = 1.0 / metrics['mean_interval_width']
            else:
                metrics['efficiency_score'] = 0.0
        
        return metrics
    
    def compare_methods(self, 
                       results_dict: Dict[str, Dict[str, np.ndarray]],
                       cate_true: Optional[np.ndarray] = None) -> pd.DataFrame:
        """
        Compare multiple causal inference methods
        
        Args:
            results_dict: Dictionary mapping method names to result dictionaries
            cate_true: True CATE values for comparison
            
        Returns:
            DataFrame with comparison results
        """
        comparison_results = []
        
        for method_name, results in results_dict.items():
            method_metrics = {'method': method_name}
            
            # Basic metrics
            cate_pred = results.get('cate_pred')
            if cate_pred is not None:
                method_metrics['ate'] = np.mean(cate_pred)
                method_metrics['ate_std'] = np.std(cate_pred)
                
                if cate_true is not None:
                    method_metrics['pehe'] = np.sqrt(np.mean((cate_true - cate_pred) ** 2))
                    method_metrics['cate_r2'] = r2_score(cate_true, cate_pred)
                    
                    corr, p_value = stats.pearsonr(cate_true, cate_pred)
                    method_metrics['cate_correlation'] = corr
                    method_metrics['correlation_p_value'] = p_value
            
            # Policy metrics if available
            if 'policy_value' in results:
                method_metrics['policy_value'] = results['policy_value']
            if 'policy_regret' in results:
                method_metrics['policy_regret'] = results['policy_regret']
            
            comparison_results.append(method_metrics)
        
        return pd.DataFrame(comparison_results)
    
    def _calculate_overlap_coefficient(self, scores1: np.ndarray, scores2: np.ndarray) -> float:
        """Calculate overlap coefficient between two distributions"""
        try:
            from scipy.stats import gaussian_kde
            
            # Create KDE for both distributions
            kde1 = gaussian_kde(scores1)
            kde2 = gaussian_kde(scores2)
            
            # Evaluate on common grid
            x_min = min(scores1.min(), scores2.min())
            x_max = max(scores1.max(), scores2.max())
            x_grid = np.linspace(x_min, x_max, 1000)
            
            pdf1 = kde1(x_grid)
            pdf2 = kde2(x_grid)
            
            # Calculate overlap coefficient
            overlap = np.trapz(np.minimum(pdf1, pdf2), x_grid)
            return float(overlap)
            
        except Exception:
            # Fallback to empirical overlap
            combined = np.concatenate([scores1, scores2])
            hist1, bins = np.histogram(scores1, bins=50, density=True, range=(combined.min(), combined.max()))
            hist2, _ = np.histogram(scores2, bins=bins, density=True)
            
            bin_width = bins[1] - bins[0]
            overlap = np.sum(np.minimum(hist1, hist2)) * bin_width
            return float(overlap)
    
    def _evaluate_covariate_balance(self, 
                                  X: np.ndarray, 
                                  t: np.ndarray, 
                                  propensity_scores: np.ndarray,
                                  n_bins: int = 5) -> Dict[str, float]:
        """Evaluate covariate balance using propensity score stratification"""
        balance_metrics = {}
        
        # Sort by propensity scores and create bins
        sorted_indices = np.argsort(propensity_scores)
        bin_size = len(propensity_scores) // n_bins
        
        imbalances = []
        
        for i in range(n_bins):
            start_idx = i * bin_size
            end_idx = (i + 1) * bin_size if i < n_bins - 1 else len(propensity_scores)
            bin_indices = sorted_indices[start_idx:end_idx]
            
            X_bin = X[bin_indices]
            t_bin = t[bin_indices]
            
            if len(np.unique(t_bin)) > 1:  # Both treatment groups present
                treated_mask = t_bin == 1
                control_mask = t_bin == 0
                
                X_treated = X_bin[treated_mask]
                X_control = X_bin[control_mask]
                
                # Calculate standardized mean differences
                for j in range(X.shape[1]):
                    treated_mean = X_treated[:, j].mean()
                    control_mean = X_control[:, j].mean()
                    pooled_std = np.sqrt((X_treated[:, j].var() + X_control[:, j].var()) / 2)
                    
                    if pooled_std > 0:
                        smd = abs(treated_mean - control_mean) / pooled_std
                        imbalances.append(smd)
        
        if imbalances:
            balance_metrics['mean_smd'] = np.mean(imbalances)
            balance_metrics['max_smd'] = np.max(imbalances)
            balance_metrics['balanced_covariates'] = np.mean(np.array(imbalances) < 0.1)
        
        return balance_metrics
    
    def generate_evaluation_report(self, 
                                  metrics: CausalMetrics,
                                  method_name: str = "CANS") -> str:
        """Generate human-readable evaluation report"""
        report = f"\n{'='*60}\n"
        report += f"CAUSAL EVALUATION REPORT - {method_name}\n"
        report += f"{'='*60}\n\n"
        
        # Treatment Effects
        report += "TREATMENT EFFECT ESTIMATES:\n"
        report += f"  Average Treatment Effect (ATE): {metrics.ate:.4f} ± {metrics.ate_std:.4f}\n"
        report += f"  95% Confidence Interval: [{metrics.ate_ci_lower:.4f}, {metrics.ate_ci_upper:.4f}]\n"
        if metrics.att != 0:
            report += f"  ATT (Effect on Treated): {metrics.att:.4f}\n"
        if metrics.atc != 0:
            report += f"  ATC (Effect on Controls): {metrics.atc:.4f}\n\n"
        
        # Model Performance
        report += "MODEL PERFORMANCE:\n"
        report += f"  Factual Prediction MSE: {metrics.factual_mse:.4f}\n"
        report += f"  Factual Prediction MAE: {metrics.factual_mae:.4f}\n"
        if metrics.pehe > 0:
            report += f"  PEHE (Heterogeneous Effect Error): {metrics.pehe:.4f}\n"
            report += f"  CATE R²: {metrics.cate_r2:.4f}\n"
            report += f"  CATE Correlation: {metrics.cate_correlation:.4f}\n\n"
        
        # Policy Performance
        if metrics.policy_value != 0:
            report += "POLICY EVALUATION:\n"
            report += f"  Policy Value: {metrics.policy_value:.4f}\n"
            if metrics.policy_regret > 0:
                report += f"  Policy Regret: {metrics.policy_regret:.4f}\n\n"
        
        # Assessment Summary
        report += "ASSESSMENT SUMMARY:\n"
        
        if metrics.pehe > 0:
            if metrics.pehe_normalized < 0.5:
                report += "  ✓ Excellent CATE estimation performance\n"
            elif metrics.pehe_normalized < 1.0:
                report += "  ⚠ Moderate CATE estimation performance\n"
            else:
                report += "  ✗ Poor CATE estimation performance\n"
        
        if metrics.cate_correlation > 0.7:
            report += "  ✓ Strong correlation with true treatment effects\n"
        elif metrics.cate_correlation > 0.3:
            report += "  ⚠ Moderate correlation with true treatment effects\n"
        elif metrics.cate_correlation > 0:
            report += "  ✗ Weak correlation with true treatment effects\n"
        
        if metrics.overlap_coefficient > 0.8:
            report += "  ✓ Good propensity score overlap\n"
        elif metrics.overlap_coefficient > 0.5:
            report += "  ⚠ Moderate propensity score overlap\n"
        elif metrics.overlap_coefficient > 0:
            report += "  ✗ Poor propensity score overlap\n"
        
        report += f"\n{'='*60}\n"
        
        return report


def bootstrap_ate_confidence_interval(cate_estimates: np.ndarray, 
                                    n_bootstrap: int = 1000,
                                    confidence_level: float = 0.95) -> Tuple[float, float]:
    """
    Calculate bootstrap confidence interval for ATE
    
    Args:
        cate_estimates: Array of CATE estimates
        n_bootstrap: Number of bootstrap samples
        confidence_level: Confidence level
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    bootstrap_ates = []
    
    for _ in range(n_bootstrap):
        bootstrap_sample = np.random.choice(cate_estimates, size=len(cate_estimates), replace=True)
        bootstrap_ates.append(np.mean(bootstrap_sample))
    
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    lower_bound = np.percentile(bootstrap_ates, lower_percentile)
    upper_bound = np.percentile(bootstrap_ates, upper_percentile)
    
    return lower_bound, upper_bound


def permutation_test_ate(cate_estimates: np.ndarray, 
                        null_ate: float = 0.0,
                        n_permutations: int = 1000) -> Tuple[float, float]:
    """
    Permutation test for ATE significance
    
    Args:
        cate_estimates: Array of CATE estimates
        null_ate: Null hypothesis ATE value
        n_permutations: Number of permutation samples
        
    Returns:
        Tuple of (test_statistic, p_value)
    """
    observed_ate = np.mean(cate_estimates)
    test_statistic = observed_ate - null_ate
    
    # Center the data under null hypothesis
    centered_estimates = cate_estimates - observed_ate + null_ate
    
    permutation_stats = []
    for _ in range(n_permutations):
        # Random signs (equivalent to permuting treatment labels)
        signs = np.random.choice([-1, 1], size=len(centered_estimates))
        perm_sample = signs * centered_estimates
        perm_ate = np.mean(perm_sample)
        permutation_stats.append(perm_ate - null_ate)
    
    # Calculate p-value (two-tailed)
    p_value = np.mean(np.abs(permutation_stats) >= np.abs(test_statistic))
    
    return test_statistic, p_value