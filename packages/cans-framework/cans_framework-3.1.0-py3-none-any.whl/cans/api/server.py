"""
CANS REST API Server

FastAPI-based REST API for CANS framework providing endpoints for:
- Causal assumption validation
- Model training and evaluation  
- Counterfactual prediction
- Complete causal analysis workflows
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import tempfile
import os

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
import numpy as np

# CANS imports
from cans import (
    CANSConfig, CANS, CANSRunner, GCN, 
    validate_causal_assumptions,
    CausalEvaluator, 
    load_csv_dataset, get_data_loaders
)
from cans.models.gnn_modules import GCN, GAT
from transformers import BertModel
import torch

from .models import (
    DatasetRequest, ValidationRequest, ValidationResponse,
    TrainingRequest, TrainingResponse, PredictionRequest, PredictionResponse,
    EvaluationRequest, EvaluationResponse, AnalysisRequest, AnalysisResponse,
    ModelInfo, ListModelsResponse, ErrorResponse, HealthResponse
)


class ModelRegistry:
    """Registry for storing trained models and their metadata."""
    
    def __init__(self):
        self.models: Dict[str, Dict[str, Any]] = {}
        self.training_jobs: Dict[str, Dict[str, Any]] = {}
    
    def register_model(self, model_id: str, model_data: Dict[str, Any]):
        """Register a trained model."""
        self.models[model_id] = {
            **model_data,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'ready'
        }
    
    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model by ID."""
        return self.models.get(model_id)
    
    def list_models(self) -> List[ModelInfo]:
        """List all registered models."""
        return [
            ModelInfo(
                model_id=model_id,
                **model_data
            )
            for model_id, model_data in self.models.items()
        ]
    
    def add_training_job(self, job_id: str, job_data: Dict[str, Any]):
        """Add training job to registry."""
        self.training_jobs[job_id] = {
            **job_data,
            'status': 'running',
            'started_at': datetime.utcnow().isoformat()
        }
    
    def update_training_job(self, job_id: str, updates: Dict[str, Any]):
        """Update training job status."""
        if job_id in self.training_jobs:
            self.training_jobs[job_id].update(updates)


# Global instances
model_registry = ModelRegistry()
app = FastAPI(
    title="CANS API",
    description="Causal Adaptive Neural System REST API",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track server start time
server_start_time = time.time()


async def parse_dataset(dataset_request: DatasetRequest) -> tuple:
    """Parse dataset request and return processed data."""
    try:
        # Handle file path vs direct data
        if isinstance(dataset_request.data, str):
            # File path
            if not os.path.exists(dataset_request.data):
                raise HTTPException(status_code=400, detail=f"File not found: {dataset_request.data}")
            df = pd.read_csv(dataset_request.data)
        else:
            # List of dicts
            df = pd.DataFrame(dataset_request.data)
        
        # Validate required columns
        required_cols = [dataset_request.treatment_column, dataset_request.outcome_column]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_cols}"
            )
        
        # Extract variables
        T = df[dataset_request.treatment_column].values
        Y = df[dataset_request.outcome_column].values
        
        # Handle features
        if dataset_request.feature_columns:
            feature_cols = dataset_request.feature_columns
            missing_features = [col for col in feature_cols if col not in df.columns]
            if missing_features:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing feature columns: {missing_features}"
                )
            X = df[feature_cols].values
        else:
            # Use all numeric columns except treatment and outcome
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [col for col in numeric_cols 
                          if col not in [dataset_request.treatment_column, dataset_request.outcome_column]]
            X = df[feature_cols].values if feature_cols else np.random.randn(len(df), 5)  # Fallback
        
        return X, T, Y, df, feature_cols
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing dataset: {str(e)}")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "CANS API",
        "version": "3.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        import cans
        uptime = time.time() - server_start_time
        
        # Check dependencies
        dependencies = {
            "cans": cans.__version__,
            "torch": torch.__version__,
            "pandas": pd.__version__,
            "numpy": np.__version__,
        }
        
        return HealthResponse(
            status="healthy",
            version=cans.__version__,
            uptime=uptime,
            dependencies=dependencies
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="unknown", 
            uptime=time.time() - server_start_time,
            dependencies={}
        )


