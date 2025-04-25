from auto_updater.prometheus_client import query_prometheus, get_cpu_query
from auto_updater.analyzer import analyze_cpu_usage
from auto_updater.k8s_updater import update_cpu_resources
from auto_updater.config import SERVICES

def main():
    for svc in SERVICES:
        print(f"Checking {svc['name']}...")
        query = get_cpu_query(svc['container'])
        metrics = query_prometheus(query)
        updates = analyze_cpu_usage(metrics)

        for _, new_cpu in updates:
            print(f"Updating {svc['name']} to {new_cpu} cores")
            update_cpu_resources(
                deployment=svc['name'],
                container=svc['container'],
                namespace=svc['namespace'],
                cpu_value=new_cpu
            )
