from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from model import TrendLearner
import joblib
import os
from datetime import datetime, timedelta
from collections import deque

app = FastAPI(title="Resource Usage Prediction API", version="1.0.0")

# Model paths
MODEL_PATH = "./models/tl_model.pkl"
SCALER_PATH = "./models/scaler.pkl"

# Load model and scaler
try:
    model = TrendLearner.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("Model and scaler loaded successfully")
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    model = None
    scaler = None

# History buffer to store recent feature data for trend smoothing
history_buffer = deque(maxlen=200)  # covers ~1 hour at ~30s intervals

# Input data model (9 features)
class UsageInput(BaseModel):
    CPU_Usage: float
    Memory_Usage: float
    RequestRate: float
    CPU_Limit: float
    Memory_Limit: float
    Latency: float
    RequestRate_Delta: float
    Hour_sin: float
    Hour_cos: float

# Output response model
class PredictionResponse(BaseModel):
    forecast: dict
    safe_range: dict
    status: str

@app.get("/")
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
        # Prepare full 9-feature input
        X = np.array([[
            input.CPU_Usage,
            input.Memory_Usage,
            input.RequestRate,
            input.CPU_Limit,
            input.Memory_Limit,
            input.Latency,
            input.RequestRate_Delta,
            input.Hour_sin,
            input.Hour_cos
        ]])

        # Scale features
        X_scaled = scaler.transform(X)
        now = datetime.now()

        # Store in buffer
        history_buffer.append((now, X_scaled[0]))

        # Use last 1 hour of data
        cutoff = now - timedelta(hours=1)
        recent_data = np.array([x[1] for x in history_buffer if x[0] >= cutoff])

        if recent_data.shape[0] == 0:
            raise HTTPException(status_code=400, detail="Insufficient recent data for prediction")

        # Aggregate for prediction
        input_for_prediction = recent_data.mean(axis=0).reshape(1, -1)

        # Predict future deltas
        pred_cpu_delta, pred_mem_delta = model.predict_usage(input_for_prediction)

        if pred_cpu_delta is None or pred_mem_delta is None:
            raise HTTPException(status_code=500, detail="Model prediction failed")

        # Compute future usage
        future_cpu = input.CPU_Usage + pred_cpu_delta[0]
        future_mem = max(0, input.Memory_Usage + pred_mem_delta[0])

        # Estimate safe operating range
        safe_range = model.safe_range(future_cpu, future_mem)

        # Online training if we have enough history
        if len(recent_data) >= 2:
            prev_cpu = recent_data[-2][0]
            prev_mem = recent_data[-2][1]
            y_cpu = np.array([input.CPU_Usage - prev_cpu])
            y_mem = np.array([input.Memory_Usage - prev_mem])
            model.partial_fit(X_scaled, y_cpu, y_mem)
            model.save(MODEL_PATH)

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
