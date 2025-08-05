#!/bin/bash

# Employee Attendance System - Deployment Script
# This script builds and runs all containers without docker-compose

set -e  # Exit on any error

echo "🚀 Starting Employee Attendance System Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if environment files exist
check_env_files() {
    print_status "Checking environment files..."
    
    if [ ! -f "backend/.env" ]; then
        print_warning "backend/.env not found. Creating from example..."
        cp backend/.env.example backend/.env
        print_warning "Please edit backend/.env with your actual configuration"
    fi
    
    if [ ! -f "telegram-bot/.env" ]; then
        print_warning "telegram-bot/.env not found. Creating from example..."
        cp telegram-bot/.env.example telegram-bot/.env
        print_warning "Please edit telegram-bot/.env with your actual configuration"
    fi
    
    if [ ! -f "frontend/.env" ]; then
        print_warning "frontend/.env not found. Creating from example..."
        cp frontend/.env.example frontend/.env
        print_warning "Please edit frontend/.env with your actual configuration"
    fi
}

# Stop and remove existing containers
cleanup_containers() {
    print_status "Cleaning up existing containers..."
    
    docker stop backend frontend nginx telegram-bot 2>/dev/null || true
    docker rm backend frontend nginx telegram-bot 2>/dev/null || true
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend
    print_status "Building backend image..."
    cd backend
    docker build -t attendance-backend .
    cd ..
    
    # Build frontend
    print_status "Building frontend image..."
    cd frontend
    docker build -t attendance-frontend .
    cd ..
    
    # Build nginx
    print_status "Building nginx image..."
    cd nginx
    docker build -t attendance-nginx .
    cd ..
    
    # Build telegram bot
    print_status "Building telegram bot image..."
    cd telegram-bot
    docker build -t attendance-bot .
    cd ..
}

# Update nginx configuration with local IP
update_nginx_config() {
    print_status "Updating nginx configuration..."
    
    # Get local IP address
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    print_status "Using local IP: $LOCAL_IP"
    
    # Create a temporary nginx config with the correct IP
    sed "s/172.31.x.x/$LOCAL_IP/g" nginx/nginx.conf > nginx/nginx.conf.tmp
    mv nginx/nginx.conf.tmp nginx/nginx.conf
}

# Run containers
run_containers() {
    print_status "Starting containers..."
    
    # Start backend first (other services depend on it)
    print_status "Starting backend container..."
    docker run -d \
        --name backend \
        -p 5000:5000 \
        --env-file backend/.env \
        --restart unless-stopped \
        attendance-backend
    
    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    sleep 10
    
    # Start frontend
    print_status "Starting frontend container..."
    docker run -d \
        --name frontend \
        -p 3000:3000 \
        --env-file frontend/.env \
        --restart unless-stopped \
        attendance-frontend
    
    # Start nginx
    print_status "Starting nginx container..."
    docker run -d \
        --name nginx \
        -p 80:80 \
        --restart unless-stopped \
        attendance-nginx
    
    # Start telegram bot
    print_status "Starting telegram bot container..."
    docker run -d \
        --name telegram-bot \
        --env-file telegram-bot/.env \
        --restart unless-stopped \
        attendance-bot
}

# Check container status
check_status() {
    print_status "Checking container status..."
    
    echo ""
    echo "Container Status:"
    echo "================="
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    echo "Container Logs (last 10 lines each):"
    echo "===================================="
    
    for container in backend frontend nginx telegram-bot; do
        echo ""
        echo "--- $container logs ---"
        docker logs --tail 10 $container 2>/dev/null || echo "Container not found"
    done
}

# Main deployment process
main() {
    print_status "Starting deployment process..."
    
    check_env_files
    cleanup_containers
    build_images
    update_nginx_config
    run_containers
    
    # Wait a bit for containers to fully start
    sleep 5
    
    check_status
    
    echo ""
    print_status "Deployment completed!"
    echo ""
    echo "Access your application:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost/api"
    echo "  Health Check: http://localhost/health"
    echo ""
    echo "To view logs: docker logs <container-name>"
    echo "To stop: docker stop backend frontend nginx telegram-bot"
    echo "To restart: ./deploy.sh"
}

# Run main function
main "$@"