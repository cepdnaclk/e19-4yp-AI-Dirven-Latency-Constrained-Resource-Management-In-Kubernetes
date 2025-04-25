def update_cpu_resources(deployment, container, namespace, cpu_value):
    body = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": container,
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
    response = apps_v1.patch_namespaced_deployment(deployment, namespace, body)
    return response
