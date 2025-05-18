import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Prometheus server URL
PROM_URL = "http://localhost:9090"

# Time range for the query
start = "2025-05-11T00:00:00Z"
end = "2025-05-12T01:00:00Z"
step = "30s"  # 30-second resolution

# Pod identifier for service-1
pod_label = "service-1"

def query_range(metric):
    url = f"{PROM_URL}/api/v1/query_range"
    params = {
        'query': metric,
        'start': start,
        'end': end,
        'step': step
    }
    response = requests.get(url, params=params).json()
    result = response['data']['result']

    if not result:
        print(f"No data found for {metric}")
        return pd.DataFrame()

    values = result[0]['values']
    timestamps = [datetime.fromtimestamp(float(t)) for t, _ in values]
    data = [float(v) for _, v in values]
    return pd.DataFrame({'timestamp': timestamps, metric: data})


# Define the metrics with pod label filtering for service-1
latency_metric = f'histogram_quantile(0.95, rate(http_server_requests_seconds_bucket{{pod=~"{pod_label}.*"}}[1m]))'
queue_metric = f'executor_queued{{pod=~"{pod_label}.*"}}'

# Query Prometheus
latency_df = query_range(latency_metric)
queue_df = query_range(queue_metric)

# Merge the data on timestamp
if not latency_df.empty and not queue_df.empty:
    df = pd.merge(latency_df, queue_df, on='timestamp', how='inner')

    # Plot the metrics
    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df[latency_metric], label='Latency (95th percentile, s)', color='red')
    plt.plot(df['timestamp'], df[queue_metric], label='Queued Requests', color='blue')
    plt.legend()
    plt.title("Service-1: Latency vs Queued Requests Over Time")
    plt.xlabel("Time")
    plt.ylabel("Metric Value")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("Unable to fetch or merge data.")
