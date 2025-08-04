# Employee Attendance System - Deployment Guide

## Architecture Overview

```
Internet → AWS Load Balancer → EC2 Instance (Private IP) → Nginx Reverse Proxy
                                                        ↓
                                Frontend (React) ← → Backend (Flask) ← → MongoDB Atlas
                                                        ↓
                                                Telegram Bot
```

## Prerequisites

1. **AWS EC2 Instance** with private IP
2. **MongoDB Atlas** cluster with connection string
3. **Telegram Bot Token** from @BotFather
4. **Docker** and **Docker Compose** installed on EC2
5. **Domain/Public IP** pointing to your EC2 instance

## Step 1: Prepare Your EC2 Instance

```bash
# Update system
sudo yum update -y  # For Amazon Linux
# or
sudo apt update && sudo apt upgrade -y  # For Ubuntu

# Install Docker
sudo yum install docker -y  # Amazon Linux
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Step 2: Clone and Configure the Application

```bash
# Clone your repository
git clone <your-repo-url>
cd employee-attendance-system

# Set up environment variables
cp backend/.env.example backend/.env
cp telegram-bot/.env.example telegram-bot/.env
cp frontend/.env.example frontend/.env
```

## Step 3: Configure Environment Variables

### Backend (.env)
```bash
# backend/.env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/employee_attendance
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
FLASK_ENV=production
FLASK_DEBUG=False
HR_USERNAME=hr.admin
HR_PASSWORD=hr.password
```

### Telegram Bot (.env)
```bash
# telegram-bot/.env
BOT_TOKEN=your_telegram_bot_token_from_botfather
BACKEND_API_URL=http://backend:5000
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/employee_attendance
GROUP_CHAT_ID=your_telegram_group_chat_id
```

### Frontend (.env)
```bash
# frontend/.env
VITE_API_URL=http://your-ec2-private-ip
VITE_APP_TITLE=Employee Attendance System
```

## Step 4: Get Your Telegram Group Chat ID

```bash
# Start your bot first, then add it to your group
# Send a message in the group, then visit:
# https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
# Look for "chat":{"id":-XXXXXXXXX,"title":"Your Group Name"}
# Use that negative number as your GROUP_CHAT_ID
```

## Step 5: Build and Deploy with Docker

### Build Individual Services

```bash
# Build backend
cd backend
docker build -t attendance-backend .

# Build frontend  
cd ../frontend
docker build -t attendance-frontend .

# Build telegram bot
cd ../telegram-bot
docker build -t attendance-bot .

# Build nginx
cd ../nginx
docker build -t attendance-nginx .
```

### Run Services with Docker Network

```bash
# Create network
docker network create attendance-network

# Run backend
docker run -d \
  --name backend \
  --network attendance-network \
  -p 5000:5000 \
  --env-file backend/.env \
  attendance-backend

# Run frontend
docker run -d \
  --name frontend \
  --network attendance-network \
  -p 3000:3000 \
  --env-file frontend/.env \
  attendance-frontend

# Run nginx reverse proxy
docker run -d \
  --name nginx \
  --network attendance-network \
  -p 80:80 \
  attendance-nginx

# Run telegram bot
docker run -d \
  --name telegram-bot \
  --network attendance-network \
  --env-file telegram-bot/.env \
  attendance-bot
```

## Step 6: Add Employee Data to Database

```bash
# Connect to backend container and run the employee script
docker exec -it backend python add_employees.py

# Or add employees programmatically:
# 1. Add single employee
# 2. Add multiple employees in batch
# 3. List all employees
```

### Example Employee Data Format:
```
Employee ID: EMP001
Employee Name: John Doe
Phone Number: +1234567890
```

## Step 7: Configure AWS Security Groups

### Inbound Rules:
- **Port 80** (HTTP) - Source: 0.0.0.0/0
- **Port 443** (HTTPS) - Source: 0.0.0.0/0 (if using SSL)
- **Port 22** (SSH) - Source: Your IP only
- **Port 5000** (Backend API) - Source: VPC only (for internal access)

### Outbound Rules:
- **All traffic** - Destination: 0.0.0.0/0

## Step 8: Update Nginx Configuration for Your Domain

```bash
# Edit nginx configuration if you have a domain
sudo docker exec -it nginx vi /etc/nginx/nginx.conf

# Update server_name from _ to your domain:
server_name your-domain.com www.your-domain.com;
```

## Step 9: Test the System

### Test Backend API:
```bash
curl http://your-ec2-public-ip/health
curl http://your-ec2-public-ip/api/
```

### Test Frontend:
```bash
# Visit in browser:
http://your-ec2-public-ip

# Login with:
Username: hr.admin
Password: hr.password
```

### Test Telegram Bot:
1. Add your bot to the Telegram group
2. Employees send "login" message
3. Check if attendance is recorded
4. Send "logout" message
5. Verify duration calculation

## Step 10: Monitoring and Logs

```bash
# View container logs
docker logs backend
docker logs frontend
docker logs telegram-bot
docker logs nginx

# Monitor container status
docker ps

# View system resources
docker stats
```

## Step 11: Database Verification

```bash
# Connect to MongoDB Atlas via mongo shell or compass
# Check collections:
# - employees (employee data)
# - attendance_records (login/logout records)

# Sample employee document:
{
  "employee_id": "EMP001",
  "employee_name": "John Doe",
  "phone_number": "+1234567890",
  "telegram_id": 123456789,
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z"
}

# Sample attendance document:
{
  "employee_id": "EMP001",
  "employee_name": "John Doe",
  "phone_number": "+1234567890",
  "telegram_id": 123456789,
  "date": "2024-01-01",
  "login_time": "2024-01-01T09:00:00+05:30",
  "logout_time": "2024-01-01T18:00:00+05:30",
  "duration": "9h 0m",
  "status": "logged_out",
  "is_grace_applied": true
}
```

## Troubleshooting

### Common Issues:

1. **Bot not responding**: Check BOT_TOKEN and GROUP_CHAT_ID
2. **Employee not found**: Verify employee data in MongoDB
3. **API not accessible**: Check backend container and network
4. **Frontend not loading**: Verify nginx proxy configuration
5. **Database connection**: Check MongoDB Atlas whitelist and credentials

### Useful Commands:

```bash
# Restart all services
docker restart backend frontend telegram-bot nginx

# Update application
git pull
docker build -t attendance-backend backend/
docker stop backend && docker rm backend
docker run -d --name backend --network attendance-network -p 5000:5000 --env-file backend/.env attendance-backend

# View detailed logs
docker logs -f telegram-bot
docker logs -f backend --tail 100
```

## Security Considerations

1. **Environment Variables**: Never commit .env files
2. **JWT Secret**: Use strong, unique secret key
3. **MongoDB**: Enable authentication and use strong passwords
4. **AWS Security Groups**: Restrict access to necessary ports only
5. **Regular Updates**: Keep Docker images and dependencies updated

## Scaling Considerations

1. **Multiple Backend Instances**: Use load balancer
2. **Database Indexing**: Already configured in the model
3. **Caching**: Consider Redis for session management
4. **Monitoring**: Implement CloudWatch or similar monitoring

## Backup Strategy

1. **MongoDB Atlas**: Enable automated backups
2. **Application Code**: Regular Git commits
3. **Environment Variables**: Secure backup of .env files
4. **Database Export**: Regular exports of employee and attendance data