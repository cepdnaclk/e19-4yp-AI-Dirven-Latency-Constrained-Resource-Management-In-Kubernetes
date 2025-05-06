from fastapi import FastAPI, Request
from app.geo_utils import get_geolocation
from app.metrics import (
    REQUEST_LATENCY, REQUEST_COUNT, start_metrics_server
)
import time

app = FastAPI()

@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time

    path = request.url.path
    REQUEST_LATENCY.labels(path=path).observe(latency)
    REQUEST_COUNT.labels(path=path).inc()

    return response

@app.get("/geoip")
def geoip_lookup(ip: str):
    result = get_geolocation(ip)
    return result

@app.on_event("startup")
def setup_metrics():
    start_metrics_server()  # runs Prometheus server on port 8001
