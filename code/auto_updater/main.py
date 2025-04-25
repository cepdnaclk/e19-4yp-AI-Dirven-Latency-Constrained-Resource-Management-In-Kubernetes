from auto_updater.prometheus_client import query_prometheus
from auto_updater.analyzer import analyze_cpu_usage
from auto_updater.k8s_updater import update_cpu_resources
from auto_updater.config import PROMETHEUS_QUERY_CPU

def main():
    print("Querying Prometheus for CPU metrics...")
    metrics = query_prometheus(PROMETHEUS_QUERY_CPU)
    print(f"Retrieved {len(metrics)} metrics.")

    updates = analyze_cpu_usage(metrics)
    print(f"Updates to apply: {updates}")

    for container, new_cpu in updates:
        print(f"Updating container {container} to CPU {new_cpu} cores")
        update_cpu_resources(new_cpu)

if __name__ == "__main__":
    main()