from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from dare_tl.model import TrendLearner

app = FastAPI()
MODEL_PATH = "./models/tl_model.pkl"
model = TrendLearner.load(MODEL_PATH)

class UsageInput(BaseModel):
    CPU_Limit: float
    Memory_Limit: float
    CPU_Usage: float
    Memory_Usage: float
    RequestRate: float

@app.post("/predict")
def predict(input: UsageInput):
    X = np.array([[input.CPU_Limit, input.Memory_Limit, input.CPU_Usage, input.Memory_Usage, input.RequestRate]])
    pred_cpu_delta, pred_mem_delta = model.predict_usage(X)

    future_cpu = input.CPU_Usage + pred_cpu_delta[0]
    future_mem = input.Memory_Usage + pred_mem_delta[0]
    safe_range = model.safe_range(future_cpu, future_mem)

    return {
        "forecast": {
            "CPU_Usage_Forecast": round(future_cpu, 2),
            "Memory_Usage_Forecast": round(future_mem, 2)
        },
        "safe_range": safe_range
    }
