import subprocess
import time
import os
from datetime import datetime

# Function to run the JMeter command
def run_jmeter():
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create a unique file name using the timestamp
    results_filename = f"test_results/hash_gen_jmx_results_{timestamp}.csv"
    
    # JMeter command with the timestamped filename
    jmeter_command = f"jmeter -n -t test_plan.jmx -l {results_filename}"

    # Run the JMeter command using subprocess
    try:
        print(f"Running JMeter test and saving results to {results_filename}...")
        subprocess.run(jmeter_command, shell=True, check=True)
        print(f"JMeter test completed successfully! Results saved to {results_filename}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running JMeter test: {e}")

# Main loop to continuously run the JMeter test
def run_continuous_tests(interval=5):
    # Ensure the test_results directory exists
    os.makedirs("test_results", exist_ok=True)

    while True:
        run_jmeter()  # Run the JMeter command
        print(f"Waiting for {interval} seconds before running the test again.")
        time.sleep(interval)  # Wait for the specified interval (default: 1 hour)

if __name__ == "__main__":
    run_continuous_tests(interval=5)
