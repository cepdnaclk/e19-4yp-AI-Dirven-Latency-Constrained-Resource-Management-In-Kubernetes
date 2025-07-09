from locust import HttpUser, task, constant, LoadTestShape
import random
import string

class HashUser(HttpUser):
    wait_time = constant(1)  # 1 second delay between tasks

    @task
    def generate_sha256(self):
        random_input = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        with self.client.post(
            "/hash/sha256",
            data=random_input,
            headers={"Content-Type": "text/plain"},
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                response.success()

class StepLoadShape(LoadTestShape):
    """
    Load pattern:
    - First 30 minutes: 5 users
    - Then increase by 20 users every 30 minutes
    - Cap at 1000 users
    """
    step_time = 1800           # 30 minutes per step
    step_users = 20
    initial_users = 5
    ramp_start_time = 1800     # start ramping after 30 min
    max_users = 1000

    def tick(self):
        run_time = self.get_run_time()

        if run_time < self.ramp_start_time:
            return (self.initial_users, self.initial_users)

        steps = (run_time - self.ramp_start_time) // self.step_time
        users = self.initial_users + steps * self.step_users
        if users > self.max_users:
            users = self.max_users

        return (int(users), int(users))
