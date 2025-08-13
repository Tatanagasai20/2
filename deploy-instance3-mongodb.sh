#!/bin/bash

# Instance 3: MongoDB Deployment Script
# This script deploys MongoDB on the third AWS instance

echo "🚀 Deploying MongoDB on Instance 3..."

# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Logout and login again for group changes to take effect
echo "Please logout and login again, then run: newgrp docker"

# Create MongoDB data directory
sudo mkdir -p /data/db
sudo chown ec2-user:ec2-user /data/db

# Run MongoDB container
echo "🗄️ Starting MongoDB..."
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v /data/db:/data/db \
  -e MONGO_INITDB_DATABASE=employee_attendance \
  mongo:6.0

# Wait for MongoDB to start
echo "⏳ Waiting for MongoDB to start..."
sleep 10

# Create database and collections
echo "🔧 Setting up database..."
docker exec -it mongodb mongosh --eval "
  use employee_attendance;
  
  // Create collections
  db.createCollection('employees');
  db.createCollection('attendance_records');
  
  // Create indexes for better performance
  db.employees.createIndex({employee_id: 1}, {unique: true});
  db.employees.createIndex({phone_number: 1}, {unique: true});
  db.employees.createIndex({telegram_id: 1}, {unique: true});
  
  db.attendance_records.createIndex({employee_id: 1, date: 1});
  db.attendance_records.createIndex({date: 1});
  db.attendance_records.createIndex({status: 1});
  
  print('Database setup completed successfully!');
"

echo "✅ MongoDB deployed successfully!"
echo "🗄️ MongoDB available at: mongodb://$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4):27017"
echo "📝 Database name: employee_attendance"
echo "🔐 No authentication required (internal network only)"
echo "⚠️ Make sure your AWS Security Groups only allow access from your backend instance"