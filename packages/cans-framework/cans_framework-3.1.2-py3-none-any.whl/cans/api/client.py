"""
CANS API Client

Python client library for interacting with the CANS REST API.
"""

import requests
import pandas as pd
import json
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CANSAPIException(Exception):
    """Custom exception for CANS API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class CANSAPIClient:
    """Client for CANS REST API."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 300
    ):
        """
        Initialize CANS API client.
        
        Args:
            base_url: Base URL of the CANS API server
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        files: Optional[dict] = None
    ) -> dict:
        """Make HTTP request to API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                if files:
                    # Remove Content-Type header for file uploads
                    headers = self.session.headers.copy()
                    headers.pop('Content-Type', None)
                    response = self.session.post(
                        url, data=data, files=files, headers=headers, timeout=self.timeout
                    )
                else:
                    response = self.session.post(url, json=data, timeout=self.timeout)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check for HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f'HTTP {response.status_code}')
                except:
                    error_msg = f'HTTP {response.status_code}: {response.text}'
                
                raise CANSAPIException(
                    error_msg,
                    status_code=response.status_code,
                    response=error_data if 'error_data' in locals() else None
                )
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise CANSAPIException("Request timeout")
        except requests.exceptions.ConnectionError:
            raise CANSAPIException(f"Connection error to {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise CANSAPIException(f"Request failed: {str(e)}")
    
    def health_check(self) -> dict:
        """Check API health status."""
        return self._make_request('GET', '/health')
    
    def validate_assumptions(
        self,
        data: Union[pd.DataFrame, str, List[dict]],
        treatment_column: str,
        outcome_column: str,
        feature_columns: Optional[List[str]] = None,
        verbose: bool = False
    ) -> dict:
        """
        Validate causal assumptions for a dataset.
        
        Args:
            data: Dataset as DataFrame, file path, or list of dicts
            treatment_column: Name of treatment column
            outcome_column: Name of outcome column
            feature_columns: List of feature column names
            verbose: Enable verbose output
            
        Returns:
            Validation results dict
        """
        # Prepare dataset request
        if isinstance(data, pd.DataFrame):
            data_list = data.to_dict('records')
        elif isinstance(data, str):
            data_list = data  # File path
        else:
            data_list = data
        
        request_data = {
            "dataset": {
                "data": data_list,
                "treatment_column": treatment_column,
                "outcome_column": outcome_column,
                "feature_columns": feature_columns
            },
            "verbose": verbose
        }
        
        return self._make_request('POST', '/validate', data=request_data)
    
    def train_model(
        self,
        data: Union[pd.DataFrame, str, List[dict]],
        treatment_column: str,
        outcome_column: str,
        feature_columns: Optional[List[str]] = None,
        text_column: Optional[str] = None,
        model_config: Optional[dict] = None,
        training_config: Optional[dict] = None,
        experiment_name: Optional[str] = None
    ) -> dict:
        """
        Train a CANS model.
        
        Args:
            data: Dataset as DataFrame, file path, or list of dicts
            treatment_column: Name of treatment column
            outcome_column: Name of outcome column
            feature_columns: List of feature column names
            text_column: Name of text column
            model_config: Model configuration dict
            training_config: Training configuration dict
            experiment_name: Name for experiment tracking
            
        Returns:
            Training results dict
        """
        # Prepare dataset
        if isinstance(data, pd.DataFrame):
            data_list = data.to_dict('records')
        elif isinstance(data, str):
            data_list = data  # File path
        else:
            data_list = data
        
        # Default configurations
        if model_config is None:
            model_config = {}
        if training_config is None:
            training_config = {}
        
        request_data = {
            "dataset": {
                "data": data_list,
                "treatment_column": treatment_column,
                "outcome_column": outcome_column,
                "feature_columns": feature_columns,
                "text_column": text_column
            },
            "model_config": model_config,
            "training_config": training_config,
            "experiment_name": experiment_name
        }
        
        return self._make_request('POST', '/train', data=request_data)
    
    def predict(
        self,
        model_id: str,
        data: Union[pd.DataFrame, str, List[dict]],
        return_counterfactuals: bool = True,
        return_uncertainty: bool = False
    ) -> dict:
        """
        Generate predictions using a trained model.
        
        Args:
            model_id: ID of trained model
            data: Data for prediction
            return_counterfactuals: Whether to return counterfactual predictions
            return_uncertainty: Whether to return uncertainty estimates
            
        Returns:
            Prediction results dict
        """
        # Prepare data
        if isinstance(data, pd.DataFrame):
            data_list = data.to_dict('records')
        elif isinstance(data, str):
            data_list = data  # File path
        else:
            data_list = data
        
        request_data = {
            "model_id": model_id,
            "data": data_list,
            "return_counterfactuals": return_counterfactuals,
            "return_uncertainty": return_uncertainty
        }
        
        return self._make_request('POST', '/predict', data=request_data)
    
    def evaluate_predictions(
        self,
        predictions: Union[pd.DataFrame, List[dict]],
        ground_truth: Optional[Union[pd.DataFrame, List[dict]]] = None
    ) -> dict:
        """
        Evaluate model predictions.
        
        Args:
            predictions: Predictions with mu0, mu1, treatment, outcome columns
            ground_truth: Optional ground truth values
            
        Returns:
            Evaluation results dict
        """
        # Prepare predictions
        if isinstance(predictions, pd.DataFrame):
            pred_list = predictions.to_dict('records')
        else:
            pred_list = predictions
        
        # Prepare ground truth
        if ground_truth is not None:
            if isinstance(ground_truth, pd.DataFrame):
                gt_list = ground_truth.to_dict('records')
            else:
                gt_list = ground_truth
        else:
            gt_list = None
        
        request_data = {
            "predictions": pred_list,
            "ground_truth": gt_list
        }
        
        return self._make_request('POST', '/evaluate', data=request_data)
    
    def complete_analysis(
        self,
        data: Union[pd.DataFrame, str, List[dict]],
        treatment_column: str,
        outcome_column: str,
        feature_columns: Optional[List[str]] = None,
        text_column: Optional[str] = None,
        model_config: Optional[dict] = None,
        training_config: Optional[dict] = None,
        skip_assumptions: bool = False,
        return_individual_effects: bool = False,
        methods: List[str] = ["backdoor"]
    ) -> dict:
        """
        Run complete causal analysis workflow.
        
        Args:
            data: Dataset as DataFrame, file path, or list of dicts
            treatment_column: Name of treatment column
            outcome_column: Name of outcome column
            feature_columns: List of feature column names
            text_column: Name of text column
            model_config: Model configuration dict
            training_config: Training configuration dict
            skip_assumptions: Skip assumption validation
            return_individual_effects: Return individual treatment effects
            methods: Causal identification methods to use
            
        Returns:
            Complete analysis results dict
        """
        # Prepare dataset
        if isinstance(data, pd.DataFrame):
            data_list = data.to_dict('records')
        elif isinstance(data, str):
            data_list = data  # File path
        else:
            data_list = data
        
        # Default configurations
        if model_config is None:
            model_config = {}
        if training_config is None:
            training_config = {}
        
        request_data = {
            "dataset": {
                "data": data_list,
                "treatment_column": treatment_column,
                "outcome_column": outcome_column,
                "feature_columns": feature_columns,
                "text_column": text_column
            },
            "model_config": model_config,
            "training_config": training_config,
            "skip_assumptions": skip_assumptions,
            "return_individual_effects": return_individual_effects,
            "methods": methods
        }
        
        return self._make_request('POST', '/analyze', data=request_data)
    
    def list_models(self) -> dict:
        """List all available models."""
        return self._make_request('GET', '/models')
    
    def get_model_info(self, model_id: str) -> dict:
        """Get information about a specific model."""
        return self._make_request('GET', f'/models/{model_id}')
    
    def delete_model(self, model_id: str) -> dict:
        """Delete a model."""
        return self._make_request('DELETE', f'/models/{model_id}')
    
    def save_results(self, results: dict, file_path: str):
        """Save analysis results to file."""
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {file_path}")
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file as DataFrame."""
        return pd.read_csv(file_path)


class AsyncCANSAPIClient:
    """Async version of CANS API client."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000", 
        api_key: Optional[str] = None,
        timeout: int = 300
    ):
        """Initialize async CANS API client."""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        
        import aiohttp
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        import aiohttp
        
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        """Make async HTTP request to API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url, params=params) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise CANSAPIException(f"HTTP {response.status}: {error_text}")
                    return await response.json()
            
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise CANSAPIException(f"HTTP {response.status}: {error_text}")
                    return await response.json()
            
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
        except Exception as e:
            if not isinstance(e, CANSAPIException):
                raise CANSAPIException(f"Request failed: {str(e)}")
            raise
    
    async def validate_assumptions(self, *args, **kwargs) -> dict:
        """Async version of validate_assumptions."""
        # Similar implementation to sync version
        pass
    
    async def train_model(self, *args, **kwargs) -> dict:
        """Async version of train_model."""
        # Similar implementation to sync version
        pass


# Convenience functions
def quick_validation(
    data_path: str,
    treatment_column: str,
    outcome_column: str,
    api_key: Optional[str] = None,
    base_url: str = "http://localhost:8000"
) -> dict:
    """Quick validation of causal assumptions."""
    client = CANSAPIClient(base_url=base_url, api_key=api_key)
    return client.validate_assumptions(data_path, treatment_column, outcome_column)


def quick_analysis(
    data_path: str,
    treatment_column: str,
    outcome_column: str,
    api_key: Optional[str] = None,
    base_url: str = "http://localhost:8000"
) -> dict:
    """Quick complete analysis."""
    client = CANSAPIClient(base_url=base_url, api_key=api_key)
    return client.complete_analysis(data_path, treatment_column, outcome_column)