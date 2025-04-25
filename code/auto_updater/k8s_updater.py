from kubernetes import client, config
from .config import NAMESPACE, DEPLOYMENT_NAME, CONTAINER_NAME

config.load_kube_config()

apps_v1 = client.AppsV1Api()

def update_cpu_resources(cpu_value):
    body = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": CONTAINER_NAME,
                            "resources": {
                                "limits": {"cpu": f"{cpu_value}"},
                                "requests": {"cpu": f"{cpu_value}"}
                            }
                        }
                    ]
                }
            }
        }
    }
    response = apps_v1.patch_namespaced_deployment(DEPLOYMENT_NAME, NAMESPACE, body)
    return response