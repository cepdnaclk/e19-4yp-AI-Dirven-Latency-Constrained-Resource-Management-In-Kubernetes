import requests
import logging

PROMETHEUS_URL = "http://prometheus-service.monitoring:9090"
logger = logging.getLogger("auto_updater")

def query_prometheus(query):
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        result = response.json()["data"]["result"]
        return result
    except Exception as e:
        logger.error(f"Failed to query Prometheus: {e}")
        return []

def get_cpu_query(pod, duration="1h"):
    return f'rate(container_cpu_usage_seconds_total{{pod="{pod}"}}[1h]) * 100'

def get_memory_query(pod):
    return f'container_memory_usage_bytes{{pod="{pod}"}}'