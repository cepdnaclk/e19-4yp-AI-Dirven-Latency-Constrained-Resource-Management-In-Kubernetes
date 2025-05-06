#!/bin/bash
mvn clean package

# Build the Docker image with tag 'base64-image'
docker build -t base64-image .

# Confirm the image is built
docker images | grep base64-image
