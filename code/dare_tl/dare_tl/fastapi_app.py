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
    
app.get("/")
def root():
    return {"message": "Resource Usage Prediction API", "status": "running"}

class UsageInput(BaseModel):
    CPU_Usage: float
    Memory_Usage: float
    RequestRate: float
    CPU_Limit: float
    Memory_Limit: float

@app.post("/predict")
def predict(input: UsageInput):
    
    X = np.array([[input.CPU_Usage, input.Memory_Usage, input.RequestRate, input.CPU_Limit, input.Memory_Limit]])
    X_scaled = scaler.transform(X)
    pred_cpu_delta, pred_mem_delta = model.predict_usage(X_scaled)

    future_cpu = input.CPU_Usage + (pred_cpu_delta[0] if pred_cpu_delta is not None else 0)
    future_mem = max(0, input.Memory_Usage + (pred_mem_delta[0] if pred_mem_delta is not None else 0))
    safe_range = model.safe_range(future_cpu, future_mem)

    return {
        "forecast": {
            "CPU_Usage_Forecast": round(future_cpu, 2),
            "Memory_Usage_Forecast": round(future_mem, 2)
        },
        "safe_range": safe_range
    }
