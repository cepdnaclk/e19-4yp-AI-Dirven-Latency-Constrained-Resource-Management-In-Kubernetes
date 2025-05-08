from locust import HttpUser, task, between, between
from random import randint
import time

class HashGeneratorUser(HttpUser):
    # Simulate a wait time between 1 and 5 seconds between tasks
    wait_time = between(1, 5)

    @task
    def send_sha256_request(self):
        self.client.post("/hash/sha256", json={"data": "test"})

    def on_start(self):
        self.client.verify = False
        self.client.get("/")

    def run(self):
        # Continuously adjust user count between 10 and 20 every 30 seconds
        while True:
            user_count = randint(10, 20)
            print(f"Starting test with {user_count} users")
            self.environment.runner.start(user_count, spawn_rate=5)
            time.sleep(30)  # Adjust the interval of changing users
