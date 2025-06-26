# scraper_server.py
import asyncio
import requests
import json
from datetime import datetime
import websockets

PROMETHEUS_URL = "http://localhost:9090"

JAVA_SERVICES = [
    {
        "name": "color-code-converter-deployment",
        "container": "color-code-converter-container",
        "pod": "color-code-converter-deployment-[a-z0-9]+-[a-z0-9]+",
        "namespace": "default"
    }
]

connected_clients = set()

# --- Your original metric functions ---
def query_prometheus(query):
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    if response.status_code == 200:
        return response.json()["data"]["result"]
    else:
        raise Exception(f"Query failed: {response.status_code} {response.text}")

def get_container_cpu_usage(pod):
    return query_prometheus(f'sum(rate(container_cpu_usage_seconds_total{{pod=~"{pod}"}}[1h]))')

def get_container_memory_usage_bytes(pod):
    return query_prometheus(f'container_memory_usage_bytes{{pod=~"{pod}"}}')

def get_container_cpu_request(pod):
    result = query_prometheus(f'kube_pod_container_resource_requests{{pod=~"{pod}", resource="cpu", unit="core"}}')
    return result[0]['value'][1] if result else "N/A"

def get_container_memory_request(pod):
    result = query_prometheus(f'kube_pod_container_resource_requests{{pod=~"{pod}", resource="memory", unit="byte"}}')
    return result[0]['value'][1] if result else "N/A"

def get_container_cpu_limit(pod):
    result = query_prometheus(f'kube_pod_container_resource_limits{{pod=~"{pod}", resource="cpu", unit="core"}}')
    return result[0]['value'][1] if result else "N/A"

def get_container_memory_limit(pod):
    result = query_prometheus(f'kube_pod_container_resource_limits{{pod=~"{pod}", resource="memory", unit="byte"}}')
    return result[0]['value'][1] if result else "N/A"

def get_latency_java(pod):
    result = query_prometheus(
        f'sum(rate(http_server_requests_seconds_sum{{pod=~"{pod}"}}[1h])) '
        f'/ sum(rate(http_server_requests_seconds_count{{pod=~"{pod}", outcome="SUCCESS"}}[1h]))'
    )
    return float(result[0]['value'][1]) if result else 0

def get_container_cpu_throttling(pod):
    result = query_prometheus(f'container_cpu_cfs_throttled_seconds_total{{pod=~"{pod}"}}')
    return result[0]['value'][1] if result else "N/A"

def get_container_memory_working_set(pod):
    result = query_prometheus(f'container_memory_working_set_bytes{{pod=~"{pod}"}}')
    return result[0]['value'][1] if result else "N/A"

# --- WebSocket push logic ---
async def handle_client(ws):
    connected_clients.add(ws)
    try:
        await ws.wait_closed()
    finally:
        connected_clients.remove(ws)

async def push_loop():
    while True:
        for service in JAVA_SERVICES:
            pod = service["pod"]
            name = service["name"]

            cpu_request = get_container_cpu_request(pod)
            mem_request = get_container_memory_request(pod)
            cpu_limit = get_container_cpu_limit(pod)
            mem_limit = get_container_memory_limit(pod)
            latency = get_latency_java(pod)
            cpu_result = get_container_cpu_usage(pod)
            mem_result = get_container_memory_usage_bytes(pod)
            cpu_throttling = get_container_cpu_throttling(pod)
            mem_working_set = get_container_memory_working_set(pod)

            timestamp = datetime.fromtimestamp(float(cpu_result[0]['value'][0])).isoformat() if cpu_result else "N/A"
            cpu_value = cpu_result[0]['value'][1] if cpu_result else "N/A"
            mem_bytes = mem_result[0]['value'][1] if mem_result else "N/A"

            data = {
                "Timestamp": timestamp,
                "Service": name,
                "CPU Request": cpu_request,
                "Memory Request": mem_request,
                "CPU Limit": cpu_limit,
                "Memory Limit": mem_limit,
                "Latency": latency,
                "CPU Usage": cpu_value,
                "Memory Usage": mem_bytes,
                "CPU Throttling": cpu_throttling,
                "Memory Working Set": mem_working_set
            }
            print(1)
            if connected_clients:
                await asyncio.gather(*(ws.send(json.dumps(data)) for ws in connected_clients))

        await asyncio.sleep(5)

async def main():
    print("WebSocket server listening at ws://0.0.0.0:8765")
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        await push_loop()

if __name__ == "__main__":
    asyncio.run(main())
