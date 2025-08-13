# Employee Attendance System - Complete Deployment Guide

## 🏗️ Architecture Overview

```
Internet → AWS Load Balancer → Instance 1 (Frontend) → Instance 2 (Backend + Telegram Bot) → Instance 3 (MongoDB)
```

- **Instance 1**: React Frontend (Port 3000) - HR Dashboard
- **Instance 2**: Flask Backend (Port 5000) + Telegram Bot
- **Instance 3**: MongoDB (Port 27017)
- **Load Balancer**: Routes traffic to frontend

## 🚀 Step-by-Step Deployment

### Prerequisites
- 3 AWS EC2 instances in the same VPC
- AWS Load Balancer configured
- Docker installed on all instances
- Your repository cloned on all instances

### Instance 1: Frontend Deployment

1. **SSH into Instance 1**
```bash
ssh -i your-key.pem ec2-user@your-instance1-public-ip
```

2. **Run the deployment script**
```bash
chmod +x deploy-instance1-frontend.sh
./deploy-instance1-frontend.sh
```

3. **Update the environment file**
```bash
# Edit frontend/.env and update:
VITE_API_URL=http://YOUR_BACKEND_PRIVATE_IP:5000
```

4. **Restart the frontend container**
```bash
docker restart frontend
```

### Instance 2: Backend + Telegram Bot Deployment

1. **SSH into Instance 2**
```bash
ssh -i your-key.pem ec2-user@your-instance2-public-ip
```

2. **Run the deployment script**
```bash
chmod +x deploy-instance2-backend.sh
./deploy-instance2-backend.sh
```

3. **Update environment files**
```bash
# Edit backend/.env:
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
SECRET_KEY=your-secret-key-change-this-in-production

# Edit telegram-bot/.env:
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance
BOT_TOKEN=your_telegram_bot_token_from_botfather
GROUP_CHAT_ID=your_telegram_group_chat_id
```

4. **Restart containers**
```bash
docker restart backend telegram-bot
```

### Instance 3: MongoDB Deployment

1. **SSH into Instance 3**
```bash
ssh -i your-key.pem ec2-user@your-instance3-public-ip
```

2. **Run the deployment script**
```bash
chmod +x deploy-instance3-mongodb.sh
./deploy-instance3-mongodb.sh
```

3. **Verify MongoDB is running**
```bash
docker ps
docker logs mongodb
```

## 🔧 Configuration Steps

### 1. Update Private IPs
Replace `YOUR_BACKEND_PRIVATE_IP` and `YOUR_MONGODB_PRIVATE_IP` in all `.env` files with actual private IPs.

### 2. Configure Telegram Bot
1. Get bot token from @BotFather
2. Add bot to your Telegram group
3. Get group chat ID from: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Update `telegram-bot/.env`

### 3. Add Sample Employees
```bash
# On Instance 2 (Backend)
cd backend
python add_sample_employees.py
```

### 4. Configure Load Balancer
- **Target Group**: Instance 1 (Frontend) on port 3000
- **Health Check**: HTTP on port 3000
- **Listener**: HTTP on port 80

## 🔒 Security Configuration

### AWS Security Groups

#### Instance 1 (Frontend)
- **Inbound**: Port 3000 from Load Balancer
- **Outbound**: All traffic

#### Instance 2 (Backend + Telegram Bot)
- **Inbound**: Port 5000 from Instance 1
- **Outbound**: Port 27017 to Instance 3

#### Instance 3 (MongoDB)
- **Inbound**: Port 27017 from Instance 2 only
- **Outbound**: All traffic

## 🧪 Testing the System

### 1. Test Frontend Access
- Visit your load balancer URL
- Should see the HR login page

### 2. Test HR Login
- Username: `hr.admin`
- Password: `hr.password`
- Should redirect to dashboard

### 3. Test Backend API
```bash
# From Instance 1
curl http://YOUR_BACKEND_PRIVATE_IP:5000/health
```

### 4. Test Telegram Bot
- Send "login" message in your Telegram group
- Check if attendance is recorded

### 5. Test Database Connection
```bash
# From Instance 2
docker exec -it backend python -c "
from models.database import get_db
db = get_db()
print('Database connected:', db.name)
"
```

## 🐛 Troubleshooting

### Frontend Not Loading
1. Check if frontend container is running: `docker ps`
2. Check frontend logs: `docker logs frontend`
3. Verify load balancer health checks

### Backend Connection Failed
1. Check backend container: `docker ps`
2. Check backend logs: `docker logs backend`
3. Verify MongoDB connection in backend logs
4. Check security groups

### Telegram Bot Not Responding
1. Check bot container: `docker ps`
2. Check bot logs: `docker logs telegram-bot`
3. Verify bot token and group chat ID
4. Check if bot is added to group

### Database Connection Issues
1. Check MongoDB container: `docker ps`
2. Check MongoDB logs: `docker logs mongodb`
3. Verify security group allows connection from backend
4. Check MongoDB URI in backend config

## 📊 Monitoring

### Container Status
```bash
# Check all containers
docker ps -a

# Check container logs
docker logs -f container_name

# Check container resources
docker stats
```

### Application Health
- Frontend: Load balancer health checks
- Backend: `curl http://backend-ip:5000/health`
- MongoDB: `docker exec mongodb mongosh --eval "db.runCommand('ping')"`

## 🔄 Updates and Maintenance

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart containers
docker build -t new-image-name .
docker stop container-name
docker rm container-name
docker run -d --name container-name -p port:port --env-file .env new-image-name
```

### Backup Database
```bash
# Create backup
docker exec mongodb mongodump --db employee_attendance --out /backup

# Copy backup from container
docker cp mongodb:/backup ./backup
```

## 📝 Important Notes

1. **Never expose MongoDB to the internet** - only allow access from backend instance
2. **Use strong JWT secrets** in production
3. **Regular backups** of MongoDB data
4. **Monitor container logs** for errors
5. **Test all connections** after deployment
6. **Update security groups** if you change instance IPs

## 🎯 Success Checklist

- [ ] Frontend accessible via load balancer
- [ ] HR can login with credentials
- [ ] Dashboard shows employee data
- [ ] Backend API responds to health check
- [ ] Telegram bot responds to messages
- [ ] MongoDB accessible from backend
- [ ] Sample employees added to database
- [ ] All security groups configured correctly

## 🆘 Support

If you encounter issues:
1. Check container logs first
2. Verify all environment variables are set
3. Confirm security group configurations
4. Test network connectivity between instances
5. Verify all services are running on correct ports