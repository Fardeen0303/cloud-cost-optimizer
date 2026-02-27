#!/bin/bash
set -e

echo "Deploying to Kubernetes..."

kubectl apply -f kubernetes/manifests/namespace.yaml
kubectl apply -f kubernetes/manifests/configmap.yaml
kubectl apply -f kubernetes/manifests/secret.yaml
kubectl apply -f kubernetes/manifests/api-gateway-deployment.yaml
kubectl apply -f kubernetes/manifests/cost-scanner-deployment.yaml
kubectl apply -f kubernetes/manifests/ingress.yaml

echo "Deployment completed!"
