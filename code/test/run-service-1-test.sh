#!/bin/bash

# Name: run-service-1-test.sh
# Description: Runs JMeter test for service-1 and saves results to results1.jtl and report1/

echo "Starting JMeter test for service-1..."

jmeter -n -t service-1-test.jmx -l results1.jtl -e -o report1

echo "Test completed. Results saved to results1.jtl and HTML report generated in report1/"
