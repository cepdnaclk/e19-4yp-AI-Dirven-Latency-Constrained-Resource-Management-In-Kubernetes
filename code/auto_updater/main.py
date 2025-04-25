from auto_updater.prometheus_client import query_prometheus, get_cpu_query, get_memory_query
from auto_updater.analyzer import analyze_cpu_usage, analyze_memory_usage
from auto_updater.k8s_updater import update_resources
from auto_updater.config import SERVICES

def main():
    for svc in SERVICES:
        container = svc["container"]
        deployment = svc["name"]
        namespace = svc["namespace"]

        print(f" Checking CPU for {container}")
        cpu_metrics = query_prometheus(get_cpu_query(container))
        cpu_updates = analyze_cpu_usage(cpu_metrics)

        print(f" Checking Memory for {container}")
        mem_metrics = query_prometheus(get_memory_query(container))
        mem_updates = analyze_memory_usage(mem_metrics)

        cpu_value = next((val for t, val in cpu_updates if t == "cpu"), None)
        mem_value = next((val for t, val in mem_updates if t == "memory"), None)

        if cpu_value or mem_value:
            print(f" Updating {container} - CPU: {cpu_value}, Memory: {mem_value}Mi")
            update_resources(deployment, container, namespace, cpu=cpu_value, memory=mem_value)
