from locust import HttpUser, task, constant, LoadTestShape
import random

class PrimeUser(HttpUser):
    wait_time = constant(1)  # Simulate realistic pacing

    @task
    def check_prime(self):
        number = 49  # or random.randint(1, 1000)
        self.client.get(f"/isPrime?number={number}")

class StepLoadShape(LoadTestShape):
    """
    Load pattern:
    - First 30 mins: 5 users
    - Then ramp up every 30 mins by 20 users
    - Cap at 1000 users
    """
    step_time = 1800           # every 30 minutes
    step_users = 20
    initial_users = 5
    ramp_start_time = 1800     # ramp starts after 30 mins
    max_users = 1000

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.ramp_start_time:
            return self.initial_users, self.initial_users

        steps = (run_time - self.ramp_start_time) // self.step_time
        users = self.initial_users + steps * self.step_users
        users = min(users, self.max_users)

        return int(users), int(users)
