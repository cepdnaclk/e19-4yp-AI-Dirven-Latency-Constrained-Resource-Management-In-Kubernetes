import logging
import sys
import signal
import threading
import time

from auto_updater.prometheus_client import query_prometheus, get_cpu_query, get_memory_query
from auto_updater.analyzer import (
    get_combined_resource_updates,
    reduce_resources_periodically,
    stop_resource_reduction,
    track_resource_allocation,
    apply_resource_reduction
)
from auto_updater.k8s_updater import update_resources
from auto_updater.config import SERVICES, CPU_THRESHOLD, MEMORY_THRESHOLD, MAX_MEMORY_LIMIT

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("auto_updater")

# Flag to control the main loop
running = True

def signal_handler(sig, frame):
    global running
    logger.info("Shutdown signal received. Stopping services...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def calculate_resource_usage(metrics, resource_type="cpu"):
    usage_map = {}
    for metric in metrics:
        container = metric["metric"].get("container")
        value = float(metric["value"][1])

        if resource_type == "memory":
            value_mi = value / (1024 * 1024)
            usage_percent = (value_mi / MAX_MEMORY_LIMIT) * 100
        else:
            usage_percent = value

        usage_map[container] = usage_percent
    return usage_map

def main():
    logger.info("Starting auto updater service")

    container_names = [svc["container"] for svc in SERVICES]
    reduction_thread = reduce_resources_periodically(interval=10)
    logger.info("Resource reduction thread started")

    try:
        while running:
            for svc in SERVICES:
                container = svc["container"]
                deployment = svc["name"]
                namespace = svc["namespace"]

                logger.info(f"Checking resources for {container}")

                cpu_metrics = query_prometheus(get_cpu_query(container, duration="1h"))
                if not cpu_metrics:
                    logger.warning(f"No CPU metrics found for {container}")
                    continue

                mem_metrics = query_prometheus(get_memory_query(container, duration="1h"))
                if not mem_metrics:
                    logger.warning(f"No memory metrics found for {container}")
                    continue

                cpu_usage = calculate_resource_usage(cpu_metrics, "cpu")
                mem_usage = calculate_resource_usage(mem_metrics, "memory")

                container_cpu_usage = cpu_usage.get(container, 0)
                container_mem_usage = mem_usage.get(container, 0)

                logger.info(f"{container} - CPU: {container_cpu_usage:.2f}%, Memory: {container_mem_usage:.2f}%")

                cpu_high = container_cpu_usage > CPU_THRESHOLD
                mem_high = container_mem_usage > MEMORY_THRESHOLD * 100

                if cpu_high or mem_high:
                    logger.info(f"{container} - High resource usage detected")
                    updates = get_combined_resource_updates(cpu_metrics, mem_metrics, headroom=0.2)
                    if container in updates:
                        container_updates = updates[container]
                        cpu_value = container_updates.get("cpu")
                        mem_value = container_updates.get("memory")

                        if cpu_value or mem_value:
                            logger.info(f"Updating {container} - CPU: {cpu_value}, Memory: {mem_value}Mi")
                            update_resources(deployment, container, namespace, cpu=cpu_value, memory=mem_value)
                            track_resource_allocation(container, cpu=cpu_value, memory=mem_value)
                else:
                    logger.info(f"{container} - Applying gradual reduction")
                    reductions = apply_resource_reduction()
                    container_reductions = [(c, r_type, value) for c, r_type, value in reductions if c == container]

                    if container_reductions:
                        cpu_value = next((value for c, r_type, value in container_reductions if r_type == "cpu"), None)
                        mem_value = next((value for c, r_type, value in container_reductions if r_type == "memory"), None)

                        if cpu_value or mem_value:
                            logger.info(f"Reducing {container} - CPU: {cpu_value}, Memory: {mem_value}Mi")
                            update_resources(deployment, container, namespace, cpu=cpu_value, memory=mem_value)
                    else:
                        logger.info(f"No reductions needed for {container}")
            time.sleep(30)

    except Exception as e:
        logger.error(f"Error in main loop: {e}", exc_info=True)
    finally:
        logger.info("Stopping resource reduction thread")
        stop_resource_reduction()
        if reduction_thread:
            reduction_thread.join(timeout=5)
        logger.info("Auto updater service stopped")

if __name__ == "__main__":
    main()