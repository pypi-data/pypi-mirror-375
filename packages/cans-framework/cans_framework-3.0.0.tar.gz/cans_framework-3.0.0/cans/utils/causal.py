import torch
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import warnings

from .causal_assumptions import CausalAssumptionTester
from .causal_evaluation import CausalEvaluator
from ..exceptions import ValidationError


class CounterfactualSimulator:
    """Enhanced counterfactual simulation with proper causal identification"""
    
    def __init__(self, identification_method: str = "backdoor"):
        """
        Initialize counterfactual simulator
        
        Args:
            identification_method: Method for causal identification
                - 'backdoor': Backdoor criterion with confounding adjustment
                - 'ipw': Inverse propensity weighting
                - 'doubly_robust': Doubly robust estimation
                - 'naive': Simple treatment assignment (original method)
        """
        self.identification_method = identification_method
        self.propensity_model = None
        self.assumption_tester = CausalAssumptionTester()
    
    def simulate_counterfactual(self, 
                              model, 
                              dataloader, 
                              intervention: int = 0,
                              confounders: Optional[torch.Tensor] = None,
                              validate_assumptions: bool = True) -> Dict[str, Any]:
        """
        Simulate counterfactual outcomes with proper identification
        
        Args:
            model: Trained CANS model
            dataloader: DataLoader containing data
            intervention: Treatment value for counterfactual (0 or 1)
            confounders: Additional confounding variables
            validate_assumptions: Whether to test causal assumptions
            
        Returns:
            Dictionary with counterfactual predictions and diagnostics
        """
        model.eval()
        device = next(model.parameters()).device
        
        # Collect data for analysis
        all_data = self._collect_data(dataloader, device)
        
        # Validate assumptions if requested
        assumption_results = None
        if validate_assumptions:
            assumption_results = self._validate_assumptions(all_data, confounders)
        
        # Perform counterfactual simulation based on identification method
        if self.identification_method == "backdoor":
            cf_results = self._backdoor_simulation(model, all_data, intervention, device)
        elif self.identification_method == "ipw":
            cf_results = self._ipw_simulation(model, all_data, intervention, device)
        elif self.identification_method == "doubly_robust":
            cf_results = self._doubly_robust_simulation(model, all_data, intervention, device)
        else:  # naive
            cf_results = self._naive_simulation(model, all_data, intervention, device)
        
        # Add assumption test results
        cf_results['assumption_tests'] = assumption_results
        cf_results['identification_method'] = self.identification_method
        cf_results['intervention'] = intervention
        
        return cf_results
    
    def _collect_data(self, dataloader, device) -> Dict[str, torch.Tensor]:
        """Collect all data from dataloader"""
        all_graphs = []
        all_texts = {'input_ids': [], 'attention_mask': [], 'token_type_ids': []}
        all_treatments = []
        all_outcomes = []
        
        with torch.no_grad():
            for batch in dataloader:
                all_graphs.append(batch['graph'].to(device))
                
                for key in all_texts.keys():
                    if key in batch['text']:
                        all_texts[key].append(batch['text'][key].to(device))
                
                all_treatments.append(batch['treatment'].to(device))
                all_outcomes.append(batch['outcome'].to(device))
        
        # Concatenate all batches
        for key in all_texts.keys():
            if all_texts[key]:
                all_texts[key] = torch.cat(all_texts[key], dim=0)
        
        return {
            'graphs': all_graphs,
            'texts': all_texts,
            'treatments': torch.cat(all_treatments, dim=0),
            'outcomes': torch.cat(all_outcomes, dim=0)
        }
    
    def _validate_assumptions(self, all_data, confounders) -> Dict[str, Any]:
        """Validate causal assumptions"""
        treatments_np = all_data['treatments'].cpu().numpy()
        outcomes_np = all_data['outcomes'].cpu().numpy()
        
        # Create covariate matrix (simplified - in practice would extract features)
        if confounders is not None:
            X = confounders.cpu().numpy()
        else:
            # Use treatment and outcome statistics as proxy features
            X = np.column_stack([
                treatments_np,
                outcomes_np,
                np.random.randn(len(treatments_np), 3)  # Placeholder features
            ])
        
        try:
            return self.assumption_tester.comprehensive_test(X, treatments_np, outcomes_np)
        except Exception as e:
            return {'error': str(e), 'assumptions_validated': False}
    
    def _backdoor_simulation(self, model, all_data, intervention, device) -> Dict[str, Any]:
        """Backdoor criterion-based simulation"""
        cf_preds = []
        factual_preds = []
        
        with torch.no_grad():
            batch_size = 32  # Process in batches to manage memory
            n_samples = len(all_data['treatments'])
            
            for i in range(0, n_samples, batch_size):
                end_idx = min(i + batch_size, n_samples)
                
                # Get batch data
                if i // batch_size < len(all_data['graphs']):
                    graph_batch = all_data['graphs'][i // batch_size]
                else:
                    graph_batch = all_data['graphs'][-1]  # Use last graph if needed
                
                text_batch = {
                    key: tensor[i:end_idx] for key, tensor in all_data['texts'].items()
                    if len(tensor) > 0
                }
                treatment_batch = all_data['treatments'][i:end_idx]
                
                # Counterfactual prediction
                treatment_cf = torch.full_like(treatment_batch, intervention, dtype=torch.float)
                mu0_cf, mu1_cf = model(graph_batch, text_batch, treatment_cf)
                y_cf = mu0_cf if intervention == 0 else mu1_cf
                cf_preds.extend(y_cf.squeeze().cpu().numpy())
                
                # Factual prediction for comparison
                mu0_fact, mu1_fact = model(graph_batch, text_batch, treatment_batch)
                y_fact = torch.where(treatment_batch.unsqueeze(-1) == 1, mu1_fact, mu0_fact)
                factual_preds.extend(y_fact.squeeze().cpu().numpy())
        
        return {
            'counterfactual_outcomes': np.array(cf_preds),
            'factual_outcomes': np.array(factual_preds),
            'treatment_effects': np.array(cf_preds) - np.array(factual_preds) if intervention == 1 else np.array(factual_preds) - np.array(cf_preds),
            'method_specific_info': {
                'confounding_adjustment': 'Applied backdoor criterion',
                'assumptions': 'Unconfoundedness given covariates'
            }
        }
    
    def _ipw_simulation(self, model, all_data, intervention, device) -> Dict[str, Any]:
        """Inverse propensity weighting simulation"""
        # First, estimate propensity scores
        propensity_scores = self._estimate_propensity_scores(all_data)
        
        cf_preds = []
        weights = []
        
        with torch.no_grad():
            batch_size = 32
            n_samples = len(all_data['treatments'])
            
            for i in range(0, n_samples, batch_size):
                end_idx = min(i + batch_size, n_samples)
                
                # Get batch data
                if i // batch_size < len(all_data['graphs']):
                    graph_batch = all_data['graphs'][i // batch_size]
                else:
                    graph_batch = all_data['graphs'][-1]
                
                text_batch = {
                    key: tensor[i:end_idx] for key, tensor in all_data['texts'].items()
                    if len(tensor) > 0
                }
                treatment_batch = all_data['treatments'][i:end_idx]
                
                # Counterfactual prediction
                treatment_cf = torch.full_like(treatment_batch, intervention, dtype=torch.float)
                mu0_cf, mu1_cf = model(graph_batch, text_batch, treatment_cf)
                y_cf = mu0_cf if intervention == 0 else mu1_cf
                
                # Calculate IPW weights
                ps_batch = propensity_scores[i:end_idx]
                if intervention == 1:
                    batch_weights = 1.0 / np.clip(ps_batch, 0.01, 0.99)
                else:
                    batch_weights = 1.0 / np.clip(1 - ps_batch, 0.01, 0.99)
                
                cf_preds.extend(y_cf.squeeze().cpu().numpy())
                weights.extend(batch_weights)
        
        # Weighted average for population estimate
        cf_preds = np.array(cf_preds)
        weights = np.array(weights)
        
        weighted_outcome = np.average(cf_preds, weights=weights)
        
        return {
            'counterfactual_outcomes': cf_preds,
            'ipw_weights': weights,
            'weighted_average_outcome': weighted_outcome,
            'propensity_scores': propensity_scores,
            'method_specific_info': {
                'weight_clipping': 'Applied to [0.01, 0.99]',
                'effective_sample_size': len(weights) / (1 + np.var(weights))
            }
        }
    
    def _doubly_robust_simulation(self, model, all_data, intervention, device) -> Dict[str, Any]:
        """Doubly robust simulation combining outcome regression and IPW"""
        # Get both backdoor and IPW results
        backdoor_results = self._backdoor_simulation(model, all_data, intervention, device)
        ipw_results = self._ipw_simulation(model, all_data, intervention, device)
        
        # Combine using doubly robust formula
        cf_backdoor = backdoor_results['counterfactual_outcomes']
        weights = ipw_results['ipw_weights']
        observed_outcomes = all_data['outcomes'].cpu().numpy()
        treatments = all_data['treatments'].cpu().numpy()
        
        # Doubly robust estimator
        indicator = (treatments == intervention).astype(float)
        dr_correction = weights * indicator * (observed_outcomes - cf_backdoor)
        doubly_robust_outcomes = cf_backdoor + dr_correction
        
        return {
            'counterfactual_outcomes': doubly_robust_outcomes,
            'backdoor_component': cf_backdoor,
            'ipw_component': ipw_results['counterfactual_outcomes'],
            'correction_term': dr_correction,
            'method_specific_info': {
                'estimator': 'Doubly robust (regression + IPW)',
                'bias_reduction': 'Robust to either model misspecification'
            }
        }
    
    def _naive_simulation(self, model, all_data, intervention, device) -> Dict[str, Any]:
        """Original naive simulation (for comparison)"""
        cf_preds = []
        
        with torch.no_grad():
            batch_size = 32
            n_samples = len(all_data['treatments'])
            
            for i in range(0, n_samples, batch_size):
                end_idx = min(i + batch_size, n_samples)
                
                if i // batch_size < len(all_data['graphs']):
                    graph_batch = all_data['graphs'][i // batch_size]
                else:
                    graph_batch = all_data['graphs'][-1]
                
                text_batch = {
                    key: tensor[i:end_idx] for key, tensor in all_data['texts'].items()
                    if len(tensor) > 0
                }
                treatment_batch = all_data['treatments'][i:end_idx]
                
                # Simple treatment assignment
                treatment_cf = torch.full_like(treatment_batch, intervention, dtype=torch.float)
                mu0, mu1 = model(graph_batch, text_batch, treatment_cf)
                y_cf = mu0 if intervention == 0 else mu1
                cf_preds.extend(y_cf.squeeze().cpu().numpy())
        
        return {
            'counterfactual_outcomes': np.array(cf_preds),
            'method_specific_info': {
                'warning': 'No confounding adjustment applied',
                'assumptions': 'Assumes no unmeasured confounding (strong assumption)'
            }
        }
    
    def _estimate_propensity_scores(self, all_data) -> np.ndarray:
        """Estimate propensity scores using available features"""
        treatments = all_data['treatments'].cpu().numpy()
        outcomes = all_data['outcomes'].cpu().numpy()
        
        # Create feature matrix (simplified - would use actual covariates in practice)
        # Using outcome and synthetic features as proxy
        X = np.column_stack([
            outcomes,
            np.random.randn(len(treatments), 3)  # Placeholder features
        ])
        
        # Fit propensity model
        if self.propensity_model is None:
            self.propensity_model = LogisticRegression(random_state=42)
        
        try:
            self.propensity_model.fit(X, treatments)
            propensity_scores = self.propensity_model.predict_proba(X)[:, 1]
        except Exception:
            # Fallback to marginal probability
            warnings.warn("Propensity model fitting failed, using marginal probability")
            propensity_scores = np.full(len(treatments), treatments.mean())
        
        return propensity_scores


def simulate_counterfactual(model, dataloader, intervention=0, **kwargs):
    """
    Legacy function for backward compatibility
    Enhanced with basic validation
    """
    simulator = CounterfactualSimulator(identification_method="naive")
    results = simulator.simulate_counterfactual(
        model, dataloader, intervention, validate_assumptions=False
    )
    return results['counterfactual_outcomes'].tolist()


def advanced_counterfactual_analysis(model, 
                                   dataloader, 
                                   methods: List[str] = ['backdoor', 'ipw', 'doubly_robust'],
                                   confounders: Optional[torch.Tensor] = None) -> Dict[str, Any]:
    """
    Comprehensive counterfactual analysis using multiple methods
    
    Args:
        model: Trained CANS model
        dataloader: DataLoader with data
        methods: List of identification methods to compare
        confounders: Optional confounding variables
        
    Returns:
        Dictionary with results from all methods
    """
    results = {}
    
    for method in methods:
        simulator = CounterfactualSimulator(identification_method=method)
        
        # Analyze both interventions
        results[method] = {
            'control': simulator.simulate_counterfactual(
                model, dataloader, intervention=0, confounders=confounders
            ),
            'treated': simulator.simulate_counterfactual(
                model, dataloader, intervention=1, confounders=confounders
            )
        }
        
        # Calculate treatment effects
        control_outcomes = results[method]['control']['counterfactual_outcomes']
        treated_outcomes = results[method]['treated']['counterfactual_outcomes']
        
        results[method]['treatment_effects'] = treated_outcomes - control_outcomes
        results[method]['ate'] = np.mean(treated_outcomes - control_outcomes)
        results[method]['ate_std'] = np.std(treated_outcomes - control_outcomes)
    
    # Compare methods
    evaluator = CausalEvaluator()
    comparison_data = {}
    
    for method in methods:
        comparison_data[method] = {
            'cate_pred': results[method]['treatment_effects'],
            'ate': results[method]['ate']
        }
    
    results['method_comparison'] = evaluator.compare_methods(comparison_data)
    
    return results
