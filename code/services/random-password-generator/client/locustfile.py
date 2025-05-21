from locust import HttpUser, task, between
from random import randint
import time
import os

class PasswordGeneratorUser(HttpUser):
    # Simulate a wait time between 1 and 5 seconds between tasks
    wait_time = between(1, 5)

    @task
    def generate_random_password(self):
        # Random length between 8 and 20
        length = randint(12, 25)
        self.client.get(f"/password?length={length}")

    def on_stop(self):
        # Perform any cleanup if necessary
        pass

def run_locust_continuously():
    """Run Locust continuously with periodic user adjustments."""
    while True:
        # user_count = randint(10, 20)
        user_count = 20  # Random user count between 10 and 20
        print(f"Starting test with {user_count} users")

        # Start Locust in headless mode with the specified user count
        command = (
            f"locust -f locustfile.py --headless -u {user_count} -r 5 "
            f"--run-time 30s --host=http://192.168.49.103:3003"
        )
        os.system(command)  # Execute the command to start the test
        time.sleep(30)  # Adjust the interval for changing users

# Start the continuous running function
if __name__ == "__main__":
    run_locust_continuously()
