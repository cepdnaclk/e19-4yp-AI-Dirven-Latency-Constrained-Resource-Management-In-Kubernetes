PROMETHEUS_URL = "http://localhost:9090"
PROMETHEUS_QUERY_CPU = 'rate(container_cpu_usage_seconds_total{container!="POD"}[5m])'
NAMESPACE = "default"
DEPLOYMENT_NAME = "ourdeployment"
CONTAINER_NAME = "our-container"
CPU_THRESHOLD = 0.8
CPU_INCREMENT = 0.1  # in cores
MAX_CPU_LIMIT = 1.0