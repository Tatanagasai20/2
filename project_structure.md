# Employee Attendance System - Project Structure

## Architecture Overview

This system consists of three main components:
1. **Telegram Bot** - For employee login/logout
2. **Flask Backend API** - Business logic and MongoDB integration
3. **React Frontend** - HR dashboard for monitoring and editing

## Project Structure

```
employee-attendance-system/
├── telegram-bot/
│   ├── bot.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
├── backend/
│   ├── app.py
│   ├── models/
│   │   └── attendance.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── attendance.py
│   ├── utils/
│   │   └── helpers.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.js
│   │   │   ├── Dashboard.js
│   │   │   ├── EmployeeList.js
│   │   │   └── EditRecord.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
└── README.md
```

## Key Features

### Telegram Bot Features:
- Employee login with grace period (5 minutes)
- Automatic logout tracking
- Name and timestamp capture
- Working hours validation (9 AM - 6 PM IST)

### Backend Features:
- MongoDB Atlas integration
- RESTful API endpoints
- Authentication system
- Attendance calculation logic
- Grace period handling

### Frontend Features:
- HR authentication (hr.admin/hr.password)
- Real-time attendance monitoring
- Manual timestamp editing
- Employee status dashboard
- Duration calculations

## Business Logic

### Login Process:
1. Employee sends message to Telegram group
2. Bot captures username and timestamp
3. Grace period applied (9:00-9:05 AM → recorded as 9:00 AM)
4. Beyond 9:06 AM → actual timestamp recorded
5. Status set to "logged in"

### Logout Process:
1. Employee sends logout message
2. Bot captures logout timestamp
3. Duration calculated
4. Status updated to "logged out"

### Grace Period Rules:
- Login between 9:00-9:05 AM IST → recorded as 9:00 AM
- Login at 9:06 AM or later → actual timestamp
- Working hours: 9:00 AM - 6:00 PM IST