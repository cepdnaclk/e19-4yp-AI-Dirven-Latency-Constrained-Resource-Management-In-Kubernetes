# client.py
import requests
import time
import random

# Target URL
URL_TEMPLATE = "http://localhost:8000/geo/{}"

# Some example IPs for testing
IP_POOL = [
    "8.8.8.8", "1.1.1.1", "123.45.67.89", "216.58.217.206", "142.250.180.14"
]

# Delay between requests (in seconds)
REQUEST_INTERVAL = 1  # 1 request per second

def generate_workload():
    while True:
        ip = random.choice(IP_POOL)
        url = URL_TEMPLATE.format(ip)

        start_time = time.time()
        try:
            response = requests.get(url)
            latency = time.time() - start_time
            print(f"[{time.strftime('%X')}] Requested {ip} - Status: {response.status_code}, Latency: {latency:.3f}s")
        except Exception as e:
            print(f"Request failed: {e}")

        time.sleep(REQUEST_INTERVAL)

if __name__ == "__main__":
    print("Starting workload generator...")
    generate_workload()
