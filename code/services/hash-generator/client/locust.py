from locust import HttpUser, task, between, constant, LoadTestShape
import random
import string
import json

class HashUser(HttpUser):
    wait_time = constant(1)  # 1 second delay between tasks for realism

    @task
    def generate_sha256(self):
        random_input = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        self.client.post(
            "/hash/sha256",
            data=json.dumps(random_input),
            headers={"Content-Type": "application/json"}
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
