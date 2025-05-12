import csv
import os
import threading
from datetime import datetime
import time
import requests

PROMETHEUS_URL = "http://localhost:9090"

JAVA_SERVICES = [
    {
        "name": "color-code-converter-deployment",
        "container": "color-code-converter-container",
        "pod": "color-code-converter-deployment-[a-z0-9]+-[a-z0-9]+",
        "namespace": "default"
    }
]

# Query Prometheus function
def query_prometheus(query):
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    if response.status_code == 200:
        return response.json()["data"]["result"]
    else:
        raise Exception(f"Query failed: {response.status_code} {response.text}")

# CPU Usage function for the container
def get_container_cpu_usage(pod):
    query = (
        f'sum(rate(container_cpu_usage_seconds_total{{'
        f'pod=~"{pod}"}}[1h]))'
    )
    result = query_prometheus(query)
    return result if result else None

# Memory usage in bytes function for the container
def get_container_memory_usage_bytes(pod):
    query = f'container_memory_usage_bytes{{pod=~"{pod}"}}'
    result = query_prometheus(query)
    return result if result else None

# CPU Request function for the container
def get_container_cpu_request(pod):
    query = f'kube_pod_container_resource_requests{{pod=~"{pod}", resource="cpu", unit="core"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

# Memory Request function for the container
def get_container_memory_request(pod):
    query = f'kube_pod_container_resource_requests{{pod=~"{pod}", resource="memory", unit="byte"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

# CPU Limit function for the container
def get_container_cpu_limit(pod):
    query = f'kube_pod_container_resource_limits{{pod=~"{pod}", resource="cpu", unit="core"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

# Memory Limit function for the container
def get_container_memory_limit(pod):
    query = f'kube_pod_container_resource_limits{{pod=~"{pod}", resource="memory", unit="byte"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

# Latency function for Java-based services
def get_latency_java(pod):
    # Query for total request time in the last hour
    latency_sum_query = (
        f'sum(rate(http_server_requests_seconds_sum{{pod=~"{pod}"}}[1h])) '
        f'/ sum(rate(http_server_requests_seconds_count{{pod=~"{pod}", outcome="SUCCESS"}}[1h]))'
    )

    # Fetch the data for the query
    result = query_prometheus(latency_sum_query)

    # If the query returns results, calculate the average latency per request
    if result:
        # Extract the value from the result
        avg_latency_per_request = float(result[0]['value'][1])  # Average latency per request
        return avg_latency_per_request
    else:
        return 0  # If no data is returned, return 0

# Function to handle CPU Throttling (CFS Throttling)
def get_container_cpu_throttling(pod):
    query = f'container_cpu_cfs_throttled_seconds_total{{pod=~"{pod}"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

# Function to handle Memory Working Set (active memory excluding cached)
def get_container_memory_working_set(pod):
    query = f'container_memory_working_set_bytes{{pod=~"{pod}"}}'
    result = query_prometheus(query)
    return result[0]['value'][1] if result else "N/A"

# Function to write data to CSV for each service
def write_to_csv(data, service_name):
    file_name = f"{service_name}_dataset.csv"
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write headers if the file is being created for the first time
        if not file_exists:
            headers = ["Timestamp", "Service", "CPU Request", "Memory Request", "CPU Limit", "Memory Limit",
                       "Latency", "CPU Usage", "Memory Usage", "CPU Throttling", "Memory Working Set"]
            writer.writerow(headers)

        writer.writerow(data)

# Function to scrape data
def scrape_data(service_list, latency_func, interval=30):
    while True:
        for service in service_list:
            pod = service["pod"]
            name = service["name"]

            # Requests and Limits
            cpu_request = get_container_cpu_request(pod)
            mem_request = get_container_memory_request(pod)
            cpu_limit = get_container_cpu_limit(pod)
            mem_limit = get_container_memory_limit(pod)

            # Latency
            latency = latency_func(pod)

            # CPU and Memory Usage
            cpu_result = get_container_cpu_usage(pod)
            mem_result = get_container_memory_usage_bytes(pod)
            cpu_throttling = get_container_cpu_throttling(pod)
            mem_working_set = get_container_memory_working_set(pod)

            # Timestamp and values
            cpu_timestamp = datetime.fromtimestamp(float(cpu_result[0]['value'][0])).isoformat() if cpu_result else "N/A"
            cpu_value = cpu_result[0]['value'][1] if cpu_result else "N/A"

            mem_timestamp = datetime.fromtimestamp(float(mem_result[0]['value'][0])).isoformat() if mem_result else "N/A"
            mem_bytes = mem_result[0]['value'][1] if mem_result else "N/A"

            timestamp = cpu_timestamp if cpu_timestamp != "N/A" else mem_timestamp

            data = [
                timestamp,
                name,
                cpu_request,
                mem_request,
                cpu_limit,
                mem_limit,
                latency,
                cpu_value,
                mem_bytes,
                cpu_throttling,
                mem_working_set
            ]

            write_to_csv(data, name)

        time.sleep(interval)

# Main function to start scraping data
def main():
    # Define the threads
    java_thread = threading.Thread(target=scrape_data, args=(JAVA_SERVICES, get_latency_java))

    # Start the threads
    java_thread.start()

    # (Optional) Wait for both threads to finish, which they never will in this loop unless interrupted
    java_thread.join()

if __name__ == "__main__":
    main()
