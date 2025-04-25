# Auto Updater for Kubernetes Resources

This tool queries Prometheus for resource usage metrics and applies CPU updates to Kubernetes deployments using the Kubernetes API.

## Setup
1. Install dependencies:
```
pip install -r requirements.txt
```
2. Set your Kubernetes context.
3. Configure your deployment details in `config.py`.

## Run
Double-click `run.bat` or use:
```
python auto_updater/main.py
```