SERVICES = [
    {
        "name": "service-1-deployment",
        "container": "service-1-container",
        "namespace": "default"
    },
    {
        "name": "service-2-deployment",
        "container": "service-2-container",
        "namespace": "default"
    }
]

CPU_THRESHOLD = 0.8
CPU_INCREMENT = 0.1
MAX_CPU_LIMIT = 1.0
PROMETHEUS_URL = "http://localhost:9090"
