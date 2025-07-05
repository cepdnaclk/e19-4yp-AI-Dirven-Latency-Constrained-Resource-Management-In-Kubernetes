from locust import HttpUser, task, between
from random import randint
import time

class HashGeneratorUser(HttpUser):
    # Simulate a wait time between 1 and 5 seconds between tasks
    wait_time = between(1, 5)

    @task
    def send_sha256_request(self):
        # Adjust the data payload to match the endpoint's expected input
        self.client.post("/hash/sha256", data="ABCDEEF123", headers={"Content-Type": "text/plain"})

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
        command = f"locust -f locustfile.py --headless -u {user_count} -r 5 --run-time 30s --host=http://192.168.49.2:32567"
        os.system(command)  # Execute the command to start the test
        time.sleep(30)  # Adjust the interval of changing users (30 seconds)

# Start the continuous running function
if __name__ == "__main__":
    import os
    run_locust_continuously()
