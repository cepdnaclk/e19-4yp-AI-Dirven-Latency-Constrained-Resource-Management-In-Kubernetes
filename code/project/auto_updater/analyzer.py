from auto_updater.config import CPU_THRESHOLD, MEMORY_THRESHOLD, MAX_MEMORY_LIMIT
import threading
import time

allocation_log = {}
reduction_running = True

def get_combined_resource_updates(cpu_metrics, memory_metrics):
    updates = {}
    for metric in cpu_metrics:
        pod = metric["metric"].get("pod")
        cpu_value = float(metric["value"][1]) * 1.2
        updates[pod] = {"cpu": f"{cpu_value:.2f}"}

    for metric in memory_metrics:
        pod = metric["metric"].get("pod")
        mem_bytes = float(metric["value"][1])
        mem_mi = mem_bytes / (1024 * 1024)
        mem_value = min(mem_mi * 1.2, MAX_MEMORY_LIMIT)
        if pod in updates:
            updates[pod]["memory"] = f"{mem_value:.2f}"
        else:
            updates[pod] = {"memory": f"{mem_value:.2f}"}

    return updates

def track_resource_allocation(pod, cpu=None, memory=None):
    allocation_log[pod] = {"cpu": cpu, "memory": memory, "timestamp": time.time()}

def apply_resource_reduction():
    reductions = []
    now = time.time()
    for pod, info in allocation_log.items():
        if now - info["timestamp"] > 3600:
            new_cpu = float(info["cpu"]) * 0.9 if info["cpu"] else None
            new_mem = float(info["memory"]) * 0.9 if info["memory"] else None
            if new_cpu:
                reductions.append((pod, "cpu", f"{new_cpu:.2f}"))
            if new_mem:
                reductions.append((pod, "memory", f"{new_mem:.2f}"))
    return reductions

def reduce_resources_periodically(interval=300):
    def reducer():
        while reduction_running:
            apply_resource_reduction()
            time.sleep(interval)

    t = threading.Thread(target=reducer)
    t.start()
    return t

def stop_resource_reduction():
    global reduction_running
    reduction_running = False