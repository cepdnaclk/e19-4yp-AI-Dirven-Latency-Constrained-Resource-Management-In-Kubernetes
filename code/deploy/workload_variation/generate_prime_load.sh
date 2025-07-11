#!/bin/bash

SERVICE_URL="http://service-1-service.default.svc.cluster.local:3001/isPrime"
PHASE=$1 # "up" or "down"
STEPS=(10 20 30 40 50 100 150 200 250 300 350 400 450 500 600 700 800 900 1000)

if [ "$PHASE" == "down" ]; then
  STEPS=(1000 900 800 700 600 500 450 400 350 300 250 200 150 100 50 40 30 20 10)
fi

for count in "${STEPS[@]}"; do
  echo "Sending $count requests..."
  for i in $(seq 1 $count); do
    # Generate a random number between 1000000 and 1001000
    number=$((1000000 + RANDOM % 1000))
    curl -s "$SERVICE_URL?number=$number" > /dev/null &
  done
  wait
  echo "Completed $count requests. Sleeping 60s..."
  sleep 60
done
