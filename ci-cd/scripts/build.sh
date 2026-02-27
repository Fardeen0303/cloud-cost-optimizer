#!/bin/bash
set -e

echo "Building all services..."

services=("api-gateway" "cost-scanner")

for service in "${services[@]}"; do
    echo "Building $service..."
    docker build -t cost-optimizer/$service:latest ./services/$service
done

echo "Build completed!"
