from pymongo import MongoClient
from datetime import datetime
from config import Config

class EmployeeModel:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client.employee_attendance
        self.collection = self.db.employees
        
        # Create indexes for better performance
        self.collection.create_index([("employee_id", 1)], unique=True)
        self.collection.create_index([("phone_number", 1)], unique=True)
        self.collection.create_index([("telegram_id", 1)], unique=True, sparse=True)
    
    def add_employee(self, employee_data):
        """Add a new employee"""
        try:
            employee = {
                "employee_id": employee_data['employee_id'],
                "employee_name": employee_data['employee_name'],
                "phone_number": employee_data['phone_number'],
                "telegram_id": employee_data.get('telegram_id'),
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.collection.insert_one(employee)
            return {"success": True, "employee_id": str(result.inserted_id)}
        except Exception as e:
            if "duplicate key error" in str(e).lower():
                return {"error": "Employee already exists"}
            return {"error": str(e)}
    
    def get_employee_by_phone(self, phone_number):
        """Get employee by phone number"""
        return self.collection.find_one({"phone_number": phone_number}, {"_id": 0})
    
    def get_employee_by_id(self, employee_id):
        """Get employee by employee ID"""
        return self.collection.find_one({"employee_id": employee_id}, {"_id": 0})
    
    def get_employee_by_telegram(self, telegram_id):
        """Get employee by telegram ID"""
        return self.collection.find_one({"telegram_id": telegram_id}, {"_id": 0})
    
    def update_telegram_id(self, phone_number, telegram_id):
        """Update telegram ID for an employee"""
        try:
            result = self.collection.update_one(
                {"phone_number": phone_number},
                {"$set": {"telegram_id": telegram_id, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            return False
    
    def get_all_employees(self):
        """Get all active employees"""
        return list(self.collection.find(
            {"status": "active"},
            {"_id": 0}
        ).sort("employee_name", 1))
    
    def update_employee(self, employee_id, updates):
        """Update employee information"""
        try:
            updates['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {"employee_id": employee_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            return False
    
    def deactivate_employee(self, employee_id):
        """Deactivate an employee"""
        try:
            result = self.collection.update_one(
                {"employee_id": employee_id},
                {"$set": {"status": "inactive", "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            return False