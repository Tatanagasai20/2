# MySQL Setup Guide for Employee Attendance System

## 🚀 **Quick Setup Overview**

✅ **MongoDB ❌ → MySQL ✅**  
The system now uses **MySQL** instead of MongoDB for better AWS integration with RDS.

## 📋 **Option 1: AWS RDS MySQL (Recommended)**

### **Step 1: Create AWS RDS MySQL Instance**

```bash
# Via AWS Console:
1. Go to AWS RDS Console
2. Click "Create database"
3. Choose "MySQL"
4. Select "Free tier" (for testing) or "Production" 
5. Configure:
   - Engine version: MySQL 8.0
   - Instance class: db.t3.micro (free tier)
   - Allocated storage: 20 GB
   - DB instance identifier: employee-attendance-db
   - Master username: admin
   - Master password: [strong password]
   - VPC: Same as your EC2 instance
   - Security group: Allow MySQL (3306) from EC2
6. Click "Create database"
```

### **Step 2: Get RDS Endpoint**

```bash
# From AWS Console, copy the endpoint (looks like):
employee-attendance-db.xxxxxxxxx.us-east-1.rds.amazonaws.com
```

### **Step 3: Configure Security Group**

```bash
# Add inbound rule to RDS security group:
Type: MySQL/Aurora
Protocol: TCP
Port: 3306
Source: Your EC2 security group ID
```

### **Step 4: Create Database Schema**

```bash
# Connect to RDS from EC2 instance:
sudo yum install mysql -y  # Amazon Linux
# or
sudo apt install mysql-client -y  # Ubuntu

# Connect to database:
mysql -h employee-attendance-db.xxxxxxxxx.us-east-1.rds.amazonaws.com -u admin -p

# Run the schema:
mysql -h [RDS-ENDPOINT] -u admin -p < backend/create_database.sql
```

## 📋 **Option 2: Local MySQL (Development)**

### **Step 1: Install MySQL**

```bash
# Amazon Linux:
sudo yum install mysql-server -y
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Ubuntu:
sudo apt update
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
```

### **Step 2: Secure MySQL**

```bash
sudo mysql_secure_installation
# Set root password
# Remove anonymous users: Y
# Disallow root login remotely: N (for local development)
# Remove test database: Y
# Reload privilege tables: Y
```

### **Step 3: Create Database and User**

```bash
sudo mysql -u root -p

CREATE DATABASE employee_attendance;
CREATE USER 'attendance_user'@'%' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON employee_attendance.* TO 'attendance_user'@'%';
FLUSH PRIVILEGES;
EXIT;

# Import schema:
mysql -u attendance_user -p employee_attendance < backend/create_database.sql
```

## 🔧 **Configuration Files**

### **Backend Environment (.env)**

```bash
# backend/.env
MYSQL_HOST=employee-attendance-db.xxxxxxxxx.us-east-1.rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=your_rds_password
MYSQL_DATABASE=employee_attendance
JWT_SECRET_KEY=your-super-secret-jwt-key
HR_USERNAME=hr.admin
HR_PASSWORD=hr.password
```

### **Telegram Bot Environment (.env)**

```bash
# telegram-bot/.env
BOT_TOKEN=your_telegram_bot_token
BACKEND_API_URL=http://your-private-ip:5000
MYSQL_HOST=employee-attendance-db.xxxxxxxxx.us-east-1.rds.amazonaws.com
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=your_rds_password
MYSQL_DATABASE=employee_attendance
GROUP_CHAT_ID=your_telegram_group_id
```

## 📊 **Database Schema Overview**

### **Tables Created:**

1. **`employees`** - Employee master data
   - `employee_id` (Primary Key)
   - `employee_name`
   - `phone_number`
   - `telegram_id` (auto-linked)
   - `status` (active/inactive)

