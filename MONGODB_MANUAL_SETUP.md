# MongoDB Manual Setup Guide for Instance 3

## 🚀 Manual MongoDB Installation (No Docker)

This guide will help you set up MongoDB manually on your 3rd AWS instance without using Docker. Run each command one by one as instructed.

## 📋 Prerequisites

- SSH access to your 3rd AWS instance
- Sudo privileges
- Internet connectivity for package downloads

## 🔧 Step-by-Step Installation

### Step 1: Connect to Your Instance
```bash
ssh -i your-key.pem ec2-user@your-instance3-public-ip
```

### Step 2: Update System Packages
```bash
sudo yum update -y
```

### Step 3: Install MongoDB Repository
```bash
# Create MongoDB repository file
sudo tee /etc/yum.repos.d/mongodb-org-6.0.repo << EOF
[mongodb-org-6.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/6.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc
EOF
```

### Step 4: Install MongoDB
```bash
sudo yum install -y mongodb-org
```

### Step 5: Create Data Directory
```bash
# Create MongoDB data directory
sudo mkdir -p /var/lib/mongo
sudo mkdir -p /var/log/mongodb

# Set proper ownership
sudo chown -R mongod:mongod /var/lib/mongo
sudo chown -R mongod:mongod /var/log/mongodb
```

### Step 6: Configure MongoDB
```bash
# Create MongoDB configuration file
sudo tee /etc/mongod.conf << EOF
# network interfaces
net:
  port: 27017
  bindIp: 0.0.0.0

# data directory
storage:
  dbPath: /var/lib/mongo

# log directory
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

# process management
processManagement:
  timeZoneInfo: /usr/share/zoneinfo

# security (no authentication for internal network)
security:
  authorization: disabled
EOF
```

### Step 7: Start MongoDB Service
```bash
# Start MongoDB service
sudo systemctl start mongod

# Enable MongoDB to start on boot
sudo systemctl enable mongod

# Check service status
sudo systemctl status mongod
```

### Step 8: Verify MongoDB is Running
```bash
# Check if MongoDB is listening on port 27017
sudo netstat -tlnp | grep 27017

# Test MongoDB connection
mongosh --eval "db.runCommand('ping')"
```

### Step 9: Create Database and Collections
```bash
# Connect to MongoDB and create database
mongosh << EOF
use employee_attendance

// Create collections
db.createCollection('employees')
db.createCollection('attendance_records')

// Create indexes for better performance
db.employees.createIndex({employee_id: 1}, {unique: true})
db.employees.createIndex({phone_number: 1}, {unique: true})
db.employees.createIndex({telegram_id: 1}, {unique: true})

db.attendance_records.createIndex({employee_id: 1, date: 1})
db.attendance_records.createIndex({date: 1})
db.attendance_records.createIndex({status: 1})

// Show created collections
show collections

// Show indexes
db.employees.getIndexes()
db.attendance_records.getIndexes()

print('Database setup completed successfully!')
exit
EOF
```

### Step 10: Test Database Operations
```bash
# Test inserting a sample document
mongosh employee_attendance << EOF
db.employees.insertOne({
  employee_id: "EMP001",
  name: "Test Employee",
  phone_number: "+1234567890",
  telegram_id: "123456789",
  department: "IT",
  created_at: new Date()
})

// Verify the document was inserted
db.employees.find()

// Clean up test data
db.employees.deleteOne({employee_id: "EMP001"})

print('Database operations test completed successfully!')
exit
EOF
```

### Step 11: Configure Firewall (if needed)
```bash
# If you have a local firewall, allow MongoDB port
sudo firewall-cmd --permanent --add-port=27017/tcp
sudo firewall-cmd --reload

# Check firewall status
sudo firewall-cmd --list-ports
```

### Step 12: Get Instance Information
```bash
# Get your private IP address
PRIVATE_IP=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)
echo "Your MongoDB private IP: $PRIVATE_IP"

# Get your public IP (for reference only)
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Your MongoDB public IP: $PUBLIC_IP"
```

## 🔍 Verification Commands

### Check MongoDB Status
```bash
# Check service status
sudo systemctl status mongod

# Check if MongoDB is running
ps aux | grep mongod

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# Check MongoDB process
sudo netstat -tlnp | grep 27017
```

### Test Database Connection
```bash
# Test local connection
mongosh --eval "db.runCommand('ping')"

# Test with specific database
mongosh employee_attendance --eval "db.stats()"
```

## 📝 Configuration for Other Instances

### Backend Instance (.env file)
```bash
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance
```

### Telegram Bot Instance (.env file)
```bash
MONGODB_URI=mongodb://YOUR_MONGODB_PRIVATE_IP:27017/employee_attendance
```

**Replace `YOUR_MONGODB_PRIVATE_IP` with the actual private IP from Step 12.**

## 🚨 Security Notes

1. **Never expose MongoDB to the internet** - only allow access from your backend instance
2. **Use AWS Security Groups** to restrict access to port 27017 only from your backend instance
3. **No authentication** is configured for internal network use
4. **Regular backups** should be implemented for production use

## 🔧 Troubleshooting

### If MongoDB won't start:
```bash
# Check logs for errors
sudo tail -f /var/log/mongodb/mongod.log

# Check configuration file syntax
sudo mongod --config /etc/mongod.conf --dryrun

# Check file permissions
ls -la /var/lib/mongo/
ls -la /var/log/mongodb/
```

### If connection fails:
```bash
# Check if MongoDB is listening
sudo netstat -tlnp | grep 27017

# Check firewall rules
sudo firewall-cmd --list-all

# Test local connection
mongosh --eval "db.runCommand('ping')"
```

## ✅ Success Checklist

- [ ] MongoDB service is running (`sudo systemctl status mongod`)
- [ ] MongoDB is listening on port 27017 (`sudo netstat -tlnp | grep 27017`)
- [ ] Database connection works (`mongosh --eval "db.runCommand('ping')"`)
- [ ] Database and collections created successfully
- [ ] Indexes created successfully
- [ ] Private IP address noted for backend configuration
- [ ] AWS Security Groups configured to allow access only from backend instance

## 🎯 Next Steps

1. **Update your backend instance** with the MongoDB private IP
2. **Update your telegram bot instance** with the MongoDB private IP
3. **Test the complete system** by running the backend and frontend
4. **Verify data flow** from frontend → backend → MongoDB

Your MongoDB instance is now ready to serve your employee attendance system! 🎉