#!/bin/bash

# Script to build the Docker image
IMAGE_NAME="primemicroservice"

echo "Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

# Check if the build was successful
if [ $? -eq 0 ]; then
  echo "Docker image '$IMAGE_NAME' built successfully."
else
  echo "Docker build failed."
  exit 1
fi
