from locust import HttpUser, task, constant, LoadTestShape
import random
import os
import time

# Define Locust User behavior
class PasswordUser(HttpUser):
    wait_time = constant(1)

    @task
    @task
    def check_prime(self):
        number = 40 #random.randint(1, 1000)
        with self.client.get(f"/echoNumber?number={number}", catch_response=True) as response:
            if response.status_code != 200:
                print(f"Failed with status {response.status_code}: {response.text}")
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                print(f"Success: {response.text}")
                response.success()

# Define Load Shape
class StepLoadShape(LoadTestShape):
    """
    Load pattern:
    - 5 users for first 30 mins
    - Increase by 20 users every 30 mins
    - Cap at 1000 users
    """
    step_time = 1800
    step_users = 20
    initial_users = 5
    ramp_start_time = 1800
    max_users = 1000

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.ramp_start_time:
            return (self.initial_users, self.initial_users)
        steps = (run_time - self.ramp_start_time) // self.step_time
        users = self.initial_users + steps * self.step_users
        return (int(min(users, self.max_users)), int(min(users, self.max_users)))

# Function to run Locust from inside the script
def run_locust_command(user_count=20):
    # Update host if needed
    target_host = "http://192.168.49.2:32360"

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
