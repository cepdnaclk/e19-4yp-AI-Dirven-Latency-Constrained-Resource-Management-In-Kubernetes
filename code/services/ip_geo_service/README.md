# 🌍 IP Geolocation API with Prometheus Metrics

This project is a lightweight microservice that provides geolocation data for a given IP address using a local IP2Location database. It exposes Prometheus-compatible metrics, including request latency and count, and is designed for Kubernetes deployment with CPU/memory resource monitoring.

---

## 📦 Features

- 🔎 Lookup geolocation for an IP address
- 📊 Prometheus metrics for:
  - Request latency
  - Request count
  - CPU usage, memory usage (via Kubernetes)
- ☸️ Kubernetes-ready with defined resource limits/requests
- 🐳 Dockerized for easy deployment

---

## 🚀 API Usage

### `GET /geoip?ip=<IP_ADDRESS>`

#### ✅ Example:
```json
GET /geoip?ip=8.8.8.8
```
#### 🔁 Response:
```json
{
  "ip": "8.8.8.8",
  "country": "US",
  "region": "California",
  "city": "Mountain View"
}
```

## 📈 Prometheus Metrics
Metrics are exposed at:
```cpp
http://<pod-ip>:8001/
```

### Metrics Provided:
* `request_latency_seconds{path="/geoip"}`
* `request_count_total{path="/geoip"}`

#### Additional (via Kubernetes Monitoring Tools):
* `container_cpu_usage_seconds_total`

* `container_memory_usage_bytes`

* `kube_pod_container_resource_requests_*`

* `kube_pod_container_resource_limits_*`

## 🛠️ Project Structure
```graphql
ip-geo-service/
├── app/
│   ├── main.py               # FastAPI app and routing
│   ├── geo_utils.py          # IP2Location-based geolocation logic
│   └── metrics.py            # Prometheus metrics middleware
├── Dockerfile
├── requirements.txt
├── IP2LOCATION-LITE-DB1.BIN  # Local geolocation DB (download separately)
├── k8s/
│   ├── deployment.yaml       # Kubernetes Deployment
│   └── service.yaml          # Kubernetes Service
└── README.md
```

## 🐳 Docker Build & Run
```bash
docker build -t ip-geo-service .
docker run -p 8000:8000 -p 8001:8001 ip-geo-service
```

## ☸️ Kubernetes Deployment

### 1. Apply the Deployment and Service:
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```
### 2. Access via NodePort, Ingress, or use port-forward:
```bash
kubectl port-forward svc/ip-geo-service 8080:80
```
Then access:
* API: `http://localhost:8080/geoip?ip=8.8.8.8`
* Metrics: `http://localhost:8080/metrics` (mapped to port 8001 internally)

## 📥 Get the IP2Location DB
1. Go to: https://lite.ip2location.com/database/ip-country-region-city

2. Download the BIN version (e.g., IP2LOCATION-LITE-DB1.BIN)

3. Place it in the root of the project.

## 📊 Prometheus Scrape Config
Add this job to the Prometheus config:
```yaml
- job_name: 'ip-geo-service'
  static_configs:
    - targets: ['ip-geo-service:8001']
```

## 📄 License
This project uses the free IP2Location LITE database under its respective license. For commercial use, refer to the official `IP2Location` licensing terms.

---