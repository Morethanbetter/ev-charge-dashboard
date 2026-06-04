#!/bin/bash
set -e

echo "=== Building and starting services ==="

# Create necessary directories
mkdir -p uploads dedup_data

# Build and start all services (3 backend instances + nginx + db)
docker-compose build
docker-compose up -d

echo "=== Waiting for services to start ==="
sleep 15

echo "=== Checking service status ==="
docker-compose ps

echo ""
echo "=== Services are ready ==="
echo "Frontend: http://localhost"
echo "Backend API (via Nginx LB): http://localhost/api/"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Default login: admin / admin123"
echo ""
echo "Backend instances: app1, app2, app3 (round-robin via Nginx)"
