from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from trend_learner.trainer import TrendLearner
from trend_learner.predictor import get_safe_resource_ranges

app = FastAPI(title="DARE Trend Learner API")

# Global TL instance (we can later make this per-service/microservice)
tl = TrendLearner()

class MetricInput(BaseModel):
    req_rate: float
    timestamp: float
    cpu_usage: float
    mem_usage: float

class PredictionOutput(BaseModel):
    predicted_cpu: float
    predicted_mem: float
    safe_range: dict

@app.post("/predict", response_model=PredictionOutput)
def predict_trend(data: MetricInput):
    try:
        # Update the TL with current usage
        tl.update(data.req_rate, data.timestamp, data.cpu_usage, data.mem_usage)

        
        # Predict next-step usage
        cpu_pred, mem_pred = tl.predict_next(data.req_rate, data.timestamp + 1)

        # Get safe resource ranges
        ranges = get_safe_resource_ranges(cpu_pred, mem_pred)

        return {
            "predicted_cpu": round(cpu_pred, 2),
            "predicted_mem": round(mem_pred, 2),
            "safe_range": ranges
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "DARE Trend Learner API is running. Use POST /predict"}
