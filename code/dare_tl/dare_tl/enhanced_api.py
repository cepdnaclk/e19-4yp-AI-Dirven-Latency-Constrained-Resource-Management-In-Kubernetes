from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import numpy as np
from enhanced_model import EnhancedTrendLearner
import joblib
import os
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced Resource Usage Prediction API", 
    version="2.0.0",
    description="Advanced ML API for container resource usage prediction with uncertainty estimation"
)

# Model paths
MODEL_PATH = "./models/enhanced_tl_model.pkl"
SCALER_PATH = "./models/enhanced_tl_scaler.pkl"

# Global model and scaler
model = None
scaler = None

@app.on_event("startup")
async def load_models():
    """Load models on startup"""
    global model, scaler
    try:
        model = EnhancedTrendLearner.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        logger.info("Enhanced model and scaler loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model or scaler: {e}")
        model = None
        scaler = None

class UsageInput(BaseModel):
    CPU_Usage: float = Field(..., description="Current CPU usage", ge=0)
    Memory_Usage: float = Field(..., description="Current memory usage (MiB)", ge=0)
    RequestRate: float = Field(..., description="Current request rate", ge=0)
    CPU_Limit: float = Field(..., description="CPU limit", gt=0)
    Memory_Limit: float = Field(..., description="Memory limit (MiB)", gt=0)

class PredictionResponse(BaseModel):
    forecast: Dict[str, float]
    safe_range: Dict[str, Any]
    uncertainty: Optional[Dict[str, float]] = None
    feature_importance: Optional[Dict[str, Any]] = None
    model_info: Dict[str, Any]
    status: str

class UpdateInput(BaseModel):
    CPU_Usage: float
    Memory_Usage: float
    RequestRate: float
    CPU_Limit: float
    Memory_Limit: float
    CPU_Usage_Delta: float
    Memory_Usage_Delta: float

