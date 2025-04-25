from kubernetes import client, config

config.load_kube_config()
apps_v1 = client.AppsV1Api()

def update_resources(deployment, container, namespace, cpu=None, memory=None):
    resources = {"limits": {}, "requests": {}}

    if cpu:
        cpu_str = f"{cpu}"
        resources["limits"]["cpu"] = cpu_str
        resources["requests"]["cpu"] = cpu_str

    if memory:
        mem_str = f"{memory}Mi"
        resources["limits"]["memory"] = mem_str
        resources["requests"]["memory"] = mem_str

    patch_body = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {"name": container, "resources": resources}
                    ]
                }
            }
        }
    }

    return apps_v1.patch_namespaced_deployment(
        name=deployment,
        namespace=namespace,
        body=patch_body
    )
