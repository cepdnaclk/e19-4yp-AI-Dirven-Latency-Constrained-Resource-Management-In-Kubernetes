import os
import json
import time
from kubernetes import client, config
from auto_updater.config import SERVICES

# Load kube config
config.load_incluster_config()

apps_v1 = client.AppsV1Api()

# Cool-down state tracker
COOLDOWN_FILE = "cooldown_state.json"
COOLDOWN_INTERVAL_SECONDS = 30 * 60  # 30 minutes

def load_cooldown_state():
    if os.path.exists(COOLDOWN_FILE):
        with open(COOLDOWN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cooldown_state(state):
    with open(COOLDOWN_FILE, "w") as f:
        json.dump(state, f)

def is_in_cooldown(service_key, state):
    last_update = state.get(service_key, 0)
    return (time.time() - last_update) < COOLDOWN_INTERVAL_SECONDS

def update_cooldown(service_key, state):
    state[service_key] = time.time()
    save_cooldown_state(state)

def get_current_resources(deployment_name, namespace, container_name):
    deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)
    for container in deployment.spec.template.spec.containers:
        if container.name == container_name:
            cpu = container.resources.requests.get('cpu', '0')
            memory = container.resources.requests.get('memory', '0')
            return cpu, memory
    return '0', '0'

def update_resources(deployment_name, container_name, namespace, new_cpu=None, new_memory=None):
    state = load_cooldown_state()
    service_key = f"{namespace}-{deployment_name}-{container_name}"

    if is_in_cooldown(service_key, state):
        print(f"[COOLDOWN] Skipping update for {service_key}")
        return

    current_cpu, current_memory = get_current_resources(deployment_name, namespace, container_name)

    # Normalize values to avoid unnecessary patches
    def normalize_cpu(cpu):
        return f"{float(cpu):.1f}"

    def normalize_mem(mem):
        return f"{int(mem)}Mi"

    patch_required = False
    patch_resources = {"requests": {}, "limits": {}}

    if new_cpu:
        new_cpu_str = normalize_cpu(new_cpu)
        if normalize_cpu(current_cpu.replace("m", "")) != new_cpu_str:
            patch_required = True
            patch_resources["requests"]["cpu"] = new_cpu_str
            patch_resources["limits"]["cpu"] = new_cpu_str

    if new_memory:
        new_memory_str = normalize_mem(new_memory)
        if current_memory != new_memory_str:
            patch_required = True
            patch_resources["requests"]["memory"] = new_memory_str
            patch_resources["limits"]["memory"] = new_memory_str

    if not patch_required:
        print(f"[INFO] No update needed for {service_key}. Skipping.")
        return

    patch_body = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": container_name,
                            "resources": patch_resources
                        }
                    ]
                }
            }
        }
    }

    try:
        apps_v1.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=patch_body
        )
        update_cooldown(service_key, state)
        print(f"[SUCCESS] Updated resources for {service_key}")
    except Exception as e:
        print(f"[ERROR] Failed to update resources for {service_key}: {e}")
