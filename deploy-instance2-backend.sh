#!/bin/bash

# Instance 2: Backend + Telegram Bot Deployment Script
# This script deploys the Flask backend and Telegram bot on the second AWS instance

echo "🚀 Deploying Backend + Telegram Bot on Instance 2..."

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

# Create .env file for backend
cat > backend/.env << EOF
# MongoDB Configuration
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
SECRET_KEY=your-secret-key-change-this-in-production

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# HR Credentials
HR_USERNAME=hr.admin
HR_PASSWORD=hr.password

# Timezone
TIMEZONE=Asia/Kolkata
EOF

# Create .env file for telegram bot
cat > telegram-bot/.env << EOF
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_from_botfather
GROUP_CHAT_ID=your_telegram_group_chat_id

# Backend API Configuration
BACKEND_API_URL=http://localhost:5000

# MongoDB Configuration
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance

# Timezone
TIMEZONE=Asia/Kolkata
EOF

# Build and run backend container
echo "🔨 Building and running Backend..."
cd backend
docker build -t attendance-backend .
docker run -d --name backend -p 5000:5000 --env-file .env attendance-backend

# Build and run telegram bot container
echo "🤖 Building and running Telegram Bot..."
cd ../telegram-bot
docker build -t attendance-bot .
docker run -d --name telegram-bot --env-file .env attendance-bot

echo "✅ Backend and Telegram Bot deployed successfully!"
echo "🌐 Backend API available at: http://$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4):5000"
echo "📝 Don't forget to update:"
echo "   - MONGODB_URI in both .env files with your MongoDB private IP"
echo "   - BOT_TOKEN and GROUP_CHAT_ID in telegram-bot/.env"
echo "   - JWT_SECRET_KEY and SECRET_KEY in backend/.env"