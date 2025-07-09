from locust import HttpUser, task, constant, LoadTestShape
import random

# Define Locust User behavior
class PasswordUser(HttpUser):
    wait_time = constant(1)

    @task
    def get_random_password(self):
        length = random.randint(8, 24)
        self.client.get(f"/password?length={length}")

# Define Load Shape
class StepLoadShape(LoadTestShape):
    """
    Load pattern:
    - 5 users for first 30 mins
    - Increase by 20 users every 30 mins
    - Cap at 1000 users
    """
    step_time = 1800  # 30 minutes
    step_users = 20
    initial_users = 5
    ramp_start_time = 1800  # start ramping after 30 mins
    max_users = 1000

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.ramp_start_time:
            return self.initial_users, self.initial_users

        steps = (run_time - self.ramp_start_time) // self.step_time
        users = self.initial_users + steps * self.step_users
        users = min(users, self.max_users)

        return users, users
