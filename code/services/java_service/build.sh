#!/bin/bash

# Script to build the Docker image
IMAGE_NAME="service-1-image"

echo "Building Docker image: $IMAGE_NAME"
docker build --no-cache -t $IMAGE_NAME .

# Check if the build was successful
if [ $? -eq 0 ]; then
  echo "Docker image '$IMAGE_NAME' built successfully."
else
  echo "Docker build failed."
  exit 1
fi
