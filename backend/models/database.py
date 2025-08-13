from pymongo import MongoClient
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        
    def connect(self):
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client.employee_attendance
            logger.info("Connected to MongoDB successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def get_db(self):
        if not self.db:
            self.connect()
        return self.db
    
    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global database instance
db_instance = Database()

def init_db(app):
    """Initialize database connection"""
    with app.app_context():
        if db_instance.connect():
            # Create indexes for better performance
            try:
                db = db_instance.get_db()
                
                # Create indexes
                db.employees.create_index("employee_id", unique=True)
                db.employees.create_index("phone_number", unique=True)
                db.employees.create_index("telegram_id", unique=True)
                
                db.attendance_records.create_index([("employee_id", 1), ("date", 1)])
                db.attendance_records.create_index("date")
                db.attendance_records.create_index("status")
                
                logger.info("Database indexes created successfully")
            except Exception as e:
                logger.error(f"Error creating indexes: {e}")
        else:
            logger.error("Failed to initialize database")

def get_db():
    """Get database instance"""
    return db_instance.get_db()