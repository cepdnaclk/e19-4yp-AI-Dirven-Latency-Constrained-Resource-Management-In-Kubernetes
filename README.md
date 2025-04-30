## Understanding the Problem Statement: Kubernetes Resource Auto-Updater with Latency Monitoring

### Overview
This setup is designed to analyze latency increments during dynamic resource updates (CPU/Memory) in a Kubernetes environment. It uses Apache JMeter to simulate traffic and measure latency, and Prometheus to collect metrics. An Auto Updater module adjusts resource allocations based on historical performance data.

### Architecture
![image](https://github.com/user-attachments/assets/e0fb570e-c350-4b41-9583-264b78fd6ebe)

#### Components
* Clients (Local Environment):
Use Apache JMeter to generate HTTP traffic towards services in the Kubernetes cluster. Latency logs are collected and stored for analysis.

* Apache JMeter:
Load testing tool used to simulate concurrent requests and log latency data for each request.

* Kubernetes Cluster:

  - Services (Service 1, Service 2): Sample applications that process HTTP requests.

  - Prometheus: Collects performance metrics (CPU, memory, etc.) from services.

  - Auto Updater: Uses 1 hour of historical data from Prometheus to compute new resource requirements.

  - Kubernetes API: Applies resource updates (requests/limits) sent by the Auto Updater.

 ### Objectives
* Measure latency impact during live resource updates.

* Evaluate whether resource adjustments introduce unacceptable latency spikes.

* Optimize auto-scaling strategies (vertical scaling focus).

### Prerequisites
* Kubernetes Cluster (Minikube, Kind, GKE, etc.)

* Apache JMeter

* Prometheus installed in the cluster

* Python or Go-based Auto Updater (custom module)

* Grafana (optional, for metric visualization)

### Setup Steps
1. Deploy Prometheus
  * Follow the Prometheus Helm chart to install Prometheus in your cluster.
2. Deploy Sample Services
  * Deploy at least two services that handle HTTP requests.
3. Configure JMeter
  * Create a test plan to send concurrent HTTP requests to the services.
  * Enable latency logging and store results locally.
4. Run Auto Updater
  * Continuously fetch metrics from Prometheus.
  * Based on predefined rules or models, send resource update requests to the Kubernetes API.
