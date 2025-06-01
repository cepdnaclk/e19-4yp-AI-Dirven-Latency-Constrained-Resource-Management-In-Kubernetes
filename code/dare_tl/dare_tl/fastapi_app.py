from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from dare_tl.model import TrendLearner
import joblib

app = FastAPI(title="Resource Usage Prediction API", version="1.0.0")
# Load model and scaler
try:
    model = TrendLearner.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("Model and scaler loaded successfully")
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    model = None
    scaler = None
    
class PredictionResponse(BaseModel):
    forecast: dict
    safe_range: dict
    status: str
    
class UsageInput(BaseModel):
    CPU_Usage: float
    Memory_Usage: float
    RequestRate: float
    CPU_Limit: float
    Memory_Limit: float
    
app.get("/")
def root():
    return {"message": "Resource Usage Prediction API", "status": "running"}

@app.get("/health")
def health_check():
    model_loaded = model is not None
    scaler_loaded = scaler is not None
    return {
        "status": "healthy" if (model_loaded and scaler_loaded) else "unhealthy",
        "model_loaded": model_loaded,
        "scaler_loaded": scaler_loaded
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(input: UsageInput):
    
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
        
        # Make predictions
        pred_cpu_delta, pred_mem_delta = model.predict_usage(X_scaled)
        
        if pred_cpu_delta is None or pred_mem_delta is None:
            raise HTTPException(status_code=500, detail="Model prediction failed")
        
        # Calculate future usage
        future_cpu = input_data.CPU_Usage + pred_cpu_delta[0]
        future_mem = max(0, input_data.Memory_Usage + pred_mem_delta[0])
        
        # Calculate safe operating range
        safe_range = model.safe_range(future_cpu, future_mem)
        
        return PredictionResponse(
            forecast={
                "CPU_Usage_Forecast": round(future_cpu, 4),
                "Memory_Usage_Forecast": round(future_mem, 0),
                "CPU_Delta": round(pred_cpu_delta[0], 4),
                "Memory_Delta": round(pred_mem_delta[0], 0)
            },
            safe_range=safe_range,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")