from locust import HttpUser, task, between
from random import randint, choice
import time
import os

class PasswordGeneratorUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def check_prime(self):
        number = randint(30, 35)  # Moderately large to cause some CPU load
        self.client.get(f"/color/n?n={number}")

    def on_stop(self):
        pass

def run_locust_fluctuating_workload():
    """Run Locust with fluctuating users via random walk logic."""
    min_users = 15
    max_users = 50
    user_count = 30  # Start at mid-point
    user_step = 1

    while True:
        # Random walk: increase or decrease users within bounds
        user_count += choice([-user_step, user_step])
        user_count = max(min_users, min(max_users, user_count))

        #print(f"[INFO] Running test with {user_count} users")

        command = (
            f"locust -f locustfile.py --headless -u {user_count} -r 3 "
            f"--run-time 60s --host=http://192.168.49.104:3015"
        )
        os.system(command)

        sleep_interval = randint(15, 30)  # Cool-down to prevent overload
        print(f"[INFO] Sleeping for {sleep_interval} seconds before next run...")
        #time.sleep(sleep_interval)

if __name__ == "__main__":
    run_locust_fluctuating_workload()
