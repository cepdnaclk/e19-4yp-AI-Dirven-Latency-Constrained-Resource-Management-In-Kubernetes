import requests
from .config import PROMETHEUS_URL, PROMETHEUS_QUERY_CPU

def query_prometheus(query):
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    response.raise_for_status()
    results = response.json()["data"]["result"]
    return results

def get_cpu_query(container_name):
    return f'rate(container_cpu_usage_seconds_total{{container="{container_name}"}}[1h])'

def get_memory_query(container):
    return f'container_memory_usage_bytes{{container="{container_name}"}}'