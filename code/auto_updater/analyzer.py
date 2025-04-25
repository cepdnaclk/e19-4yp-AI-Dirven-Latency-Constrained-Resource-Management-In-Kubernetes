from .config import CPU_THRESHOLD, CPU_INCREMENT, MAX_CPU_LIMIT

def analyze_cpu_usage(cpu_metrics):
    updates = []
    for metric in cpu_metrics:
        usage = float(metric["value"][1])
        container = metric["metric"].get("container")
        if usage > CPU_THRESHOLD:
            new_cpu = min(usage + CPU_INCREMENT, MAX_CPU_LIMIT)
            updates.append((container, new_cpu))
    return updates

def analyze_memory_usage(metrics):
    updates = []
    for metric in metrics:
        usage_bytes = float(metric["value"][1])
        usage_mi = usage_bytes / (1024 * 1024)
        if usage_mi > MEMORY_THRESHOLD * MAX_MEMORY_LIMIT:
            new_memory = min(usage_mi + MEMORY_INCREMENT, MAX_MEMORY_LIMIT)
            updates.append(("memory", int(new_memory)))
    return updates