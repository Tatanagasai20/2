import os
from dotenv import load_dotenv
import pytz

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:5000')
    
    # MySQL configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    
    GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
    
    # Working hours configuration (IST timezone)
    TIMEZONE = pytz.timezone('Asia/Kolkata')
    WORK_START_HOUR = 9  # 9 AM
    WORK_END_HOUR = 18   # 6 PM
    GRACE_PERIOD_MINUTES = 5  # 5 minutes grace period
    
    # Commands
    LOGIN_COMMANDS = ['login', 'checkin', 'in']
    LOGOUT_COMMANDS = ['logout', 'checkout', 'out']