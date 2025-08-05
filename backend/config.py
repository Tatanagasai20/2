import os
from dotenv import load_dotenv
import pytz

# Load environment variables from .env file
load_dotenv()

class Config:
    # MySQL configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

    # SQLAlchemy configuration (using pymysql instead of mysqlconnector)
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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

