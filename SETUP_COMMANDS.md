# 🚀 Complete Setup Commands

## 📋 **Prerequisites**
- 3 AWS EC2 instances in same VPC
- Load Balancer configured
- Repository cloned on all instances

---

## 🖥️ **Instance 1: Frontend**

### **Connect & Install Docker**
```bash
ssh -i your-key.pem ec2-user@your-instance1-public-ip
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user
# Logout and login again, then:
newgrp docker
```

### **Build & Run Frontend**
```bash
cd frontend
docker build -t employee-frontend .
cat > .env << EOF
VITE_API_URL=http://YOUR_BACKEND_PRIVATE_IP:5000
EOF
docker run -d --name frontend --restart unless-stopped -p 3000:3000 --env-file .env employee-frontend
docker ps
```

---

## 🐍 **Instance 2: Backend + Telegram Bot**

### **Connect & Install Docker**
```bash
ssh -i your-key.pem ec2-user@your-instance2-public-ip
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user
# Logout and login again, then:
newgrp docker
```

### **Generate JWT Secret**
```bash
sudo yum install python3 -y
python3 -c "import secrets,string;print(''.join(secrets.choice(string.ascii_letters+string.digits+string.punctuation)for i in range(64)))"
```

### **Build & Run Backend**
```bash
cd backend
cat > .env << EOF
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance
JWT_SECRET_KEY=YOUR_GENERATED_JWT_SECRET
SECRET_KEY=YOUR_FLASK_SECRET_KEY
EOF
docker build -t employee-backend .
docker run -d --name backend --restart unless-stopped -p 5000:5000 --env-file .env employee-backend
```

### **Build & Run Telegram Bot**
```bash
cd ../telegram-bot
cat > .env << EOF
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
GROUP_CHAT_ID=YOUR_TELEGRAM_GROUP_ID
EOF
docker build -t employee-telegram-bot .
docker run -d --name telegram-bot --restart unless-stopped --env-file .env employee-telegram-bot
docker ps
```

---

## 🗄️ **Instance 3: MongoDB**

### **Connect & Install MongoDB**
```bash
ssh -i your-key.pem ec2-user@your-instance3-public-ip
sudo yum update -y
sudo tee /etc/yum.repos.d/mongodb-org-6.0.repo << EOF
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
EOF
sudo yum install -y mongodb-org
```

### **Configure & Start MongoDB**
```bash
sudo mkdir -p /var/lib/mongo /var/log/mongodb
sudo chown -R mongod:mongod /var/lib/mongo /var/log/mongodb
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
sudo systemctl start mongod
sudo systemctl enable mongod
```

### **Setup Database**
```bash
mongosh << EOF
use employee_attendance
db.createCollection('employees')
db.createCollection('attendance_records')
db.employees.createIndex({employee_id: 1}, {unique: true})
db.employees.createIndex({phone_number: 1}, {unique: true})
db.employees.createIndex({telegram_id: 1}, {unique: true})
db.attendance_records.createIndex({employee_id: 1, date: 1})
db.attendance_records.createIndex({date: 1})
db.attendance_records.createIndex({status: 1})
exit
EOF
```

---

## 🔧 **Configuration**

### **Get Private IPs**
```bash
# On each instance, run:
curl -s http://169.254.169.254/latest/meta-data/local-ipv4
```

### **Update .env Files**
Replace `YOUR_BACKEND_PRIVATE_IP` and `YOUR_MONGODB_PRIVATE_IP` with actual private IPs.

---

## ✅ **Test Everything**

### **Test MongoDB**
```bash
# On Instance 3:
mongosh --eval "db.runCommand('ping')"
```

### **Test Backend**
```bash
# On Instance 2:
curl http://localhost:5000/health
```

### **Test Frontend**
```bash
# On Instance 1:
curl http://localhost:3000
```

---

## 🔒 **Security Groups**

### **Instance 1 (Frontend)**
- Inbound: Port 3000 from Load Balancer

### **Instance 2 (Backend)**
- Inbound: Port 5000 from Frontend Instance

### **Instance 3 (MongoDB)**
- Inbound: Port 27017 from Backend Instance only