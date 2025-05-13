from prometheus_client import start_http_server, Summary, Counter

REQUEST_LATENCY = Summary("request_latency_seconds", "Request latency", ["path"])
REQUEST_COUNT = Counter("request_count_total", "Total number of requests", ["path"])

def start_metrics_server():
    start_http_server(9090)  # Prometheus will scrape here
