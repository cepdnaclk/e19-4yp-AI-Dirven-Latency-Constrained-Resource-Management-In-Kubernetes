from fastapi import FastAPI, Request
from app.sentiment import analyze_sentiment
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY, start_metrics_server
import time

app = FastAPI()

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = time.time() - start
    path = request.url.path
    REQUEST_COUNT.labels(path=path).inc()
    REQUEST_LATENCY.labels(path=path).observe(latency)
    return response

@app.on_event("startup")
def on_startup():
    start_metrics_server()

@app.get("/sentiment")
def get_sentiment(text: str):
    return {"sentiment": analyze_sentiment(text)}
