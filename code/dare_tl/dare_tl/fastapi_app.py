from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from model import TrendLearner
import joblib
import os
from datetime import datetime, timedelta
from collections import deque

app = FastAPI(title="Resource Usage Prediction API", version="1.0.0")
# Load model and scaler
# Model paths
MODEL_PATH = "./models/tl_model.pkl"
SCALER_PATH = "./models/scaler.pkl"
try:
    model = TrendLearner.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("Model and scaler loaded successfully")
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    model = None
    scaler = None
    
history_buffer = deque(maxlen=200)  # covers a bit more than 1 hour at ~30s intervals
    
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
            input.CPU_Usage, 
            input.Memory_Usage, 
            input.RequestRate, 
            input.CPU_Limit, 
            input.Memory_Limit
        ]])
        
        # Scale input features
        X_scaled = scaler.transform(X)
        now = datetime.now()
        
        # Add new data to buffer
        history_buffer.append((now, new_data_scaled[0]))
        
         # Filter last 1 hour of data
        cutoff = now - timedelta(hours=1)
        recent_data = np.array([x[1] for x in history_buffer if x[0] >= cutoff])

        if recent_data.shape[0] == 0:
            raise HTTPException(status_code=400, detail="Insufficient recent data for prediction")
        
        # Use the average of recent features as input to the model
        input_for_prediction = recent_data.mean(axis=0).reshape(1, -1)
        
        # Make predictions
        pred_cpu_delta, pred_mem_delta = model.predict_usage(X_scaled)
        
        if pred_cpu_delta is None or pred_mem_delta is None:
            raise HTTPException(status_code=500, detail="Model prediction failed")
        
        # Calculate future usage
        future_cpu = input.CPU_Usage + pred_cpu_delta[0]
        future_mem = max(0, input.Memory_Usage + pred_mem_delta[0])
        
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
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)