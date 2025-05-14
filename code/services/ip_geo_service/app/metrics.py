from prometheus_client import start_http_server, Summary, Counter
import time
from flask import Flask, request

# Prometheus metrics
REQUEST_LATENCY = Summary("request_latency_seconds", "Request latency", ["path"])
REQUEST_COUNT = Counter("request_count_total", "Total number of requests", ["path"])

# Start Prometheus metrics server (bind to all interfaces)
def start_metrics_server():
    start_http_server(port=9090, addr="0.0.0.0")  
