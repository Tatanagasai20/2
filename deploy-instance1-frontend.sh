#!/bin/bash

# Instance 1: Frontend Deployment Script
# This script deploys the React frontend on the first AWS instance

echo "🚀 Deploying Frontend on Instance 1..."

# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Logout and login again for group changes to take effect
echo "Please logout and login again, then run: newgrp docker"

# Clone repository (replace with your repo URL)
# git clone <your-repo-url>
# cd employee-attendance-system

# Create .env file for frontend
cat > frontend/.env << EOF
VITE_API_URL=http://YOUR_BACKEND_PRIVATE_IP:5000
VITE_APP_TITLE=Employee Attendance System
EOF

# Build and run frontend container
cd frontend
docker build -t attendance-frontend .
docker run -d --name frontend -p 3000:3000 --env-file .env attendance-frontend

echo "✅ Frontend deployed successfully on port 3000"
echo "🌐 Access your frontend at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3000"
echo "📝 Don't forget to update VITE_API_URL in frontend/.env with your backend private IP"