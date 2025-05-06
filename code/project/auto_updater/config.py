SERVICES = [
    {
        "name": "service-1-deployment",
        "container": "service-1-container",
        "pod": "service-1-deployment-[a-z0-9]+-[a-z0-9]+",
        "namespace": "default"
    },
    {
        "name": "service-2-deployment",
        "container": "service-2-container",
        "pod": "service-2-deployment-[a-z0-9]+-[a-z0-9]+",
        "namespace": "default"
    }
]

CPU_THRESHOLD = 0.8
CPU_INCREMENT = 0.1
MAX_CPU_LIMIT = 1.0

CPU_DOWNSCALE_THRESHOLD = 0.3
CPU_DECREMENT = 0.1
MIN_CPU_LIMIT = 0.1

PROMETHEUS_URL = "http://localhost:9090"

MEMORY_THRESHOLD = 0.8
MEMORY_INCREMENT = 128  # in Mi
MAX_MEMORY_LIMIT = 2048  # in Mi (2Gi)

MEMORY_DOWNSCALE_THRESHOLD = 0.3
MEMORY_DECREMENT = 128  # Mi
MIN_MEMORY_LIMIT = 256  # Mi

# Resource Reduction Parameters
CPU_REDUCTION_RATE = 0.05  
MEMORY_REDUCTION_RATE = 32  
MIN_CPU_AFTER_REDUCTION = 0.2  
MIN_MEMORY_AFTER_REDUCTION = 256