#!/bin/bash

# Backend Restart Script
echo "🔄 Backend Restart Script"
echo "========================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Stop and remove existing backend container
print_status "Stopping existing backend container..."
docker stop backend 2>/dev/null || true
docker rm backend 2>/dev/null || true

# Remove existing image
print_status "Removing existing backend image..."
docker rmi attendance-backend 2>/dev/null || true

# Build new image
print_status "Building new backend image..."
cd backend
docker build -t attendance-backend .
cd ..

# Check if build was successful
if [ $? -eq 0 ]; then
    print_status "✅ Image built successfully"
else
    print_error "❌ Image build failed"
    exit 1
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    print_warning "backend/.env not found, creating from example..."
    cp backend/.env.example backend/.env
    print_warning "Please edit backend/.env with your actual configuration"
fi

# Start backend container
print_status "Starting backend container..."
docker run -d \
    --name backend \
    -p 5000:5000 \
    --env-file backend/.env \
    --restart unless-stopped \
    attendance-backend

# Wait for container to start
print_status "Waiting for container to start..."
sleep 10

# Check if container is running
if docker ps | grep -q backend; then
    print_status "✅ Backend container is running"
    
    # Check logs
    echo ""
    print_status "Container logs:"
    docker logs backend
    
    # Test health endpoint
    echo ""
    print_status "Testing health endpoint..."
    sleep 5
    
    if curl -s http://localhost:5000/health > /dev/null; then
        print_status "✅ Health endpoint is responding"
        curl http://localhost:5000/health
    else
        print_error "❌ Health endpoint is not responding"
        echo ""
        print_status "Recent logs:"
        docker logs --tail 10 backend
    fi
    
else
    print_error "❌ Backend container failed to start"
    echo ""
    print_status "Container logs:"
    docker logs backend
fi

echo ""
print_status "Restart complete!"