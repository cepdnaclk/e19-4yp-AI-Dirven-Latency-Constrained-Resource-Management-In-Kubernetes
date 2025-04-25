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