from locust import HttpUser, task, constant, constant, LoadTestShape
import random
import string
import json
import os
import time

class HashUser(HttpUser):
    wait_time = constant(1)  # 1 second delay between tasks for realism

    @task
    def generate_sha256(self):
        random_input = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        self.client.post(
            "/hash/sha256",
            data=random_input,  # send as plain text
            headers={"Content-Type": "text/plain"}  # correct content type
        )

class StepLoadShape(LoadTestShape):
    """
    Step load pattern:
    - First 30 mins constant 5 users
    - Every 30 mins, ramp up by 20 users
    - Max users capped at 1000
    """
    step_time = 1800          # Duration of each step (30 minutes)
    step_users = 20           # Users added at each step
    initial_users = 5         # Start with 5 users
    ramp_start_time = 1800    # Begin ramping after 30 mins
    max_users = 1000          # Cap to avoid overload

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.ramp_start_time:
            return (self.initial_users, self.initial_users)

        ramp_duration = run_time - self.ramp_start_time
        steps = ramp_duration // self.step_time
        users = self.initial_users + steps * self.step_users

        if users > self.max_users:
            users = self.max_users

        return (int(users), int(users))
    
# Function to run Locust from inside the script
def run_locust_command(user_count=20):
    target_host = "http://192.168.49.2:32567"

    command = (
        f"locust -f locustfile_runner.py --headless "
        f"-u {user_count} -r 5 --run-time 30s --host={target_host}"
    )
    print(f"Running: {command}")
    os.system(command)

if __name__ == "__main__":
    # Run the test repeatedly every 30 seconds
    while True:
        run_locust_command(user_count=20)
        print("Sleeping before next round...\n")
        time.sleep(30)
