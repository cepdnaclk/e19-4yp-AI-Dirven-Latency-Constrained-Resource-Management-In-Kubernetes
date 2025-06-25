import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time

JMETER_PATH = "jmeter"  # Update if jmeter is not in PATH
LOGS_DIR = "logs"
CLIENT_DIRS = ["client_1", "client_2"]


def find_jmx_files():
    jmx_files = []
    for client_dir in CLIENT_DIRS:
        for root, _, files in os.walk(client_dir):
            for file in files:
                if file.endswith(".jmx"):
                    jmx_files.append(os.path.join(root, file))
    return jmx_files


def run_jmx_test(jmx_path):
    jmx_abs_path = os.path.abspath(jmx_path)
    jmx_dir = os.path.dirname(jmx_abs_path)
    jmx_filename = os.path.basename(jmx_path).replace(".jmx", "")

    # Extract client and service names
    client_name = os.path.normpath(jmx_path).split(os.sep)[0].replace("_", "")
    service_name = "service1" if "service-1" in jmx_filename else "service2"

    while True:
        # Create a unique timestamped report directory
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_report_dir = os.path.abspath("generated_reports")
        os.makedirs(base_report_dir, exist_ok=True)

        report_dir = os.path.join(base_report_dir, f"{client_name}_{service_name}_report_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)

        results_path = os.path.join(report_dir, f"{jmx_filename}_results.csv")

        # Create log file for this run
        os.makedirs("logs", exist_ok=True)
        log_path = os.path.join("logs", f"{client_name}_{service_name}.log")

        session_header = f"\n{'=' * 10} NEW SESSION [{datetime.now()}] {jmx_filename} {'=' * 10}\n"

        with open(log_path, "a") as log_file:
            log_file.write(session_header)
            log_file.flush()

            print(f"[{datetime.now()}] Running: {jmx_path}")
            process = subprocess.Popen(
                [
                    JMETER_PATH, "-n",
                    "-t", jmx_abs_path,
                    "-l", results_path
                    # "-e", "-o", report_dir
                ],
                stdout=log_file,
                stderr=log_file,
                cwd=jmx_dir
            )
            process.wait()

            log_file.write(f"[{datetime.now()}] Finished with exit code {process.returncode}\n")
            log_file.flush()

            print(f"Test completed. Results saved to {results_path}")
            # print(f"Test completed. Results saved to {results_path} and HTML report generated in {report_dir}/")

        time.sleep(5)



def main():
    jmx_files = find_jmx_files()

    if not jmx_files:
        print("No JMX files found.")
        return

    print(f"Found {len(jmx_files)} JMX files. Executing in parallel...")

    with ThreadPoolExecutor(max_workers=len(jmx_files)) as executor:
        for jmx_file in jmx_files:
            executor.submit(run_jmx_test, jmx_file)


if __name__ == "__main__":
    main()