@app.get("/")
async def root():
    return {
        "message": "Enhanced Resource Usage Prediction API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Advanced feature engineering",
            "Uncertainty estimation",
            "Multiple model types (SGD, Random Forest)",
            "Real-time model updates",
            "Comprehensive validation metrics"
        ]
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with model diagnostics"""
    model_loaded = model is not None
    scaler_loaded = scaler is not None
    
    health_info = {
        "status": "healthy" if (model_loaded and scaler_loaded) else "unhealthy",
        "model_loaded": model_loaded,
        "scaler_loaded": scaler_loaded
    }
    
    if model_loaded:
        health_info.update({
            "model_type": model.ensemble_method,
            "feature_engineering": model.feature_engineering,
            "is_fitted": model.is_fitted,
            "window_size": model.window_size
        })
        
        # Add validation metrics if available
        val_metrics = model.get_validation_metrics()
        if val_metrics:
            health_info["validation_r2"] = {
                "cpu": val_metrics.get("latest_cpu_r2"),
                "memory": val_metrics.get("latest_mem_r2")
            }
    
    return health_info

@app.post("/predict", response_model=PredictionResponse)
async def predict(input_data: UsageInput):
    """Enhanced prediction with uncertainty estimation"""
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="Model or scaler not loaded")
    
    try:
        # Prepare input data
        X = np.array([[
            input_data.CPU_Usage,
            input_data.Memory_Usage,
            input_data.RequestRate,
            input_data.CPU_Limit,
            input_data.Memory_Limit
        ]])
        
        # Scale input features
        X_scaled = scaler.transform(X)
        
        # Make predictions with uncertainty
        cpu_pred, mem_pred, cpu_std, mem_std = model.predict_with_uncertainty(X_scaled)
        
        if cpu_pred is None or mem_pred is None:
            raise HTTPException(status_code=500, detail="Model prediction failed")
        
        # Calculate future usage
        future_cpu = input_data.CPU_Usage + cpu_pred[0]
        future_mem = max(0, input_data.Memory_Usage + mem_pred[0])
        
        # Calculate safe operating range with uncertainty
        uncertainty = (cpu_std[0], mem_std[0]) if cpu_std is not None else None
        safe_range = model.safe_range(future_cpu, future_mem, uncertainty=uncertainty)
        
        # Prepare response
        response_data = {
            "forecast": {
                "CPU_Usage_Forecast": round(float(future_cpu), 4),
                "Memory_Usage_Forecast": round(float(future_mem), 0),
                "CPU_Delta": round(float(cpu_pred[0]), 4),
                "Memory_Delta": round(float(mem_pred[0]), 0)
            },
            "safe_range": safe_range,
            "model_info": {
                "model_type": model.ensemble_method,
                "feature_engineering": model.feature_engineering,
                "confidence_level": "high" if uncertainty is None else "medium"
            },
            "status": "success"
        }
        
        # Add uncertainty information if available
        if uncertainty:
            response_data["uncertainty"] = {
                "CPU_Delta_Std": round(float(cpu_std[0]), 4),
                "Memory_Delta_Std": round(float(mem_std[0]), 0),
                "confidence_interval_95": {
                    "CPU_Delta": [
                        round(float(cpu_pred[0] - 1.96 * cpu_std[0]), 4),
                        round(float(cpu_pred[0] + 1.96 * cpu_std[0]), 4)
                    ],
                    "Memory_Delta": [
                        round(float(mem_pred[0] - 1.96 * mem_std[0]), 0),
                        round(float(mem_pred[0] + 1.96 * mem_std[0]), 0)
                    ]
                }
            }
        
        # Add feature importance if available
        importance = model.get_feature_importance()
        if importance:
            response_data["feature_importance"] = importance
        
        return PredictionResponse(**response_data)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/update")
async def update_model(input_data: UpdateInput):
    """Update model with new data point"""
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="Model or scaler not loaded")
    
    try:
        # Prepare input features
        X = np.array([[
            input_data.CPU_Usage,
            input_data.Memory_Usage,
            input_data.RequestRate,
            input_data.CPU_Limit,
            input_data.Memory_Limit
        ]])
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Target values
        y_cpu = np.array([input_data.CPU_Usage_Delta])
        y_mem = np.array([input_data.Memory_Usage_Delta])
        
        # Update model
        model.partial_fit(X_scaled, y_cpu, y_mem)
        
        # Save updated model
        model.save(MODEL_PATH)
        
        logger.info("Model updated successfully with new data point")
        
        return {
            "status": "success",
            "message": "Model updated successfully",
            "data_point": {
                "CPU_Usage": input_data.CPU_Usage,
                "Memory_Usage": input_data.Memory_Usage,
                "CPU_Delta": input_data.CPU_Usage_Delta,
                "Memory_Delta": input_data.Memory_Usage_Delta
            }
        }
        
    except Exception as e:
        logger.error(f"Model update error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model update error: {str(e)}")

@app.get("/model/info")
async def get_model_info():
    """Get detailed model information"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        info = {
            "model_type": model.ensemble_method,
            "feature_engineering": model.feature_engineering,
            "window_size": model.window_size,
            "ema_alpha": model.alpha,
            "is_fitted": model.is_fitted,
            "feature_history_length": len(model.feature_history)
        }
        
        # Add validation metrics
        val_metrics = model.get_validation_metrics()
        if val_metrics:
            info["validation_metrics"] = val_metrics
        
        # Add feature importance
        importance = model.get_feature_importance()
        if importance:
            info["feature_importance"] = importance
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

@app.get("/model/metrics")
async def get_model_metrics():
    """Get model performance metrics"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        val_metrics = model.get_validation_metrics()
        if val_metrics is None:
            return {"message": "No validation metrics available"}
        
        return {
            "latest_metrics": {
                "cpu_mse": val_metrics["latest_cpu_mse"],
                "mem_mse": val_metrics["latest_mem_mse"],
                "cpu_r2": val_metrics["latest_cpu_r2"],
                "mem_r2": val_metrics["latest_mem_r2"]
            },
            "metrics_history_length": len(val_metrics["history"]["cpu_mse"]),
            "average_r2": {
                "cpu": np.mean(val_metrics["history"]["cpu_r2"]),
                "memory": np.mean(val_metrics["history"]["mem_r2"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting model metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting model metrics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)