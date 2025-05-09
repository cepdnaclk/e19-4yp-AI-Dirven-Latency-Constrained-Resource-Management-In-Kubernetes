#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Build the Spring Boot application
echo "Packaging Spring Boot application..."
mvn clean package -DskipTests

# Set Docker environment to point to Minikube's Docker daemon
echo "Switching to Minikube's Docker environment..."
eval $(minikube docker-env)

# Build the Docker image
echo "Building Docker image 'rand-pw-gen-image' inside Minikube..."
docker build -t rand-pw-gen-image:latest .

# Apply Kubernetes service and deployment
echo "Deploying application using service.yaml..."
kubectl apply -f service.yaml

echo "✅ Application deployed successfully in Minikube!"
