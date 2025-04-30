#!/bin/bash

# Name: run-service-2-test.sh
# Description: Runs JMeter test for service-2 and saves results to results2.jtl and report2/

echo "Starting JMeter test for service-2..."

jmeter -n -t service-2-test.jmx -l results2.jtl -e -o report2

echo "Test completed. Results saved to results2.jtl and HTML report generated in report2/"
