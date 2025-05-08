# Sentiment Analysis Service

A simple FastAPI-based microservice that performs sentiment analysis on a given text using TextBlob. This service also exposes Prometheus metrics for resource usage and request latency.

---

## 🧠 Features

- REST API to analyze sentiment (`positive`, `negative`, `neutral`)
- Prometheus-compatible metrics:
  - Request count and latency
  - Container CPU/memory usage
  - Container CPU/memory requests and limits

---

## 📁 Project Structure

```bash
sentiment_service/
├── app/
│ ├── init.py
│ ├── main.py # FastAPI app
│ ├── sentiment.py # Sentiment logic using TextBlob
│ ├── metrics.py # Prometheus metrics setup
├── requirements.txt # Python dependencies
├── Dockerfile # Docker image definition
├── .dockerignore
├── kubernetes/
│ ├── deployment.yaml # Kubernetes deployment definition
│ └── service.yaml # Kubernetes service definition
```

---

## 🚀 API Usage

### `GET /sentiment?text=your_text_here`

**Example Request:**
```bash
curl "http://localhost:8000/sentiment?text=I love this project!"
```
**Response:**
```json
{
  "sentiment": "positive"
}
```

## 📊 Exposed Prometheus Metrics
Accessible at: `http://<pod_ip>:8001/metrics`

### Example Metrics:
* `request_count{path="/sentiment"}`

* `request_latency_seconds_bucket{path="/sentiment"}`

* `container_cpu_usage`

* `container_memory_usage`

* `container_cpu_request, container_cpu_limit`

* `container_memory_request, container_memory_limit`

## 🐳 Docker Instructions
### Build the Docker Image
```bash
docker build -t <your-dockerhub-username>/sentiment-service:latest .
```
### Push to Docker Hub
```bash
docker push <your-dockerhub-username>/sentiment-service:latest
```
## ☸️ Kubernetes Deployment
### Apply Deployment & Service
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```
The service is exposed with:
* `HTTP API`: Port `80`
* `Metrics`: Port `8001`

## 📦 Requirements
* Python 3.9+
* Docker
* Kubernetes cluster (Minikube, k3s, or cloud-based)
* Prometheus (for metrics scraping)