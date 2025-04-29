from .config import (
    CPU_THRESHOLD,
    CPU_DOWNSCALE_THRESHOLD,
    CPU_INCREMENT,
    CPU_DECREMENT,
    MAX_CPU_LIMIT,
    MIN_CPU_LIMIT,
    MEMORY_THRESHOLD,
    MEMORY_DOWNSCALE_THRESHOLD,
    MEMORY_INCREMENT,
    MEMORY_DECREMENT,
    MAX_MEMORY_LIMIT,
    MIN_MEMORY_LIMIT
)

def analyze_cpu_usage(cpu_metrics):
    updates = []
    for metric in cpu_metrics:
        usage = float(metric["value"][1])
        container = metric["metric"].get("container")

        if usage > CPU_THRESHOLD:
            new_cpu = min(usage + CPU_INCREMENT, MAX_CPU_LIMIT)
            updates.append((container, round(new_cpu, 1)))
        elif usage < CPU_DOWNSCALE_THRESHOLD:
            new_cpu = max(usage - CPU_DECREMENT, MIN_CPU_LIMIT)
            updates.append((container, round(new_cpu, 1)))

    return updates


def analyze_memory_usage(metrics):
    updates = []
    for metric in metrics:
        usage_bytes = float(metric["value"][1])
        usage_mi = usage_bytes / (1024 * 1024)
        container = metric["metric"].get("container")

        if usage_mi > MEMORY_THRESHOLD * MAX_MEMORY_LIMIT:
            new_memory = min(usage_mi + MEMORY_INCREMENT, MAX_MEMORY_LIMIT)
            updates.append((container, int(new_memory)))
        elif usage_mi < MEMORY_DOWNSCALE_THRESHOLD * MAX_MEMORY_LIMIT:
            new_memory = max(usage_mi - MEMORY_DECREMENT, MIN_MEMORY_LIMIT)
            updates.append((container, int(new_memory)))

    return updates
