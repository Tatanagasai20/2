# 🐳 Complete Docker + MongoDB Setup Guide

## 🏗️ **Architecture Overview**
```
Internet → Load Balancer → Instance 1 (Frontend Docker) → Instance 2 (Backend Docker + Telegram Bot Docker) → Instance 3 (MongoDB Direct)
```

- **Instance 1**: React Frontend (Docker) - Port 3000
- **Instance 2**: Flask Backend (Docker) + Telegram Bot (Docker) - Port 5000
- **Instance 3**: MongoDB (Direct Installation) - Port 27017

## 📋 **Prerequisites Checklist**
- [ ] 3 AWS EC2 instances in the same VPC
- [ ] Docker installed on Instance 1 & 2
- [ ] Your repository cloned on all instances
- [ ] AWS Security Groups configured
- [ ] Load Balancer configured

---

## 🚀 **Instance 1: Frontend (Docker)**

### **Step 1: Connect to Instance 1**
```bash
ssh -i your-key.pem ec2-user@your-instance1-public-ip
```

### **Step 2: Install Docker**
```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Logout and login again, then run:
newgrp docker
```

### **Step 3: Clone Repository & Build Frontend**
```bash
# Clone your repository
git clone <your-repo-url>
cd <your-repo-name>/frontend

# Build Docker image
docker build -t employee-frontend .

# Create .env file
cat > .env << EOF
VITE_API_URL=http://YOUR_BACKEND_PRIVATE_IP:5000
EOF
```

### **Step 4: Run Frontend Container**
```bash
# Run the container
docker run -d \
  --name frontend \
  --restart unless-stopped \
  -p 3000:3000 \
  --env-file .env \
  employee-frontend

# Check if running
docker ps
docker logs frontend
```

---

## 🐍 **Instance 2: Backend + Telegram Bot (Docker)**

### **Step 1: Connect to Instance 2**
```bash
ssh -i your-key.pem ec2-user@your-instance2-public-ip
```

### **Step 2: Install Docker**
```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Logout and login again, then run:
newgrp docker
```

### **Step 3: Generate JWT Secret (Python)**
```bash
# Install Python if not available
sudo yum install python3 -y

# Generate JWT secret
python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + string.punctuation
jwt_secret = ''.join(secrets.choice(alphabet) for i in range(64))
print('JWT_SECRET_KEY=' + jwt_secret)
"
```

### **Step 4: Build Backend Container**
```bash
# Clone repository
git clone <your-repo-url>
cd <your-repo-name>/backend

# Create .env file
cat > .env << EOF
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance
JWT_SECRET_KEY=YOUR_GENERATED_JWT_SECRET
SECRET_KEY=YOUR_FLASK_SECRET_KEY
EOF

# Build Docker image
docker build -t employee-backend .
```

### **Step 5: Build Telegram Bot Container**
```bash
cd ../telegram-bot

# Create .env file
cat > .env << EOF
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
GROUP_CHAT_ID=YOUR_TELEGRAM_GROUP_ID
EOF

# Build Docker image
docker build -t employee-telegram-bot .
```

### **Step 6: Run Backend & Telegram Bot**
```bash
# Run Backend
docker run -d \
  --name backend \
  --restart unless-stopped \
  -p 5000:5000 \
  --env-file ../backend/.env \
  employee-backend

# Run Telegram Bot
docker run -d \
  --name telegram-bot \
  --restart unless-stopped \
  --env-file .env \
  employee-telegram-bot

# Check containers
docker ps
docker logs backend
docker logs telegram-bot
```

---

## 🗄️ **Instance 3: MongoDB (Direct Installation)**

### **Step 1: Connect to Instance 3**
```bash
ssh -i your-key.pem ec2-user@your-instance3-public-ip
```

### **Step 2: Install MongoDB**
```bash
# Update system
sudo yum update -y

# Create MongoDB repository
sudo tee /etc/yum.repos.d/mongodb-org-6.0.repo << EOF
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
EOF

# Install MongoDB
sudo yum install -y mongodb-org
```

