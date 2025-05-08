#!/bin/bash

# Create the parent directory for generated reports if it doesn't exist
REPORTS_DIR="generated_reports"
mkdir -p "$REPORTS_DIR"

# Create a timestamped folder name within the generated_reports directory
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
REPORT_DIR="$REPORTS_DIR/report_$TIMESTAMP"

# Create the timestamped report directory
mkdir -p "$REPORT_DIR"

# Run the JMeter test in non-GUI mode
jmeter -n -t $(dirname "$0")/service-2-test.jmx -l "$REPORT_DIR/results2.csv" -e -o "$REPORT_DIR"

# Print a message when the test is completed
echo "Test completed. Results saved to $REPORT_DIR/results2.csv and HTML report generated in $REPORT_DIR/"
