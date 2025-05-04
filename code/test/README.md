# Automated Microservice Testing Framework

This system runs performance/load tests for multiple microservices using `.sh` scripts (e.g., JMeter `.jmx` tests). Each script is executed in parallel and continuously for 1 hour, with logging enabled for monitoring.

## 🗂 Directory Structure

```
.
├── automated_test.py
├── client 1/
│   ├── run-service-1-test.sh
│   ├── run-service-2-test.sh
│   ├── service-1-test.jmx
│   └── service-2-test.jmx
├── client 2/
│   ├── run-service-1-test.sh
│   ├── run-service-2-test.sh
│   ├── service-1-test.jmx
│   └── service-2-test.jmx
└── logs/
    └── *.log
```

## 🚀 Running the Tests

To run all test scripts in the background and keep them running even if you disconnect:

```bash
nohup python3 automated_test.py &
```

- `nohup` ensures the script continues running after logout or disconnection.
- `&` puts the process in the background.
- Each `.sh` script is run in parallel and logs to a dedicated file under the `logs/` directory.
- The main script itself does **not** print to terminal.

## 🧪 Log Files

Logs are saved in `logs/` with names based on the script paths. For example:

```bash
logs/client_1_run-service-1-test.sh.log
logs/client_2_run-service-2-test.sh.log
```

Each log includes:

- A timestamped session header.
- Output of the corresponding `.sh` script.
- Notes when a script is restarted (if it exits before 1 hour).

## 🛑 Stopping the Tests

To stop the running background script:

```bash
pkill -f automated_test.py
```

This will terminate all instances of `automated_test.py`.

## 🔍 Monitoring

You can check if the script is still running with:

```bash
ps aux | grep automated_test.py
```

Or monitor log output using:

```bash
tail -f logs/client_1_run-service-1-test.sh.log
```

## ⚙️ Customization

- Test duration is currently set to **1 hour** per script. You can change it in `automated_test.py`:

```python
SCRIPT_DURATION = 3600  # seconds
```

- Logs are appended, not overwritten, to preserve history.
