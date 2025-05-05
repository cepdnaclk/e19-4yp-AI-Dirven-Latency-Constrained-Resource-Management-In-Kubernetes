import time
import json
import os
from .config import *

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
        elif usage < CPU_THRESHOLD - 0.2:
            target_cpu = max(usage - CPU_DECREMENT, MIN_CPU_LIMIT)

        if target_cpu:
            updates.append((container, round(target_cpu, 2)))
    return updates

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
        elif usage_mi < MEMORY_THRESHOLD * MIN_MEMORY_LIMIT:
            target_mem = max(usage_mi - MEMORY_DECREMENT, MIN_MEMORY_LIMIT)

        if target_mem:
            updates.append((container, int(target_mem)))
    return updates

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

