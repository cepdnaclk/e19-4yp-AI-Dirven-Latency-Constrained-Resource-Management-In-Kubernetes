#!/bin/bash
echo "Starting client activation..."

echo "Activating Prime Verifier Service and Echo Service Clients..."
nohup python ../test/automated_test.py > ../test/automated_test.log 2>&1 &

echo "Activating Hash Generator Service Clients..."
nohup locust -f ../services/hash-generator/client/locustfile.py > ../services/hash-generator/client/locustfile.log 2>&1 &

echo "Activating Random Password Generator Service Clients..."
nohup locust -f ../services/random-password-generator/client/locustfile.py > ../services/random-password-generator/client/locustfile.log 2>&1 &

echo "All clients activated."
