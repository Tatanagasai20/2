import os
from dotenv import load_dotenv
import pytz

# Load environment variables from .env file
load_dotenv()

class Config:
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/employee_attendance')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

    # HR credentials
    HR_USERNAME = os.getenv('HR_USERNAME', 'hr.admin')
    HR_PASSWORD = os.getenv('HR_PASSWORD', 'hr.password')

    # Timezone and working hours
    TIMEZONE = pytz.timezone('Asia/Kolkata')
    WORK_START_HOUR = 9
    WORK_END_HOUR = 18
    GRACE_PERIOD_MINUTES = 5
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

