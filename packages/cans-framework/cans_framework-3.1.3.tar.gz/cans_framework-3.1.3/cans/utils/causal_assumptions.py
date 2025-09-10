"""
Causal assumption testing utilities for CANS framework.
Implements tests for fundamental causal inference assumptions.
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
import warnings

from ..exceptions import ValidationError


class CausalAssumptionTester:
    """Test fundamental causal inference assumptions"""
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize assumption tester
        
        Args:
            alpha: Significance level for statistical tests
        """
        self.alpha = alpha
    
    def test_unconfoundedness(self, 
                            X: np.ndarray, 
                            T: np.ndarray, 
                            Y: np.ndarray,
                            method: str = 'placebo') -> Dict[str, Any]:
        """
        Test unconfoundedness assumption (Y₀, Y₁) ⊥ T | X
        
        Args:
            X: Covariates [n_samples, n_features]
            T: Treatment assignments [n_samples]
            Y: Observed outcomes [n_samples]
            method: Test method ('placebo', 'falsification', 'balance')
            
        Returns:
            Dictionary with test results
        """
        if method == 'placebo':
            return self._placebo_test(X, T, Y)
        elif method == 'falsification':
            return self._falsification_test(X, T, Y)
        elif method == 'balance':
            return self._balance_test(X, T)
        else:
            raise ValueError(f"Unknown test method: {method}")
    
    def _placebo_test(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray) -> Dict[str, Any]:
        """Placebo treatment test using pre-treatment outcomes"""
        # Split features into pre and post treatment (simplified assumption)
        mid_point = X.shape[1] // 2
        X_pre = X[:, :mid_point]
        X_post = X[:, mid_point:]
        
        # Create placebo treatment from pre-treatment features
        placebo_model = RandomForestClassifier(n_estimators=100, random_state=42)
        placebo_model.fit(X_pre, T)
        T_placebo = placebo_model.predict(X_pre)
        
        # Test if placebo treatment predicts outcome
        outcome_model = RandomForestRegressor(n_estimators=100, random_state=42)
        X_with_placebo = np.column_stack([X_pre, T_placebo])
        scores = cross_val_score(outcome_model, X_with_placebo, Y, cv=5, scoring='r2')
        
        # Compare with null model (no treatment)
        null_scores = cross_val_score(outcome_model, X_pre, Y, cv=5, scoring='r2')
        
        # Statistical test
        t_stat, p_value = stats.ttest_rel(scores, null_scores)
        
        return {
            'test_name': 'Placebo Test',
            'test_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'interpretation': 'Reject unconfoundedness' if p_value < self.alpha else 'Fail to reject unconfoundedness',
            'placebo_r2': np.mean(scores),
            'null_r2': np.mean(null_scores),
            'warning': 'Placebo test assumes features can be split into pre/post treatment'
        }
    
    def _falsification_test(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray) -> Dict[str, Any]:
        """Test using irrelevant outcomes that shouldn't be affected by treatment"""
        # Create synthetic irrelevant outcome from pre-treatment features only
        Y_irrelevant = np.random.normal(X.mean(axis=1), 0.1)
        
        # Test treatment effect on irrelevant outcome
        treated_mean = Y_irrelevant[T == 1].mean()
        control_mean = Y_irrelevant[T == 0].mean()
        
        # T-test for difference
        t_stat, p_value = stats.ttest_ind(Y_irrelevant[T == 1], Y_irrelevant[T == 0])
        
        return {
            'test_name': 'Falsification Test',
            'test_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'interpretation': 'Evidence of confounding' if p_value < self.alpha else 'No evidence of confounding',
            'treated_mean': treated_mean,
            'control_mean': control_mean,
            'effect_size': treated_mean - control_mean
        }
    
    def _balance_test(self, X: np.ndarray, T: np.ndarray) -> Dict[str, Any]:
        """Test covariate balance between treatment groups"""
        results = {}
        p_values = []
        
        for i in range(X.shape[1]):
            covariate = X[:, i]
            treated = covariate[T == 1]
            control = covariate[T == 0]
            
            # Two-sample t-test
            t_stat, p_value = stats.ttest_ind(treated, control)
            p_values.append(p_value)
            
            results[f'covariate_{i}'] = {
                'test_statistic': t_stat,
                'p_value': p_value,
                'treated_mean': treated.mean(),
                'control_mean': control.mean(),
                'standardized_diff': (treated.mean() - control.mean()) / np.sqrt((treated.var() + control.var()) / 2)
            }
        
        # Multiple testing correction (Bonferroni)
        corrected_alpha = self.alpha / len(p_values)
        significant_vars = sum(1 for p in p_values if p < corrected_alpha)
        
        return {
            'test_name': 'Covariate Balance Test',
            'significant_covariates': significant_vars,
            'total_covariates': len(p_values),
            'corrected_alpha': corrected_alpha,
            'min_p_value': min(p_values),
            'interpretation': f'{significant_vars} covariates significantly imbalanced' if significant_vars > 0 else 'Covariates appear balanced',
            'covariate_results': results
        }
    
    def test_positivity(self, 
                       X: np.ndarray, 
                       T: np.ndarray, 
                       min_prob: float = 0.05) -> Dict[str, Any]:
        """
        Test positivity assumption: 0 < P(T=1|X) < 1
        
        Args:
            X: Covariates
            T: Treatment assignments
            min_prob: Minimum probability threshold
            
        Returns:
            Positivity test results
        """
        # Estimate propensity scores
        propensity_model = LogisticRegression(max_iter=1000, random_state=42)
        propensity_model.fit(X, T)
        propensity_scores = propensity_model.predict_proba(X)[:, 1]
        
        # Check violations
        violations_low = (propensity_scores < min_prob).sum()
        violations_high = (propensity_scores > (1 - min_prob)).sum()
        total_violations = violations_low + violations_high
        
        # Calculate overlap statistics
        treated_scores = propensity_scores[T == 1]
        control_scores = propensity_scores[T == 0]
        
        # Overlap measures
        overlap_coefficient = self._calculate_overlap_coefficient(treated_scores, control_scores)
        
        return {
            'test_name': 'Positivity Test',
            'total_samples': len(T),
            'violations_low': int(violations_low),
            'violations_high': int(violations_high),
            'total_violations': int(total_violations),
            'violation_rate': total_violations / len(T),
            'min_propensity': propensity_scores.min(),
            'max_propensity': propensity_scores.max(),
            'overlap_coefficient': overlap_coefficient,
            'positivity_satisfied': total_violations == 0,
            'interpretation': f'{total_violations} samples violate positivity assumption' if total_violations > 0 else 'Positivity assumption satisfied'
        }
    
    def _calculate_overlap_coefficient(self, scores1: np.ndarray, scores2: np.ndarray) -> float:
        """Calculate overlap coefficient between two distributions"""
        from scipy.stats import gaussian_kde
        
        try:
            # Create KDE for both distributions
            kde1 = gaussian_kde(scores1)
            kde2 = gaussian_kde(scores2)
            
            # Evaluate on common grid
            x_min = min(scores1.min(), scores2.min())
            x_max = max(scores1.max(), scores2.max())
            x_grid = np.linspace(x_min, x_max, 100)
            
            pdf1 = kde1(x_grid)
            pdf2 = kde2(x_grid)
            
            # Calculate overlap coefficient
            overlap = np.trapz(np.minimum(pdf1, pdf2), x_grid)
            return float(overlap)
            
        except Exception:
            # Fallback to simple overlap measure
            return 1.0 - abs(scores1.mean() - scores2.mean())
    
    def test_sutva(self, 
                   X: np.ndarray, 
                   T: np.ndarray, 
                   Y: np.ndarray,
                   spatial_coords: Optional[np.ndarray] = None,
                   network_edges: Optional[List[Tuple[int, int]]] = None) -> Dict[str, Any]:
        """
        Test SUTVA (Stable Unit Treatment Value Assumption)
        
        Args:
            X: Covariates
            T: Treatment assignments
            Y: Outcomes
            spatial_coords: Spatial coordinates for spillover detection
            network_edges: Network edges for interference detection
            
        Returns:
            SUTVA test results
        """
        results = {
            'test_name': 'SUTVA Test',
            'interference_detected': False,
            'spillover_effects': {}
        }
        
        # Test for spatial spillovers
        if spatial_coords is not None:
            spatial_results = self._test_spatial_spillovers(X, T, Y, spatial_coords)
            results['spatial_spillovers'] = spatial_results
            if spatial_results['significant']:
                results['interference_detected'] = True
        
        # Test for network interference
        if network_edges is not None:
            network_results = self._test_network_interference(X, T, Y, network_edges)
            results['network_interference'] = network_results
            if network_results['significant']:
                results['interference_detected'] = True
        
        # Test for treatment heterogeneity (multiple versions)
        heterogeneity_results = self._test_treatment_heterogeneity(X, T, Y)
        results['treatment_heterogeneity'] = heterogeneity_results
        
        results['interpretation'] = 'SUTVA violations detected' if results['interference_detected'] else 'No clear SUTVA violations'
        
        return results
    
    def _test_spatial_spillovers(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray, coords: np.ndarray) -> Dict[str, Any]:
        """Test for spatial spillover effects"""
        from scipy.spatial.distance import pdist, squareform
        
        # Calculate distance matrix
        distances = squareform(pdist(coords))
        
        # For each unit, calculate treatment intensity of neighbors
        neighbor_threshold = np.percentile(distances[distances > 0], 25)  # 25th percentile as threshold
        
        spillover_effects = []
        for i in range(len(Y)):
            neighbors = np.where((distances[i] < neighbor_threshold) & (distances[i] > 0))[0]
            if len(neighbors) > 0:
                neighbor_treatment_rate = T[neighbors].mean()
                spillover_effects.append(neighbor_treatment_rate)
            else:
                spillover_effects.append(0.0)
        
        spillover_effects = np.array(spillover_effects)
        
        # Test correlation between spillover and outcomes
        correlation, p_value = stats.pearsonr(spillover_effects, Y)
        
        return {
            'correlation': correlation,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'neighbor_threshold': neighbor_threshold,
            'avg_spillover_effect': spillover_effects.mean()
        }
    
    def _test_network_interference(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray, edges: List[Tuple[int, int]]) -> Dict[str, Any]:
        """Test for network-based interference"""
        import networkx as nx
        
        # Build network
        G = nx.Graph()
        G.add_nodes_from(range(len(Y)))
        G.add_edges_from(edges)
        
        # Calculate network treatment exposure
        network_exposure = []
        for i in range(len(Y)):
            neighbors = list(G.neighbors(i))
            if neighbors:
                exposure = T[neighbors].mean()
            else:
                exposure = 0.0
            network_exposure.append(exposure)
        
        network_exposure = np.array(network_exposure)
        
        # Test effect of network exposure on outcomes
        correlation, p_value = stats.pearsonr(network_exposure, Y)
        
        return {
            'correlation': correlation,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'avg_network_exposure': network_exposure.mean(),
            'network_density': nx.density(G)
        }
    
    def _test_treatment_heterogeneity(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray) -> Dict[str, Any]:
        """Test for treatment version heterogeneity"""
        # Test if treatment effects vary significantly across subgroups
        unique_treatments = np.unique(T)
        
        if len(unique_treatments) <= 2:
            # Binary treatment - test for heterogeneity across covariate subgroups
            # Split by median of first covariate
            if X.shape[1] > 0:
                median_val = np.median(X[:, 0])
                subgroup1 = X[:, 0] <= median_val
                subgroup2 = X[:, 0] > median_val
                
                # Calculate treatment effects in each subgroup
                effect1 = Y[(T == 1) & subgroup1].mean() - Y[(T == 0) & subgroup1].mean()
                effect2 = Y[(T == 1) & subgroup2].mean() - Y[(T == 0) & subgroup2].mean()
                
                # Test difference in effects
                effect_diff = abs(effect1 - effect2)
                
                # Simplified test - in practice would use more sophisticated methods
                heterogeneity_detected = effect_diff > Y.std() * 0.5
                
                return {
                    'heterogeneity_detected': heterogeneity_detected,
                    'effect_subgroup1': effect1,
                    'effect_subgroup2': effect2,
                    'effect_difference': effect_diff,
                    'interpretation': 'Treatment effects vary across subgroups' if heterogeneity_detected else 'Treatment effects appear homogeneous'
                }
        
        return {
            'heterogeneity_detected': False,
            'interpretation': 'Insufficient variation to test treatment heterogeneity'
        }
    
    def comprehensive_test(self, 
                          X: np.ndarray, 
                          T: np.ndarray, 
                          Y: np.ndarray,
                          **kwargs) -> Dict[str, Any]:
        """
        Run comprehensive causal assumption tests
        
        Args:
            X: Covariates
            T: Treatment assignments  
            Y: Outcomes
            **kwargs: Additional arguments for specific tests
            
        Returns:
            Complete test results
        """
        results = {
            'sample_size': len(Y),
            'treatment_proportion': T.mean(),
            'outcome_statistics': {
                'mean': Y.mean(),
                'std': Y.std(),
                'min': Y.min(),
                'max': Y.max()
            }
        }
        
        # Run all assumption tests
        try:
            results['unconfoundedness'] = self.test_unconfoundedness(X, T, Y)
        except Exception as e:
            results['unconfoundedness'] = {'error': str(e)}
        
        try:
            results['positivity'] = self.test_positivity(X, T)
        except Exception as e:
            results['positivity'] = {'error': str(e)}
        
        try:
            results['sutva'] = self.test_sutva(X, T, Y, **kwargs)
        except Exception as e:
            results['sutva'] = {'error': str(e)}
        
        # Overall assessment
        violations = []
        if results.get('unconfoundedness', {}).get('significant', False):
            violations.append('Unconfoundedness')
        if not results.get('positivity', {}).get('positivity_satisfied', True):
            violations.append('Positivity')
        if results.get('sutva', {}).get('interference_detected', False):
            violations.append('SUTVA')
        
        results['assumption_violations'] = violations
        results['causal_identification_valid'] = len(violations) == 0
        results['recommendations'] = self._generate_recommendations(violations)
        
        return results
    
    def _generate_recommendations(self, violations: List[str]) -> List[str]:
        """Generate recommendations based on assumption violations"""
        recommendations = []
        
        if 'Unconfoundedness' in violations:
            recommendations.extend([
                'Consider instrumental variable methods',
                'Add more confounders to the model',
                'Use regression discontinuity if applicable',
                'Apply sensitivity analysis for unmeasured confounding'
            ])
        
        if 'Positivity' in violations:
            recommendations.extend([
                'Trim extreme propensity scores',
                'Use overlap weighting instead of IPW',
                'Consider matching methods with caliper',
                'Restrict analysis to common support region'
            ])
        
        if 'SUTVA' in violations:
            recommendations.extend([
                'Model interference effects explicitly',
                'Use clustered or hierarchical treatment designs',
                'Apply spillover-robust estimation methods',
                'Consider network-based causal inference'
            ])
        
        if not violations:
            recommendations.append('All assumptions appear satisfied - proceed with causal analysis')
        
        return recommendations


def validate_causal_assumptions(X: np.ndarray, 
                              T: np.ndarray, 
                              Y: np.ndarray,
                              **kwargs) -> Dict[str, Any]:
    """
    Convenience function for comprehensive assumption testing
    
    Args:
        X: Covariates [n_samples, n_features]
        T: Treatment assignments [n_samples]
        Y: Outcomes [n_samples]
        **kwargs: Additional test parameters
        
    Returns:
        Complete assumption test results
    """
    tester = CausalAssumptionTester()
    return tester.comprehensive_test(X, T, Y, **kwargs)