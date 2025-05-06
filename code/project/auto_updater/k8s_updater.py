import subprocess
import logging
logger = logging.getLogger("auto_updater")

def update_resources(deployment, container, namespace, cpu=None, memory=None):
    patch = {"spec": {"template": {"spec": {"containers": [{"name": container}]}}}}
    container_patch = patch["spec"]["template"]["spec"]["containers"][0]

    if cpu:
        container_patch.setdefault("resources", {}).setdefault("limits", {})["cpu"] = cpu
        container_patch["resources"].setdefault("requests", {})["cpu"] = cpu
    if memory:
        container_patch.setdefault("resources", {}).setdefault("limits", {})["memory"] = f"{memory}Mi"
        container_patch["resources"].setdefault("requests", {})["memory"] = f"{memory}Mi"

    cmd = [
        "kubectl", "patch", "deployment", deployment,
        "-n", namespace,
        "-p", str(patch),
        "--type", "merge"
    ]

    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Patched {deployment} with CPU: {cpu}, Memory: {memory}Mi")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to update deployment {deployment}: {e}")