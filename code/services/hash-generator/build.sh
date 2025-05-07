#!/bin/bash

# Exit immediately if a command fails
set -e

# Clean and package the app, skipping tests
mvn clean package -DskipTests

# Build Docker image with the name 'hash-gen-image'
docker build -t hash-gen-image .

# Optional: show image list to confirm build
docker images | grep hash-gen-image
