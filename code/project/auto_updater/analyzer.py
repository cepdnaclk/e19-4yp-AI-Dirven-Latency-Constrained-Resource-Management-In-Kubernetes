import time
import json
import os
from .config import *

# Analyze CPU usage and suggest updates
def analyze_cpu(cpu_metrics):
    updates = []
    for metric in cpu_metrics:
        usage = float(metric['value'][1])
        container = metric['metric'].get('container')
        if not container:
            continue

        target_cpu = None
        if usage > CPU_THRESHOLD:
            target_cpu = min(usage + CPU_INCREMENT, MAX_CPU_LIMIT)
        elif usage < CPU_DOWNSCALE_THRESHOLD:
            target_cpu = max(usage - CPU_DECREMENT, MIN_CPU_LIMIT)

        if target_cpu:
            updates.append((container, round(target_cpu, 2)))
    return updates

# Analyze memory usage and suggest updates
def analyze_memory(mem_metrics):
    updates = []
    for metric in mem_metrics:
        usage_bytes = float(metric["value"][1])
        usage_mi = usage_bytes / (1024 * 1024)
        container = metric['metric'].get('container')
        if not container:
            continue

        target_mem = None
        if usage_mi > MEMORY_THRESHOLD * MAX_MEMORY_LIMIT:
            target_mem = min(usage_mi + MEMORY_INCREMENT, MAX_MEMORY_LIMIT)
        elif usage_mi < MEMORY_DOWNSCALE_THRESHOLD * MIN_MEMORY_LIMIT:
            target_mem = max(usage_mi - MEMORY_DECREMENT, MIN_MEMORY_LIMIT)

        if target_mem:
            updates.append((container, int(target_mem)))
    return updates

# Prevent frequent updates with a cooldown period
def should_apply_update(container):
    now = time.time()
    state_file = os.path.join(os.path.dirname(__file__), 'cooldown_state.json')
    state = {}

    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            state = json.load(f)

    last_time = state.get(container, 0)
    if now - last_time > COOLDOWN_PERIOD_MINUTES * 60:
        state[container] = now
        with open(state_file, 'w') as f:
            json.dump(state, f)
        return True
    return False

# Combine CPU and memory updates into one dictionary
def get_combined_resource_updates(cpu_metrics, memory_metrics):
    cpu_updates = analyze_cpu(cpu_metrics)
    memory_updates = analyze_memory(memory_metrics)

    updates = {}
    for container, cpu in cpu_updates:
        updates[container] = {"cpu": cpu}
    for container, mem in memory_updates:
        if container in updates:
            updates[container]["memory"] = mem
        else:
            updates[container] = {"memory": mem}
    return updates

# Track allocated resources over time
resource_tracking = {}

def track_resource_allocation(container, cpu, memory):
    if container not in resource_tracking:
        resource_tracking[container] = []
    resource_tracking[container].append({
        "timestamp": time.time(),
        "cpu": cpu,
        "memory": memory
    })

# Periodically reduce resources for a container
def reduce_resources_periodically(container, interval=600, steps=3):
    if container not in resource_tracking:
        print(f"No tracking data for {container}")
        return

    for i in range(steps):
        time.sleep(interval)
        last_alloc = resource_tracking[container][-1]
        new_cpu = max(last_alloc["cpu"] - CPU_DECREMENT, MIN_CPU_LIMIT)
        new_mem = max(last_alloc["memory"] - MEMORY_DECREMENT, MIN_MEMORY_LIMIT)
        apply_resource_reduction(container, new_cpu, new_mem)
        track_resource_allocation(container, new_cpu, new_mem)

# Dummy stop flag; replace with better coordination if needed
stop_reduction = {}

def stop_resource_reduction(container):
    stop_reduction[container] = True

# Hook for applying reduction (can integrate with k8s_updater)
def apply_resource_reduction(container, cpu, memory):
    print(f"Applying reduction for {container}: CPU={cpu}, Memory={memory}Mi")
    # This is a placeholder. You should call update_resources() here if needed.
