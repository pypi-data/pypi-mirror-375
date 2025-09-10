"""
Pydantic models for CANS API requests and responses.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
import pandas as pd
import numpy as np


class DatasetRequest(BaseModel):
    """Request model for dataset operations."""
    data: Union[List[Dict], str] = Field(..., description="CSV data as list of dicts or file path")
    treatment_column: str = Field(..., description="Name of treatment column")
    outcome_column: str = Field(..., description="Name of outcome column") 
    feature_columns: Optional[List[str]] = Field(None, description="List of feature column names")
    text_column: Optional[str] = Field(None, description="Name of text column")
    
    @validator('data')
    def validate_data(cls, v):
        if isinstance(v, str):
            return v  # File path
        if isinstance(v, list) and len(v) > 0:
            return v  # List of records
        raise ValueError("Data must be non-empty list or valid file path")


class ValidationRequest(BaseModel):
    """Request for causal assumption validation."""
    dataset: DatasetRequest
    verbose: bool = Field(default=False, description="Enable verbose output")


class ValidationResponse(BaseModel):
    """Response from causal assumption validation."""
    causal_identification_valid: bool
    unconfoundedness_test: Dict[str, Any]
    positivity_test: Dict[str, Any] 
    sutva_test: Dict[str, Any]
    summary: Dict[str, Any]
    recommendations: List[str]


class ModelConfig(BaseModel):
    """Configuration for CANS model."""
    gnn_type: str = Field(default="GCN", description="GNN architecture type")
    gnn_hidden_dim: int = Field(default=128, description="GNN hidden dimension")
    fusion_dim: int = Field(default=256, description="Fusion layer dimension")
    text_model: str = Field(default="distilbert-base-uncased", description="Text model name")


class TrainingConfig(BaseModel):
    """Training configuration."""
    learning_rate: float = Field(default=0.001, description="Learning rate")
    batch_size: int = Field(default=32, description="Batch size")
    epochs: int = Field(default=50, description="Number of epochs")
    loss_type: str = Field(default="cfr", description="Loss function type")
    early_stopping_patience: int = Field(default=10, description="Early stopping patience")


class TrainingRequest(BaseModel):
    """Request for model training."""
    dataset: DatasetRequest
    model_config: Optional[ModelConfig] = Field(default_factory=ModelConfig)
    training_config: Optional[TrainingConfig] = Field(default_factory=TrainingConfig)
    experiment_name: Optional[str] = Field(None, description="Experiment name for tracking")


class TrainingResponse(BaseModel):
    """Response from model training."""
    model_id: str = Field(..., description="Unique model identifier")
    training_metrics: Dict[str, List[float]]
    validation_metrics: Dict[str, List[float]]
    final_performance: Dict[str, float]
    training_time: float
    experiment_name: Optional[str]


class PredictionRequest(BaseModel):
    """Request for model predictions."""
    model_id: str = Field(..., description="Model identifier")
    data: Union[List[Dict], str] = Field(..., description="Data for prediction")
    return_counterfactuals: bool = Field(default=True, description="Return counterfactual predictions")
    return_uncertainty: bool = Field(default=False, description="Return uncertainty estimates")


class PredictionResponse(BaseModel):
    """Response from model predictions."""
    predictions: List[Dict[str, float]]
    treatment_effects: Optional[List[float]]
    counterfactuals: Optional[Dict[str, List[float]]]
    uncertainty: Optional[List[Dict[str, float]]]
    summary_stats: Dict[str, float]


class EvaluationRequest(BaseModel):
    """Request for model evaluation."""
    predictions: List[Dict[str, float]] = Field(..., description="Model predictions")
    ground_truth: Optional[List[Dict[str, float]]] = Field(None, description="Ground truth values")
    
    @validator('predictions')
    def validate_predictions(cls, v):
        required_keys = ['mu0', 'mu1', 'treatment', 'outcome']
        for pred in v:
            missing = [k for k in required_keys if k not in pred]
            if missing:
                raise ValueError(f"Missing required keys in predictions: {missing}")
        return v


class EvaluationResponse(BaseModel):
    """Response from model evaluation."""
    ate: float = Field(..., description="Average Treatment Effect")
    ate_std: float = Field(..., description="ATE standard error")
    ate_confidence_interval: List[float] = Field(..., description="ATE 95% CI")
    factual_mse: float = Field(..., description="Factual prediction MSE")
    pehe: Optional[float] = Field(None, description="PEHE score")
    cate_r2: Optional[float] = Field(None, description="CATE R-squared")
    policy_value: Optional[float] = Field(None, description="Policy value")
    calibration_metrics: Optional[Dict[str, float]] = Field(None, description="Calibration scores")


class AnalysisRequest(BaseModel):
    """Request for complete causal analysis."""
    dataset: DatasetRequest
    model_config: Optional[ModelConfig] = Field(default_factory=ModelConfig)
    training_config: Optional[TrainingConfig] = Field(default_factory=TrainingConfig)
    skip_assumptions: bool = Field(default=False, description="Skip assumption validation")
    return_individual_effects: bool = Field(default=False, description="Return individual treatment effects")
    methods: List[str] = Field(default=["backdoor"], description="Causal identification methods")


class AnalysisResponse(BaseModel):
    """Response from complete causal analysis."""
    validation_results: Optional[ValidationResponse]
    training_results: TrainingResponse
    evaluation_results: EvaluationResponse
    causal_effects: Dict[str, Any]
    individual_effects: Optional[List[float]]
    recommendations: List[str]
    analysis_summary: Dict[str, Any]


class ModelInfo(BaseModel):
    """Information about a trained model."""
    model_id: str
    experiment_name: Optional[str]
    created_at: str
    model_config: ModelConfig
    training_config: TrainingConfig
    performance_metrics: Dict[str, float]
    status: str


class ListModelsResponse(BaseModel):
    """Response for listing available models."""
    models: List[ModelInfo]
    total_count: int


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Detailed error information")
    error_code: Optional[str] = Field(None, description="Error code")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="CANS version")
    uptime: float = Field(..., description="Uptime in seconds")
    dependencies: Dict[str, str] = Field(..., description="Dependency versions")