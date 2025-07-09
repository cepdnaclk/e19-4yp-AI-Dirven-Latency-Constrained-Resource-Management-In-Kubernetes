from locust import HttpUser, task, constant, LoadTestShape
import random

# Define Locust User behavior
class PasswordUser(HttpUser):
    wait_time = constant(1)

    @task
    def check_prime(self):
        number = 40  # fixed input for testing
        with self.client.get(f"/echoNumber?number={number}", catch_response=True) as response:
            if response.status_code != 200:
                print(f"Failed with status {response.status_code}: {response.text}")
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                print(f"Success: {response.text}")
                response.success()

# Load pattern class
class StepLoadShape(LoadTestShape):
    """
    Step load pattern:
    - First 30 mins: 5 users
    - Every 30 mins: add 20 more users
    - Cap at 1000 users
    """
    step_time = 1800  # 30 minutes per step
    step_users = 20
    initial_users = 5
    ramp_start_time = 1800  # after 30 mins
    max_users = 1000

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.ramp_start_time:
            return self.initial_users, self.initial_users

        steps = (run_time - self.ramp_start_time) // self.step_time
        users = self.initial_users + steps * self.step_users

        if users > self.max_users:
            users = self.max_users

        return int(users), int(users)
