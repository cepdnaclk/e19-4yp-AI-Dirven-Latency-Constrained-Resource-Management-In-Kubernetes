from locust import HttpUser, task, constant, LoadTestShape
import random
import os
import time

class PrimeUser(HttpUser):
    wait_time = constant(1)  # Simulate realistic pacing

    @task
    def check_prime(self):
        number = 49 #random.randint(1, 1000)
        self.client.get(f"/isPrime?number={number}")

# Define custom load shape
class StepLoadShape(LoadTestShape):
    """
    - Run at a constant user count for 30 mins (1800 seconds)
    - Then gradually ramp up every 30 mins
    - After crash, you can restart and reduce user count manually
    """

    step_time = 1800  # seconds between steps after initial phase
    step_users = 20  # increase this many users each step
    initial_users = 5  # constant user count for the first 30 mins
    ramp_start_time = 1800  # after 30 mins, start ramping
    max_users = 1000  # upper bound before crash

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.ramp_start_time:
            return (self.initial_users, self.initial_users)

        # ramp phase
        ramp_duration = run_time - self.ramp_start_time
        steps = ramp_duration // self.step_time
        users = self.initial_users + steps * self.step_users

        if users > self.max_users:
            users = self.max_users

        return (int(users), int(users))
    
# Function to run Locust from inside the script
def run_locust_command(user_count=20):
    target_host = "http://192.168.49.2:31662"

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
    
# nohup locust -f locust.py --host=http://localhost:3001 --headless > locust.log 2>&1 &
