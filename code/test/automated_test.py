import subprocess
import time
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

SCRIPT_DURATION = 3630
LOGS_DIR = "logs"

def find_shell_scripts(root_dirs=["client_1", "client_2"]):
    sh_files = []
    for root_dir in root_dirs:
        for dirpath, _, filenames in os.walk(root_dir):
            for file in filenames:
                if file.endswith(".sh"):
                    sh_files.append(os.path.join(dirpath, file))
    return sh_files

def get_log_file_path(script_path):
    rel_path = os.path.relpath(script_path, ".").replace("/", "_")
    log_filename = f"{rel_path}.log"
    return os.path.join(LOGS_DIR, log_filename)

def run_script_continuously(script_path, duration):
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file_path = get_log_file_path(script_path)

    end_time = datetime.now() + timedelta(seconds=duration)
    with open(log_file_path, "a") as log_file:
        session_header = f"\n{'='*20} NEW SESSION [{datetime.now()}] {script_path} {'='*20}\n"
        log_file.write(session_header)
        log_file.flush()

        while datetime.now() < end_time:
            log_file.write(f"[{datetime.now()}] Starting {script_path}\n")
            log_file.flush()
            process = subprocess.Popen(
                ["bash", script_path],
                stdout=log_file,
                stderr=log_file
            )
            while process.poll() is None and datetime.now() < end_time:
                time.sleep(5)

            log_file.write(f"[{datetime.now()}] Script ended or killed\n")
            log_file.flush()
            if datetime.now() < end_time:
                log_file.write(f"[{datetime.now()}] Restarting {script_path}\n")
                log_file.flush()

def main():
    sh_files = find_shell_scripts()
    if not sh_files:
        print("No .sh files found.")
        return

    # print(f"Found {len(sh_files)} .sh files.")
    # print(sh_files)
    with ThreadPoolExecutor(max_workers=len(sh_files)) as executor:
        for script in sh_files:
            executor.submit(run_script_continuously, script, SCRIPT_DURATION)

if __name__ == "__main__":
    main()