### **Step 3: Configure MongoDB**
```bash
# Create directories
sudo mkdir -p /var/lib/mongo
sudo mkdir -p /var/log/mongodb
sudo chown -R mongod:mongod /var/lib/mongo
sudo chown -R mongod:mongod /var/log/mongodb

# Create config file
sudo tee /etc/mongod.conf << EOF
net:
  port: 27017
  bindIp: 0.0.0.0
storage:
  dbPath: /var/lib/mongo
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
processManagement:
  timeZoneInfo: /usr/share/zoneinfo
security:
  authorization: disabled
EOF
```

### **Step 4: Start MongoDB**
```bash
# Start and enable MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Check status
sudo systemctl status mongod
```

### **Step 5: Setup Database**
```bash
# Connect and create database
mongosh << EOF
use employee_attendance

// Create collections
db.createCollection('employees')
db.createCollection('attendance_records')

// Create indexes
db.employees.createIndex({employee_id: 1}, {unique: true})
db.employees.createIndex({phone_number: 1}, {unique: true})
db.employees.createIndex({telegram_id: 1}, {unique: true})

db.attendance_records.createIndex({employee_id: 1, date: 1})
db.attendance_records.createIndex({date: 1})
db.attendance_records.createIndex({status: 1})

print('Database setup completed!')
exit
EOF
```

---

## 🔧 **Configuration & Testing**

### **Step 1: Update Private IPs**
Replace `YOUR_BACKEND_PRIVATE_IP` and `YOUR_MONGODB_PRIVATE_IP` in all `.env` files with actual private IPs.

### **Step 2: Test Connections**
```bash
# Test MongoDB (Instance 3)
mongosh --eval "db.runCommand('ping')"

# Test Backend (Instance 2)
curl http://localhost:5000/health

# Test Frontend (Instance 1)
curl http://localhost:3000
```

### **Step 3: Test Complete Flow**
1. **Frontend** → **Backend** → **MongoDB**
2. **Telegram Bot** → **MongoDB**
3. **Load Balancer** → **Frontend**

---

## 🔒 **Security Configuration**

### **AWS Security Groups**

#### **Instance 1 (Frontend)**
- **Inbound**: Port 3000 from Load Balancer
- **Outbound**: All traffic

#### **Instance 2 (Backend)**
- **Inbound**: Port 5000 from Frontend Instance
- **Outbound**: Port 27017 to MongoDB Instance

#### **Instance 3 (MongoDB)**
- **Inbound**: Port 27017 from Backend Instance only
- **Outbound**: All traffic

---

## 🚨 **Troubleshooting**

### **Docker Issues**
```bash
# Check container logs
docker logs <container-name>

# Restart containers
docker restart <container-name>

# Check container status
docker ps -a
```

### **MongoDB Issues**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check logs
sudo tail -f /var/log/mongodb/mongod.log

# Check if listening
sudo netstat -tlnp | grep 27017
```

### **Connection Issues**
```bash
# Test MongoDB connection
mongosh --eval "db.runCommand('ping')"

# Test backend health
curl http://localhost:5000/health

# Check environment variables
docker exec <container-name> env | grep MONGODB
```

---

## ✅ **Success Checklist**

- [ ] Frontend container running on Instance 1 (Port 3000)
- [ ] Backend container running on Instance 2 (Port 5000)
- [ ] Telegram Bot container running on Instance 2
- [ ] MongoDB running on Instance 3 (Port 27017)
- [ ] All containers can communicate with each other
- [ ] Load Balancer routing to Frontend
- [ ] Frontend can reach Backend
- [ ] Backend can reach MongoDB
- [ ] Telegram Bot can reach MongoDB

---

## 🎯 **Next Steps**

1. **Test the complete system** end-to-end
2. **Add sample employees** to test functionality
3. **Configure monitoring** and logging
4. **Set up backups** for MongoDB
5. **Implement CI/CD** pipeline

Your Docker + MongoDB system is now ready! 🎉