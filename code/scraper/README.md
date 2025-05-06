# Kubernetes Service Metrics Scraper

This script scrapes resource usage and request latency metrics from **Prometheus** for Java- and Go-based Kubernetes services. The data is continuously written to individual CSV files for each service, enabling offline analysis and model training for performance prediction or scaling decisions.

## 📋 Features

- Scrapes:

  - CPU and memory requests & limits
  - CPU and memory usage
  - Request latency

- Works with:

  - Java services (using Spring Boot metrics)
  - Go services (using custom Prometheus metrics)

- Runs **continuously** in parallel threads for each language category
- Outputs data to:

  ```
  service-1-deployment_dataset.csv
  service-2-deployment_dataset.csv
  ```

## 🛠️ Requirements

- Python 3.7+
- Prometheus running and accessible at: `http://localhost:9090`
- Metrics must be exposed and scraped by Prometheus using standard Kubernetes metric exporters.

Install dependencies (if not already installed):

```bash
pip install requests
```

## 🏃‍♂️ Running the Script

You can run the script in the background using `nohup` to ensure it keeps running even after the terminal is closed.

### Basic Run (foreground)

```bash
python3 prometheus_scraper.py
```

### Run in Background with `nohup`

```bash
nohup python3 prometheus_scraper.py > scraper.log 2>&1 &
```

- `> scraper.log` stores standard output in `scraper.log`.
- `2>&1` redirects error output to the same file.
- `&` runs the process in the background.

### To Check If It's Running

```bash
ps aux | grep prometheus_scraper.py
```

Or check the log file:

```bash
tail -f scraper.log
```

### To Stop the Script

Find the process ID (PID) and kill it:

```bash
ps aux | grep prometheus_scraper.py
kill <PID>
```

## 📁 Output Format

Each row in the output CSV looks like this:

| Timestamp | Service | CPU Request | Memory Request | CPU Limit | Memory Limit | Latency | CPU Usage | Memory Usage |
| --------- | ------- | ----------- | -------------- | --------- | ------------ | ------- | --------- | ------------ |

Example:

```
2025-05-06T14:33:21.345Z,service-1-deployment,0.5,536870912,1,1073741824,0.015,0.03,890000000
```
