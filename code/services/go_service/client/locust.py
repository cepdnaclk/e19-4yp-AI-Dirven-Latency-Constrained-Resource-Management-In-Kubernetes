from locust import HttpUser, task, between, LoadTestShape
import random

class EchoUser(HttpUser):
    wait_time = between(0.5, 1.5)  # Simulate realistic pacing

    @task
    def echo_number(self):
        number = random.randint(1, 1000)
        self.client.get(f"/echoNumber?number={number}")

# Define custom load shape
class StepLoadShape(LoadTestShape):
    """
    - Run at a constant user count for 30 mins (1800 seconds)
    - Then gradually ramp up every 2 mins
    - After crash, you can restart and reduce user count manually
    """

    step_time = 120  # seconds between steps after initial phase
    step_users = 20  # increase this many users each step
    initial_users = 50  # constant user count for the first 30 mins
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
