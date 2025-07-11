import csv
import os
import threading
from datetime import datetime
import time
import requests

PROMETHEUS_URL = "http://localhost:9090"

JAVA_SERVICES = [
    {
        "name": "service-1-deployment",
        "container": "service-1-container",
        "pod": "service-1-deployment-[a-z0-9]+-[a-z0-9]+",
        "namespace": "default",
        "app_label": "service-1"
    },
    {
        "name": "rand-pw-gen-deployment",
        "container": "rand-pw-gen-container",
        "pod": "rand-pw-gen-deployment-[a-z0-9]+-[a-z0-9]+",
        "namespace": "default",
        "app_label": "rand-pw-gen"
        
    },
    {
        "name": "hash-gen-deployment",
        "container": "hash-gen-container",
        "pod": "hash-gen-deployment-[a-z0-9]+-[a-z0-9]+",
        "namespace": "default",
        "app_label": "hash-gen"
    }
    
]

GO_SERVICES = [
    {
        "name": "service-2-deployment",
        "container": "service-2-container",
        "pod": "service-2-deployment-[a-z0-9]+-[a-z0-9]+",
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
    query = (
        f'sum(rate(container_cpu_usage_seconds_total{{'
        f'pod=~"{pod}"}}[1h]))'
    )
    result = query_prometheus(query)
    return result


def get_container_memory_usage_bytes(pod):
    query = f'container_memory_usage_bytes{{pod=~"{pod}"}}'
    result = query_prometheus(query)
    return result

def get_container_cpu_request(pod):
    query = f'kube_pod_container_resource_requests{{pod=~"{pod}", resource="cpu", unit="core"}}'
    result = query_prometheus(query)
    return result[0]['value'][1]

def get_container_memory_request(pod):
    query = f'kube_pod_container_resource_requests{{pod=~"{pod}", resource="memory", unit="byte"}}'
    result = query_prometheus(query)
    return result[0]['value'][1]

def get_container_cpu_limit(pod):
    query = f'kube_pod_container_resource_limits{{pod=~"{pod}", resource="cpu", unit="core"}}'
    result = query_prometheus(query)
    return result[0]['value'][1]

def get_container_memory_limit(pod):
    query = f'kube_pod_container_resource_limits{{pod=~"{pod}", resource="memory", unit="byte"}}'
    result = query_prometheus(query)
    return result[0]['value'][1]

def get_request_rate_java(pod, app_label):
    query = (
        f'sum(rate(http_server_requests_seconds_count{{'
        f'namespace="default", '
        f'app="{app_label}", '
        f'pod=~"{pod}", '
        f'outcome="SUCCESS", '
        f'status=~"2.."'
        f'}}[5m]))'
    )
    result = query_prometheus(query)
    return float(result[0]['value'][1]) if result else 0

def get_request_rate_go(pod):
    query = f'sum(rate(echo_number_request_duration_seconds_count{{pod=~"{pod}"}}[5m]))'
    result = query_prometheus(query)
    return float(result[0]['value'][1]) if result else 0


def get_latency_java(pod, app_label):
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


def get_latency_go(pod):
    query = (
        f"(sum by (pod) ("
        f"rate(echo_number_request_duration_seconds_sum{{pod=~\"{pod}\"}}[1h])"
        f")) / (sum by (pod) ("
        f"rate(echo_number_request_duration_seconds_count{{pod=~\"{pod}\"}}[1h])"
        f"))"
    )
    result =  query_prometheus(query)
    if result:
        # Extract the value from the result
        avg_latency_per_request = float(result[0]['value'][1])  # Average latency per request
        return avg_latency_per_request
    else:
        return 0  # If no data is returned, return 0

# Function to write data to CSV for each service
def write_to_csv(data, service_name):
    file_name = f"{service_name}_dataset.csv"
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Write headers if the file is being created for the first time
        if not file_exists:
            headers = ["Timestamp", "Service", "CPU Request", "Memory Request", "CPU Limit", "Memory Limit",
                       "Latency", "CPU Usage", "Memory Usage", "Request Rate"]
            writer.writerow(headers)

        writer.writerow(data)



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
            app_label = service.get("app_label", "") 
            latency = latency_func(pod, app_label) if latency_func == get_latency_java else latency_func(pod)

            # CPU and Memory Usage
            cpu_result = get_container_cpu_usage(pod)
            mem_result = get_container_memory_usage_bytes(pod)

            # Timestamp and values
            cpu_timestamp = datetime.fromtimestamp(float(cpu_result[0]['value'][0])).isoformat() if cpu_result else "N/A"
            cpu_value = cpu_result[0]['value'][1] if cpu_result else "N/A"

            mem_timestamp = datetime.fromtimestamp(float(mem_result[0]['value'][0])).isoformat() if mem_result else "N/A"
            mem_bytes = mem_result[0]['value'][1] if mem_result else "N/A"

            timestamp = cpu_timestamp if cpu_timestamp != "N/A" else mem_timestamp
            
            # Request rate
            app_label = service.get("app_label", "")  # fallback in case it's not set
            req_rate = get_request_rate_java(pod, app_label) if latency_func == get_latency_java else get_request_rate_go(pod)


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
                req_rate
            ]

            write_to_csv(data, name)

        time.sleep(interval)

def main():
    # Define the threads
    java_thread = threading.Thread(target=scrape_data, args=(JAVA_SERVICES, get_latency_java))
    go_thread = threading.Thread(target=scrape_data, args=(GO_SERVICES, get_latency_go))

    # Start the threads
    java_thread.start()
    go_thread.start()

    # (Optional) Wait for both threads to finish, which they never will in this loop unless interrupted
    java_thread.join()
    go_thread.join()

if __name__ == "__main__":
    main()




