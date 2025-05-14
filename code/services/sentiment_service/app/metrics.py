from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil
import os
import threading
import time

REQUEST_COUNT = Counter("request_count", "Total number of requests", ["path"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Latency per request", ["path"])

CPU_USAGE = Gauge("container_cpu_usage", "CPU usage %")
MEMORY_USAGE = Gauge("container_memory_usage", "Memory usage in bytes")
CPU_REQUEST = Gauge("container_cpu_request", "Requested CPU")
MEMORY_REQUEST = Gauge("container_memory_request", "Requested memory")
CPU_LIMIT = Gauge("container_cpu_limit", "CPU limit")
MEMORY_LIMIT = Gauge("container_memory_limit", "Memory limit")

def collect_container_metrics():
    while True:
        process = psutil.Process(os.getpid())
        CPU_USAGE.set(process.cpu_percent(interval=None))
        MEMORY_USAGE.set(process.memory_info().rss)
        # You can set static values from env vars or K8s Downward API for requests/limits
        CPU_REQUEST.set(100)
        MEMORY_REQUEST.set(128 * 1024 * 1024)
        CPU_LIMIT.set(200)
        MEMORY_LIMIT.set(256 * 1024 * 1024)
        time.sleep(5)

def start_metrics_server():
    start_http_server(port=9090, addr="0.0.0.0")
    thread = threading.Thread(target=collect_container_metrics)
    thread.daemon = True
    thread.start()