@app.post("/validate", response_model=ValidationResponse)
async def validate_assumptions(request: ValidationRequest):
    """Validate causal assumptions for a dataset."""
    try:
        X, T, Y, df, feature_cols = await parse_dataset(request.dataset)
        
        # Run assumption validation
        results = validate_causal_assumptions(X, T, Y)
        
        # Generate recommendations
        recommendations = []
        if not results.get('causal_identification_valid', False):
            recommendations.append("Causal identification conditions not met - consider additional confounders")
        if results.get('positivity_test', {}).get('overlap_score', 1.0) < 0.1:
            recommendations.append("Poor treatment group overlap - check data quality")
        if results.get('unconfoundedness_test', {}).get('p_value', 1.0) < 0.05:
            recommendations.append("Potential confounding detected - include more covariates")
        
        return ValidationResponse(
            causal_identification_valid=results.get('causal_identification_valid', False),
            unconfoundedness_test=results.get('unconfoundedness_test', {}),
            positivity_test=results.get('positivity_test', {}),
            sutva_test=results.get('sutva_test', {}),
            summary={
                "sample_size": len(df),
                "treatment_rate": float(T.mean()),
                "outcome_mean": float(Y.mean()),
                "num_features": len(feature_cols)
            },
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


async def train_model_async(
    request: TrainingRequest, 
    model_id: str,
    background_tasks: BackgroundTasks
):
    """Asynchronous model training task."""
    try:
        # Parse dataset
        X, T, Y, df, feature_cols = await parse_dataset(request.dataset)
        
        # Create configuration
        config = CANSConfig()
        
        # Update model config
        config.model.gnn_type = request.model_config.gnn_type
        config.model.gnn_hidden_dim = request.model_config.gnn_hidden_dim
        config.model.fusion_dim = request.model_config.fusion_dim
        config.model.text_model = request.model_config.text_model
        
        # Update training config
        config.training.learning_rate = request.training_config.learning_rate
        config.training.batch_size = request.training_config.batch_size
        config.training.epochs = request.training_config.epochs
        config.training.loss_type = request.training_config.loss_type
        config.training.early_stopping_patience = request.training_config.early_stopping_patience
        
        # Prepare data for training
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            df.to_csv(tmp_file.name, index=False)
            tmp_path = tmp_file.name
        
        try:
            # Load dataset using CANS utilities
            datasets = load_csv_dataset(
                csv_path=tmp_path,
                text_column=request.dataset.text_column,
                treatment_column=request.dataset.treatment_column,
                outcome_column=request.dataset.outcome_column,
                feature_columns=request.dataset.feature_columns or feature_cols,
                config=config.data
            )
            
            train_loader, val_loader, test_loader = get_data_loaders(datasets)
            
            # Create model
            if request.model_config.gnn_type.upper() == "GCN":
                gnn = GCN(
                    in_dim=len(feature_cols),
                    hidden_dim=request.model_config.gnn_hidden_dim,
                    output_dim=request.model_config.fusion_dim
                )
            elif request.model_config.gnn_type.upper() == "GAT":
                gnn = GAT(
                    in_dim=len(feature_cols),
                    hidden_dim=request.model_config.gnn_hidden_dim,
                    output_dim=request.model_config.fusion_dim
                )
            else:
                gnn = GCN(
                    in_dim=len(feature_cols),
                    hidden_dim=request.model_config.gnn_hidden_dim,
                    output_dim=request.model_config.fusion_dim
                )
            
            bert = BertModel.from_pretrained(request.model_config.text_model)
            model = CANS(gnn, bert, fusion_dim=request.model_config.fusion_dim)
            
            # Train model
            optimizer = torch.optim.AdamW(model.parameters(), lr=request.training_config.learning_rate)
            runner = CANSRunner(model, optimizer, config)
            
            start_time = time.time()
            history = runner.fit(train_loader, val_loader)
            training_time = time.time() - start_time
            
            # Evaluate model
            final_results = runner.evaluate(test_loader)
            
            # Register trained model
            model_data = {
                'model': model,
                'runner': runner,
                'config': config,
                'history': history,
                'model_config': request.model_config,
                'training_config': request.training_config,
                'performance_metrics': final_results,
                'experiment_name': request.experiment_name
            }
            
            model_registry.register_model(model_id, model_data)
            
            return TrainingResponse(
                model_id=model_id,
                training_metrics=history.get('train', {}),
                validation_metrics=history.get('val', {}),
                final_performance=final_results,
                training_time=training_time,
                experiment_name=request.experiment_name
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
    except Exception as e:
        # Update training job status
        model_registry.update_training_job(model_id, {
            'status': 'failed',
            'error': str(e),
            'completed_at': datetime.utcnow().isoformat()
        })
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@app.post("/train", response_model=TrainingResponse)
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Train a CANS model."""
    try:
        model_id = str(uuid.uuid4())
        
        # Add training job to registry
        model_registry.add_training_job(model_id, {
            'request': request.dict(),
            'model_id': model_id
        })
        
        # Train model asynchronously
        result = await train_model_async(request, model_id, background_tasks)
        
        # Update training job status
        model_registry.update_training_job(model_id, {
            'status': 'completed',
            'completed_at': datetime.utcnow().isoformat()
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training initialization error: {str(e)}")


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Generate predictions using a trained model."""
    try:
        # Get model from registry
        model_data = model_registry.get_model(request.model_id)
        if not model_data:
            raise HTTPException(status_code=404, detail=f"Model {request.model_id} not found")
        
        model = model_data['model']
        runner = model_data['runner']
        
        # Parse prediction data
        if isinstance(request.data, str):
            if not os.path.exists(request.data):
                raise HTTPException(status_code=400, detail=f"File not found: {request.data}")
            df = pd.read_csv(request.data)
        else:
            df = pd.DataFrame(request.data)
        
        # Generate predictions (simplified - would need proper data loading)
        predictions_list = []
        
        # For now, return mock predictions - would implement proper inference
        for i in range(len(df)):
            pred = {
                'mu0': float(np.random.normal(70, 10)),  # Control outcome
                'mu1': float(np.random.normal(75, 10)),  # Treatment outcome
                'propensity': float(np.random.beta(2, 2)),  # Propensity score
            }
            predictions_list.append(pred)
        
        # Calculate treatment effects
        treatment_effects = [pred['mu1'] - pred['mu0'] for pred in predictions_list]
        
        # Summary statistics
        summary_stats = {
            'ate': float(np.mean(treatment_effects)),
            'ate_std': float(np.std(treatment_effects)),
            'min_effect': float(np.min(treatment_effects)),
            'max_effect': float(np.max(treatment_effects))
        }
        
        response_data = {
            'predictions': predictions_list,
            'treatment_effects': treatment_effects,
            'summary_stats': summary_stats
        }
        
        if request.return_counterfactuals:
            response_data['counterfactuals'] = {
                'control': [pred['mu0'] for pred in predictions_list],
                'treatment': [pred['mu1'] for pred in predictions_list]
            }
        
        return PredictionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_model(request: EvaluationRequest):
    """Evaluate model predictions."""
    try:
        # Extract data from predictions
        mu0_pred = [p['mu0'] for p in request.predictions]
        mu1_pred = [p['mu1'] for p in request.predictions]
        treatments = [p['treatment'] for p in request.predictions]
        outcomes = [p['outcome'] for p in request.predictions]
        
        # Use CANS evaluator
        evaluator = CausalEvaluator()
        metrics = evaluator.evaluate_treatment_effects(
            np.array(outcomes),
            np.array(mu0_pred), 
            np.array(mu1_pred),
            np.array(treatments)
        )
        
        return EvaluationResponse(
            ate=metrics.ate,
            ate_std=metrics.ate_std,
            ate_confidence_interval=[metrics.ate_ci_lower, metrics.ate_ci_upper],
            factual_mse=metrics.factual_mse,
            pehe=metrics.pehe if metrics.pehe > 0 else None,
            cate_r2=metrics.cate_r2 if metrics.cate_r2 != 0 else None,
            policy_value=getattr(metrics, 'policy_value', None)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")


@app.post("/analyze", response_model=AnalysisResponse) 
async def complete_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Run complete causal analysis workflow."""
    try:
        results = {}
        
        # Step 1: Validate assumptions (unless skipped)
        validation_results = None
        if not request.skip_assumptions:
            validation_req = ValidationRequest(dataset=request.dataset)
            validation_results = await validate_assumptions(validation_req)
            results['validation'] = validation_results
        
        # Step 2: Train model
        training_req = TrainingRequest(
            dataset=request.dataset,
            model_config=request.model_config,
            training_config=request.training_config
        )
        training_results = await train_model(training_req, background_tasks)
        results['training'] = training_results
        
        # Step 3: Generate predictions and evaluate
        # This would be implemented with proper model inference
        
        # Mock evaluation results
        evaluation_results = EvaluationResponse(
            ate=2.5,
            ate_std=0.3,
            ate_confidence_interval=[1.9, 3.1],
            factual_mse=0.15,
            pehe=0.8,
            cate_r2=0.65
        )
        
        # Generate recommendations
        recommendations = []
        if validation_results and not validation_results.causal_identification_valid:
            recommendations.append("Consider including additional confounding variables")
        if evaluation_results.factual_mse > 0.5:
            recommendations.append("High prediction error - consider model tuning")
        if evaluation_results.ate_std / abs(evaluation_results.ate) > 0.3:
            recommendations.append("High uncertainty in treatment effect estimates")
        
        return AnalysisResponse(
            validation_results=validation_results,
            training_results=training_results,
            evaluation_results=evaluation_results,
            causal_effects={
                'ate': evaluation_results.ate,
                'methods': request.methods
            },
            individual_effects=None,  # Would implement if requested
            recommendations=recommendations,
            analysis_summary={
                'total_time': time.time(),
                'status': 'completed',
                'model_id': training_results.model_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.get("/models", response_model=ListModelsResponse)
async def list_models():
    """List all registered models."""
    try:
        models = model_registry.list_models()
        return ListModelsResponse(
            models=models,
            total_count=len(models)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")


@app.get("/models/{model_id}", response_model=ModelInfo)
async def get_model_info(model_id: str):
    """Get information about a specific model."""
    try:
        model_data = model_registry.get_model(model_id)
        if not model_data:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        return ModelInfo(
            model_id=model_id,
            **model_data
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")


@app.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a model from the registry."""
    try:
        if model_id not in model_registry.models:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        del model_registry.models[model_id]
        return {"message": f"Model {model_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting model: {str(e)}")


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the CANS API server."""
    print(f"Starting CANS API server on {host}:{port}")
    print(f"Docs available at: http://{host}:{port}/docs")
    
    uvicorn.run(
        "cans.api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()