# Docker Deployment Guide - Employee Attendance System

## 🚀 Quick Start

1. **Make sure Docker is running**
2. **Configure your environment files** (see below)
3. **Run the deployment script:**
   ```bash
   ./deploy.sh
   ```

## 📋 Prerequisites

- Docker installed and running
- MySQL database running (local or remote)
- Telegram bot token from @BotFather
- Telegram group chat ID

## ⚙️ Configuration

### 1. Backend Configuration (`backend/.env`)

```bash
# Copy the example file
cp backend/.env.example backend/.env

# Edit with your actual values
MYSQL_HOST=localhost          # Your MySQL host
MYSQL_PORT=3306              # MySQL port
MYSQL_USER=your_mysql_user   # MySQL username
MYSQL_PASSWORD=your_password # MySQL password
MYSQL_DATABASE=employee_attendance

JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
FLASK_ENV=production
FLASK_DEBUG=False

HR_USERNAME=hr.admin
HR_PASSWORD=hr.password

TIMEZONE=Asia/Kolkata
WORK_START_HOUR=9
WORK_END_HOUR=18
GRACE_PERIOD_MINUTES=5
```

### 2. Telegram Bot Configuration (`telegram-bot/.env`)

```bash
# Copy the example file
cp telegram-bot/.env.example telegram-bot/.env

# Edit with your actual values
BOT_TOKEN=your_telegram_bot_token_from_botfather
GROUP_CHAT_ID=your_telegram_group_chat_id

BACKEND_API_URL=http://localhost:5000

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=employee_attendance

TIMEZONE=Asia/Kolkata
WORK_START_HOUR=9
WORK_END_HOUR=18
GRACE_PERIOD_MINUTES=5
```

### 3. Frontend Configuration (`frontend/.env`)

```bash
# Copy the example file
cp frontend/.env.example frontend/.env

# Edit with your actual values
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=Employee Attendance System
VITE_DEV_SERVER_PORT=3000
```

## 🔧 Manual Container Deployment

If you prefer to run containers manually instead of using the script:

### 1. Build Images
```bash
# Build backend
cd backend
docker build -t attendance-backend .
cd ..

# Build frontend
cd frontend
docker build -t attendance-frontend .
cd ..

# Build nginx
cd nginx
docker build -t attendance-nginx .
cd ..

# Build telegram bot
cd telegram-bot
docker build -t attendance-bot .
cd ..
```

### 2. Run Containers
```bash
# Start backend
docker run -d \
  --name backend \
  -p 5000:5000 \
  --env-file backend/.env \
  --restart unless-stopped \
  attendance-backend

# Start frontend
docker run -d \
  --name frontend \
  -p 3000:3000 \
  --env-file frontend/.env \
  --restart unless-stopped \
  attendance-frontend

# Start nginx
docker run -d \
  --name nginx \
  -p 80:80 \
  --restart unless-stopped \
  attendance-nginx

# Start telegram bot
docker run -d \
  --name telegram-bot \
  --env-file telegram-bot/.env \
  --restart unless-stopped \
  attendance-bot
```

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Containers Exit Immediately

**Check container logs:**
```bash
docker logs backend
docker logs frontend
docker logs nginx
docker logs telegram-bot
```

**Common causes:**
- Missing environment variables
- Database connection issues
- Port conflicts
- Missing dependencies

#### 2. Backend Container Issues

**Check if backend is running:**
```bash
curl http://localhost:5000/health
```

**Common backend issues:**
- MySQL connection failed
- Missing environment variables
- Port 5000 already in use

**Solutions:**
```bash
# Check if port 5000 is in use
sudo lsof -i :5000

# Kill process using port 5000
sudo kill -9 <PID>

# Restart backend container
docker restart backend
```

#### 3. Frontend Container Issues

**Check if frontend is running:**
```bash
curl http://localhost:3000
```

**Common frontend issues:**
- Build failed
- Port 3000 already in use
- API URL configuration

#### 4. Nginx Container Issues

**Check nginx configuration:**
```bash
docker exec nginx nginx -t
```

**Common nginx issues:**
- Configuration syntax errors
- Upstream server unreachable
- Port 80 already in use

#### 5. Telegram Bot Issues

**Check bot logs:**
```bash
docker logs telegram-bot
```

**Common bot issues:**
- Invalid bot token
- Wrong group chat ID
- Backend API unreachable

### Debugging Commands

```bash
# Check container status
docker ps -a

# Check container resources
docker stats

# Enter container shell
docker exec -it backend bash
docker exec -it frontend sh
docker exec -it nginx sh
docker exec -it telegram-bot bash

# View real-time logs
docker logs -f backend
docker logs -f frontend
docker logs -f nginx
docker logs -f telegram-bot

# Check network connectivity
docker network ls
docker network inspect bridge
```

## 📊 Health Checks

### Backend Health Check
```bash
curl http://localhost:5000/health
```
Expected response:
```json
{
  "status": "healthy",
  "service": "attendance-backend",
  "database": "mysql"
}
```

### Frontend Health Check
```bash
curl http://localhost:3000
```
Should return the React app HTML.

### Nginx Health Check
```bash
curl http://localhost
```
Should return the frontend application.

## 🗄️ Database Setup

### 1. Create MySQL Database
```sql
CREATE DATABASE employee_attendance;
```

### 2. Run Database Schema
```bash
# Copy the SQL file to your MySQL server
mysql -u your_user -p employee_attendance < backend/create_database.sql
```

### 3. Add Sample Employees
```bash
# Run the employee script
docker exec -it backend python add_employees.py
```

## 🔄 Restart Services

### Restart All Services
```bash
./deploy.sh
```

### Restart Individual Service
```bash
docker restart backend
docker restart frontend
docker restart nginx
docker restart telegram-bot
```

### Stop All Services
```bash
docker stop backend frontend nginx telegram-bot
```

## 📝 Log Files

### Container Logs
```bash
# View all logs
docker logs backend
docker logs frontend
docker logs nginx
docker logs telegram-bot

# Follow logs in real-time
docker logs -f backend
```

### Nginx Logs
```bash
# Access logs
docker exec nginx tail -f /var/log/nginx/access.log

# Error logs
docker exec nginx tail -f /var/log/nginx/error.log
```

## 🌐 Access URLs

After successful deployment:

- **Frontend (HR Dashboard):** http://localhost
- **Backend API:** http://localhost/api
- **Health Check:** http://localhost/health
- **Direct Backend:** http://localhost:5000
- **Direct Frontend:** http://localhost:3000

## 🔐 Default Credentials

- **HR Username:** hr.admin
- **HR Password:** hr.password

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review container logs
3. Verify environment configuration
4. Ensure all prerequisites are met
5. Check database connectivity

## 🚨 Important Notes

- Always use `--restart unless-stopped` for production
- Keep your environment files secure
- Regularly backup your database
- Monitor container resource usage
- Update your bot token and database credentials regularly