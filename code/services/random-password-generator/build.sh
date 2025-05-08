#!/bin/bash

# Print the start message
echo "Building Docker image 'rand-pw-gen-image'..."

# Build the Docker image
docker build -t rand-pw-gen-image:latest .

# Check if the build was successful
if [ $? -eq 0 ]; then
  echo "Docker image 'rand-pw-gen-image' built successfully!"
else
  echo "Docker image build failed."
fi