2. **`attendance_records`** - Daily attendance logs
   - `employee_id` (Foreign Key)
   - `date`, `login_time`, `logout_time`
   - `duration`, `status`
   - `is_grace_applied`

### **Sample Data Structure:**

```sql
-- Employee record
INSERT INTO employees (employee_id, employee_name, phone_number) 
VALUES ('EMP001', 'John Doe', '+1234567890');

-- Attendance record
INSERT INTO attendance_records (employee_id, employee_name, phone_number, telegram_id, date, login_time, status)
VALUES ('EMP001', 'John Doe', '+1234567890', 123456789, '2024-01-01', '2024-01-01 09:00:00', 'logged_in');
```

## 🚀 **Deployment Commands (Updated for MySQL)**

```bash
# 1. Update environment files with MySQL credentials
cp backend/.env.example backend/.env
cp telegram-bot/.env.example telegram-bot/.env
# Edit with your RDS details

# 2. Test database connection
mysql -h [RDS-ENDPOINT] -u admin -p -e "SHOW DATABASES;"

# 3. Build and run containers
docker build -t attendance-backend backend/
docker build -t attendance-frontend frontend/
docker build -t attendance-bot telegram-bot/
docker build -t attendance-nginx nginx/

# 4. Run services
docker run -d --name backend -p 5000:5000 --env-file backend/.env attendance-backend
docker run -d --name frontend -p 3000:3000 --env-file frontend/.env attendance-frontend
docker run -d --name nginx -p 80:80 attendance-nginx
docker run -d --name telegram-bot --env-file telegram-bot/.env attendance-bot
```

## ✅ **Verification Steps**

### **1. Test Database Connection**

```bash
# From EC2 instance:
mysql -h [RDS-ENDPOINT] -u admin -p

# Check tables:
USE employee_attendance;
SHOW TABLES;
DESCRIBE employees;
DESCRIBE attendance_records;
```

### **2. Test Backend API**

```bash
curl http://your-ec2-ip/health
# Should return: {"status":"healthy","service":"attendance-backend","database":"mysql"}
```

### **3. Add Test Employee**

```bash
docker exec -it backend python add_employees.py
# Add: EMP001, John Doe, +1234567890
```

### **4. Verify Database**

```bash
mysql -h [RDS-ENDPOINT] -u admin -p -e "SELECT * FROM employee_attendance.employees;"
```

## 🔍 **Troubleshooting**

### **Connection Issues:**

```bash
# Test connectivity:
telnet [RDS-ENDPOINT] 3306

# Check security groups:
# - RDS security group allows 3306 from EC2
# - EC2 security group allows outbound to 3306

# Test MySQL client:
mysql -h [RDS-ENDPOINT] -u admin -p --ssl-disabled
```

### **Application Errors:**

```bash
# Check backend logs:
docker logs backend

# Test database from container:
docker exec -it backend python -c "
from config import Config
import mysql.connector
conn = mysql.connector.connect(
    host=Config.MYSQL_HOST,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    database=Config.MYSQL_DATABASE
)
print('Database connected successfully!')
conn.close()
"
```

## 💰 **AWS Costs (Estimated)**

- **RDS MySQL db.t3.micro**: ~$12-15/month
- **Free Tier**: 750 hours free for first 12 months
- **Storage**: 20 GB free, then ~$0.115/GB/month
- **Backup**: 20 GB free automated backups

## 🔐 **Security Best Practices**

1. **Use strong passwords** for RDS
2. **Enable encryption** at rest
3. **Use VPC security groups** - no 0.0.0.0/0 access
4. **Regular backups** enabled
5. **Monitor access** via CloudTrail
6. **Rotate passwords** regularly

## 📈 **Performance Tips**

1. **Indexes**: Already optimized in schema
2. **Connection pooling**: Handled by SQLAlchemy
3. **Query optimization**: Use EXPLAIN for slow queries
4. **Monitoring**: Enable RDS Performance Insights
5. **Scaling**: Easy to upgrade instance class