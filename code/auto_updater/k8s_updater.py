from kubernetes import client, config

def update_resources(container, cpu=None, memory=None):
    config.load_kube_config()
    api = client.CoreV1Api()

    # This part assumes container name equals pod label name
    pods = api.list_pod_for_all_namespaces(label_selector=f"app={container}").items
    for pod in pods:
        name = pod.metadata.name
        namespace = pod.metadata.namespace

        resources = pod.spec.containers[0].resources
        limits = resources.limits or {}
        requests = resources.requests or {}

        update = False
        if cpu:
            current_cpu = requests.get("cpu", "0")
            if str(cpu) != current_cpu:
                requests["cpu"] = str(cpu)
                limits["cpu"] = str(cpu)
                update = True
        if memory:
            mem_str = f"{memory}Mi"
            current_mem = requests.get("memory", "0")
            if mem_str != current_mem:
                requests["memory"] = mem_str
                limits["memory"] = mem_str
                update = True

        if update:
            patch = {"spec": {"containers": [{"name": container, "resources": {"limits": limits, "requests": requests}}]}}
            api.patch_namespaced_pod(name, namespace, patch)
