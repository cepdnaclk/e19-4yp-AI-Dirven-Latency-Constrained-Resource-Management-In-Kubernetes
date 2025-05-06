from auto_updater.prometheus_client import query_prometheus, get_cpu_query, get_memory_query
from auto_updater.analyzer import analyze_cpu, analyze_memory
from auto_updater.k8s_updater import update_resources
from auto_updater.config import SERVICES, CPU_THRESHOLD, MEMORY_THRESHOLD, MAX_MEMORY_LIMIT
from auto_updater.analyzer import (
    get_combined_resource_updates,
    reduce_resources_periodically,
    stop_resource_reduction,
    track_resource_allocation,
    apply_resource_reduction
)
import logging
import time
import sys
import signal
import threading

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
    """Handle termination signals"""
    global running
    logger.info("Shutdown signal received. Stopping services...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def calculate_resource_usage(metrics, resource_type="cpu"):
    """
    Calculate the current resource usage percentage from metrics
    
    Args:
        metrics: List of metrics from Prometheus
        resource_type: Either "cpu" or "memory"
    
    Returns:
        Dictionary mapping container names to their usage percentage
    """
    usage_map = {}
    
    for metric in metrics:
        container = metric["metric"].get("container")
        value = float(metric["value"][1])
        
        if resource_type == "memory":
            # Convert bytes to Mi
            value_mi = value / (1024 * 1024)
            # Calculate percentage of max memory
            usage_percent = (value_mi / MAX_MEMORY_LIMIT) * 100
        else:  # CPU
            # Assuming value is already percentage
            usage_percent = value
            
        usage_map[container] = usage_percent
    
    return usage_map

def main():
    """Main application logic"""
    logger.info("Starting auto updater service")
    
    # Start the periodic resource reduction thread
    reduction_thread = threading.Thread(target=reduce_resources_periodically, args=(10,))
    reduction_thread.start()
    logger.info("Resource reduction thread started")
    
    try:
        while running:
            for svc in SERVICES:
                container = svc["container"]
                pod = svc["pod"]
                deployment = svc["name"]
                namespace = svc["namespace"]
                
                logger.info(f"Checking resources for {container}")
                
                # Get CPU metrics
                cpu_metrics = query_prometheus(get_cpu_query(container))
                if not cpu_metrics:
                    logger.warning(f"No CPU metrics found for {container}")
                    continue
                
                # Get memory metrics
                mem_metrics = query_prometheus(get_memory_query(container))
                if not mem_metrics:
                    logger.warning(f"No memory metrics found for {container}")
                    continue
                
                # Calculate current usage percentages
                cpu_usage = calculate_resource_usage(cpu_metrics, "cpu")
                mem_usage = calculate_resource_usage(mem_metrics, "memory")
                
                # Get current container's usage values
                container_cpu_usage = cpu_usage.get(container, 0)
                container_mem_usage = mem_usage.get(container, 0)
                
                logger.info(f"{container} - Current CPU: {container_cpu_usage:.2f}%, Memory: {container_mem_usage:.2f}%")
                
                # Check if usage is above threshold
                cpu_high = container_cpu_usage > CPU_THRESHOLD
                mem_high = container_mem_usage > MEMORY_THRESHOLD * 100
                
                if cpu_high or mem_high:
                    # If resource usage is above 80%, use the standard analysis to reduce resources
                    logger.info(f"{container} - High resource usage detected - applying resource scaling")
                    
                    # Get updates using standard analysis
                    updates = get_combined_resource_updates(cpu_metrics, mem_metrics)
                    
                    # Extract updates for this container
                    if container in updates:
                        container_updates = updates[container]
                        cpu_value = container_updates.get("cpu")
                        mem_value = container_updates.get("memory")
                        
                        # Update resources if needed
                        if cpu_value or mem_value:
                            logger.info(f"Updating {container} - CPU: {cpu_value}, Memory: {mem_value}Mi")
                            update_resources(deployment, container, namespace, cpu=cpu_value, memory=mem_value)
                            
                            # Track the allocation for future reductions
                            track_resource_allocation(container, cpu=cpu_value, memory=mem_value)
                else:
                    # If resource usage is below threshold, apply gradual reduction
                    logger.info(f"{container} - Resource usage within limits - applying gradual reduction")
                    
                    # Apply immediate reduction for this container
                    reductions = apply_resource_reduction()
                    
                    # Filter reductions for this container
                    container_reductions = [(c, r_type, value) for c, r_type, value in reductions if c == container]
                    
                    if container_reductions:
                        # Extract CPU and memory values
                        cpu_value = next((value for c, r_type, value in container_reductions 
                                        if c == container and r_type == "cpu"), None)
                        mem_value = next((value for c, r_type, value in container_reductions 
                                        if c == container and r_type == "memory"), None)
                        
                        if cpu_value or mem_value:
                            logger.info(f"Reducing {container} - CPU: {cpu_value}, Memory: {mem_value}Mi")
                            update_resources(deployment, container, namespace, cpu=cpu_value, memory=mem_value)
                    else:
                        logger.info(f"No reductions needed for {container}")
            
            # Wait before next check
            time.sleep(30)
            
    except Exception as e:
        logger.error(f"Error in main loop: {e}", exc_info=True)
    finally:
        # Stop the reduction thread
        logger.info("Stopping resource reduction thread")
        stop_resource_reduction()
        
        # Wait for thread to complete
        if reduction_thread:
            reduction_thread.join(timeout=5)
        
        logger.info("Auto updater service stopped")

if __name__ == "__main__":
    main()