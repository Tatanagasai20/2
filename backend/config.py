import os
from dotenv import load_dotenv
import pytz

load_dotenv()

class Config:
    MONGODB_URI = os.getenv('MONGODB_URI')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    
    # HR credentials
    HR_USERNAME = os.getenv('HR_USERNAME', 'hr.admin')
    HR_PASSWORD = os.getenv('HR_PASSWORD', 'hr.password')
    
    # Timezone
    TIMEZONE = pytz.timezone('Asia/Kolkata')
    
    # Working hours
    WORK_START_HOUR = 9
    WORK_END_HOUR = 18
    GRACE_PERIOD_MINUTES = 5