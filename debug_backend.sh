#!/bin/bash

# Backend Debug Script
echo "🔍 Backend Debug Script"
echo "======================"

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running!"
    exit 1
fi

print_status "Docker is running"

# Check all containers
echo ""
print_status "Checking all containers:"
docker ps -a

# Check if backend container exists
if docker ps -a | grep -q backend; then
    print_status "Backend container exists"
    
    # Check if it's running
    if docker ps | grep -q backend; then
        print_status "Backend container is running"
        
        # Check port binding
        echo ""
        print_status "Checking port binding:"
        docker port backend
        
        # Check container logs
        echo ""
        print_status "Backend container logs (last 20 lines):"
        docker logs --tail 20 backend
        
        # Check if port 5000 is listening
        echo ""
        print_status "Checking if port 5000 is listening:"
        netstat -tlnp | grep 5000 || echo "Port 5000 not found in netstat"
        
        # Test local connection
        echo ""
        print_status "Testing local connection to backend:"
        if curl -s http://localhost:5000/health > /dev/null; then
            print_status "✅ Backend is responding locally"
            curl http://localhost:5000/health
        else
            print_error "❌ Backend is not responding locally"
        fi
        
    else
        print_error "Backend container is not running"
        echo ""
        print_status "Backend container logs:"
        docker logs backend
    fi
else
    print_error "Backend container does not exist"
fi

# Check for port conflicts
echo ""
print_status "Checking for port conflicts:"
sudo lsof -i :5000 || echo "No processes found on port 5000"

# Check Docker network
echo ""
print_status "Docker network information:"
docker network ls
docker network inspect bridge

# Check container resources
echo ""
print_status "Container resource usage:"
docker stats --no-stream

# Check environment variables
echo ""
print_status "Checking backend environment file:"
if [ -f "backend/.env" ]; then
    echo "✅ backend/.env exists"
    echo "Environment variables:"
    grep -v "^#" backend/.env | grep -v "^$"
else
    print_error "❌ backend/.env does not exist"
fi

echo ""
print_status "Debug complete!"