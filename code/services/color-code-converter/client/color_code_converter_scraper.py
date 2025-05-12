import csv
import os
import threading
from datetime import datetime
import time
import requests
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

PROMETHEUS_URL = "http://localhost:9090"
CSV_FILE = "color-code-converter-deployment_dataset.csv"

JAVA_SERVICES = [
    {
        "name": "color-code-converter-deployment",
        "container": "color-code-converter-container",
        "pod": "color-code-converter-deployment-[a-z0-9]+-[a-z0-9]+",
        "namespace": "default"
    }
]

def query_prometheus(query):
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    if response.status_code == 200:
        return response.json()["data"]["result"]
    else:
        raise Exception(f"Query failed: {response.status_code} {response.text}")

def get_container_cpu_usage(pod):
    query = f'sum(rate(container_cpu_usage_seconds_total{{pod=~"{pod}"}}[1h]))'
    return query_prometheus(query)

def get_container_memory_usage_bytes(pod):
    query = f'container_memory_usage_bytes{{pod=~"{pod}"}}'
    return query_prometheus(query)

def get_container_cpu_request(pod):
    query = f'kube_pod_container_resource_requests{{pod=~"{pod}", resource="cpu", unit="core"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

def get_container_memory_request(pod):
    query = f'kube_pod_container_resource_requests{{pod=~"{pod}", resource="memory", unit="byte"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

def get_container_cpu_limit(pod):
    query = f'kube_pod_container_resource_limits{{pod=~"{pod}", resource="cpu", unit="core"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

def get_container_memory_limit(pod):
    query = f'kube_pod_container_resource_limits{{pod=~"{pod}", resource="memory", unit="byte"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

def get_latency_java(pod):
    query = (
        f'sum(rate(http_server_requests_seconds_sum{{pod=~"{pod}"}}[1h])) '
        f'/ sum(rate(http_server_requests_seconds_count{{pod=~"{pod}", outcome="SUCCESS"}}[1h]))'
    )
    result = query_prometheus(query)
    return float(result[0]['value'][1]) if result else 0

def get_container_cpu_throttling(pod):
    query = f'container_cpu_cfs_throttled_seconds_total{{pod=~"{pod}"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

def get_container_memory_working_set(pod):
    query = f'container_memory_working_set_bytes{{pod=~"{pod}"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

def write_to_csv(data, service_name):
    file_name = f"{service_name}_dataset.csv"
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Service", "CPU Request", "Memory Request",
                "CPU Limit", "Memory Limit", "Latency",
                "CPU Usage", "Memory Usage", "CPU Throttling", "Memory Working Set"
            ])
        writer.writerow(data)

def scrape_data(service_list, latency_func, interval=30):
    while True:
        for service in service_list:
            pod = service["pod"]
            name = service["name"]
            cpu_request = get_container_cpu_request(pod)
            mem_request = get_container_memory_request(pod)
            cpu_limit = get_container_cpu_limit(pod)
            mem_limit = get_container_memory_limit(pod)
            latency = latency_func(pod)
            cpu_result = get_container_cpu_usage(pod)
            mem_result = get_container_memory_usage_bytes(pod)
            cpu_throttling = get_container_cpu_throttling(pod)
            mem_working_set = get_container_memory_working_set(pod)

            cpu_timestamp = datetime.fromtimestamp(float(cpu_result[0]['value'][0])).isoformat() if cpu_result else "N/A"
            cpu_value = cpu_result[0]['value'][1] if cpu_result else "N/A"
            mem_timestamp = datetime.fromtimestamp(float(mem_result[0]['value'][0])).isoformat() if mem_result else "N/A"
            mem_bytes = mem_result[0]['value'][1] if mem_result else "N/A"
            timestamp = cpu_timestamp if cpu_timestamp != "N/A" else mem_timestamp

            data = [
                timestamp, name, cpu_request, mem_request, cpu_limit, mem_limit,
                latency, cpu_value, mem_bytes, cpu_throttling, mem_working_set
            ]
            write_to_csv(data, name)
        time.sleep(interval)

# ----------------- DASH APP -------------------
app = Dash(__name__)
app.layout = html.Div([
    html.H2("Real-time Resource Usage - Color Code Converter"),
    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0),
    dcc.Graph(id='live-graph')
])

@app.callback(
    Output('live-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    if not os.path.exists(CSV_FILE):
        return go.Figure()
    df = pd.read_csv(CSV_FILE)
    df = df.tail(100)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Latency"],
                             mode='lines+markers', name='Latency'))
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["CPU Usage"],
                             mode='lines+markers', name='CPU Usage'))
    fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["Memory Usage"],
                             mode='lines+markers', name='Memory Usage'))

    fig.update_layout(title="Live Resource Metrics",
                      xaxis_title="Timestamp",
                      yaxis_title="Metric Values")
    return fig

def start_dash():
    app.run(debug=False, host='0.0.0.0', port=8050)

# ---------------- MAIN -------------------
def main():
    t1 = threading.Thread(target=scrape_data, args=(JAVA_SERVICES, get_latency_java))
    t2 = threading.Thread(target=start_dash)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__ == "__main__":
    main()
