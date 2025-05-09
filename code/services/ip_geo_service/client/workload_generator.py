import requests
import random
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Simulated real-world public IPs
COMMON_IPS = [
    "8.8.8.8", "1.1.1.1", "142.250.180.14", "216.58.217.206",
    "104.244.42.1", "151.101.1.69", "23.45.67.89", "198.35.26.96"
]

def fetch_ip(ip):
    try:
        start = time.time()
        res = requests.get(f"http://ip-geo-service/geo/{ip}", timeout=2)
        latency = time.time() - start
        print(f"[{ip}] {res.status_code} in {latency:.2f}s: {res.json()}")
    except Exception as e:
        print(f"[{ip}] ERROR: {e}")

def generate_workload():
    with ThreadPoolExecutor(max_workers=5) as executor:
        while True:
            batch_ips = random.choices(COMMON_IPS, k=random.randint(2, 5))
            executor.map(fetch_ip, batch_ips)
            time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    generate_workload()
