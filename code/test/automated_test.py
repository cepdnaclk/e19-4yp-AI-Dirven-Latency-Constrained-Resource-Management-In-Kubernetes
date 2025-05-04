import subprocess
import time
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

SCRIPT_DURATION = 3630
LOGS_DIR = "logs"


def find_files(root_dirs=["client_1", "client_2"], file_extension=".sh"):
    files = []
    for root_dir in root_dirs:
        for dirpath, _, filenames in os.walk(root_dir):
            for file in filenames:
                if file.endswith(file_extension):
                    files.append(os.path.join(dirpath, file))
    return files


def get_log_file_path(script_path):
    rel_path = os.path.relpath(script_path, ".").replace("/", "_")
    log_filename = f"{rel_path}.log"
    return os.path.join(LOGS_DIR, log_filename)


def get_jmx_files(root_dirs=["client_1", "client_2"]):
    return find_files(root_dirs, ".jmx")


def run_script_continuously(script_path, duration, jmx_file):
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file_path = get_log_file_path(script_path)

    script_dir = os.path.dirname(script_path)

    # Print the full path of the script for debugging
    print(f"Attempting to run script: {os.path.abspath(script_path)}")

    end_time = datetime.now() + timedelta(seconds=duration)
    with open(log_file_path, "a") as log_file:
        session_header = f"\n{'=' * 20} NEW SESSION [{datetime.now()}] {script_path} {'=' * 20}\n"
        log_file.write(session_header)
        log_file.flush()

        while datetime.now() < end_time:
            log_file.write(f"[{datetime.now()}] Starting {script_path} with JMX {jmx_file}\n")
            log_file.flush()

            # Change working directory to where the script is located
            process = subprocess.Popen(
                ["bash", script_path],
                stdout=log_file,
                stderr=log_file,
                cwd=os.path.abspath(script_path)  # Set the working directory to the directory of the script
            )
            while process.poll() is None and datetime.now() < end_time:
                time.sleep(5)

            log_file.write(f"[{datetime.now()}] Script ended or killed\n")
            log_file.flush()
            if datetime.now() < end_time:
                log_file.write(f"[{datetime.now()}] Restarting {script_path}\n")
                log_file.flush()



def main():
    print("Starting script execution...")
    print("Current working directory:", os.getcwd())  # <-- Add this

    sh_files = find_files(file_extension=".sh")
    jmx_files = get_jmx_files()

    if not sh_files:
        print("No .sh files found.")
        return

    if not jmx_files:
        print("No .jmx files found.")
        return

    print(f"Found {len(sh_files)} .sh files.")
    print(f"Found {len(jmx_files)} .jmx files.")

    with ThreadPoolExecutor(max_workers=len(sh_files)) as executor:
        for script in sh_files:
            jmx_file = jmx_files[0]
            executor.submit(run_script_continuously, script, SCRIPT_DURATION, jmx_file)



if __name__ == "__main__":
    main()
