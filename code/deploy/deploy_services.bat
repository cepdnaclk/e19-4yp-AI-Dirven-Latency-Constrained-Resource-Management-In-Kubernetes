@echo off
echo Deploying Service 1 and Service 2 to Kubernetes...

kubectl apply -f ../service1.yaml
echo Service 1 deployed.

kubectl apply -f ../service2.yaml
echo Service 2 deployed.

echo Checking the status of the pods...
kubectl get pods -n default

echo Checking the status of the services...
kubectl get svc -n default

echo Deployment complete.
pause
