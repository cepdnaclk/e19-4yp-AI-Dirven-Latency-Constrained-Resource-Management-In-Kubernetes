import requests
from .config import PROMETHEUS_URL, PROMETHEUS_QUERY_CPU

def query_prometheus(query):
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    response.raise_for_status()
    results = response.json()["data"]["result"]
    return results