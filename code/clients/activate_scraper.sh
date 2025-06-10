#!/bin/bash
echo "Starting prometheus scrapers..."

echo "Activating Prime Verifier Service and Echo Service Clients..."
nohup python ../scraper/prometheus_scraper.py > ../scraper/scraper.log 2>&1 &

echo "Activating Hash Generator Service Clients..."
nohup locust -f ../services/hash-generator/client/prometheus_scraper.py > ../services/hash-generator/client/scraper.log 2>&1 &

echo "Activating Random Password Generator Service Clients..."
nohup locust -f ../services/random-password-generator/client/prometheus_scraper.py > ../services/random-password-generator/client/scraper.log 2>&1 &

echo "All scrapers activated."
