from models.database import get_db
from datetime import datetime
from bson import ObjectId

class EmployeeModel:
    def __init__(self):
        self.db = get_db()
    
    def add_employee(self, employee_data):
        """Add a new employee"""
        try:
            # Check if employee already exists
            existing = self.db.employees.find_one({
                '$or': [
                    {'employee_id': employee_data['employee_id']},
                    {'phone_number': employee_data['phone_number']}
                ]
            })
            
            if existing:
                return {"error": "Employee already exists with this ID or phone number"}
            
            # Add timestamps
            employee_data['created_at'] = datetime.utcnow()
            employee_data['updated_at'] = datetime.utcnow()
            employee_data['status'] = 'active'
            
            result = self.db.employees.insert_one(employee_data)
            return {"success": True, "employee_id": str(result.inserted_id)}
            
        except Exception as e:
            print(f"Error adding employee: {e}")
            return {"error": str(e)}
    
    def get_employee_by_telegram_id(self, telegram_id):
        """Get employee by Telegram ID"""
        try:
            employee = self.db.employees.find_one({'telegram_id': telegram_id})
            if employee:
                employee['_id'] = str(employee['_id'])
                if employee.get('created_at'):
                    employee['created_at'] = employee['created_at'].isoformat()
                if employee.get('updated_at'):
                    employee['updated_at'] = employee['updated_at'].isoformat()
            return employee
        except Exception as e:
            print(f"Error getting employee by telegram ID: {e}")
            return None
    
    def get_employee_by_id(self, employee_id):
        """Get employee by employee ID"""
        try:
            employee = self.db.employees.find_one({'employee_id': employee_id})
            if employee:
                employee['_id'] = str(employee['_id'])
                if employee.get('created_at'):
                    employee['created_at'] = employee['created_at'].isoformat()
                if employee.get('updated_at'):
                    employee['updated_at'] = employee['updated_at'].isoformat()
            return employee
        except Exception as e:
            print(f"Error getting employee by ID: {e}")
            return None
    
    def get_all_employees(self):
        """Get all employees"""
        try:
            employees = list(self.db.employees.find({'status': 'active'}))
            
            # Convert ObjectId to string for JSON serialization
            for employee in employees:
                employee['_id'] = str(employee['_id'])
                if employee.get('created_at'):
                    employee['created_at'] = employee['created_at'].isoformat()
                if employee.get('updated_at'):
                    employee['updated_at'] = employee['updated_at'].isoformat()
            
            return employees
        except Exception as e:
            print(f"Error getting all employees: {e}")
            return []
    
    def update_employee(self, employee_id, update_data):
        """Update employee information"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            
            result = self.db.employees.update_one(
                {'employee_id': employee_id},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating employee: {e}")
            return False
    
    def delete_employee(self, employee_id):
        """Soft delete employee (set status to inactive)"""
        try:
            result = self.db.employees.update_one(
                {'employee_id': employee_id},
                {'$set': {'status': 'inactive', 'updated_at': datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting employee: {e}")
            return False
    
    def search_employees(self, search_term):
        """Search employees by name, ID, or phone number"""
        try:
            query = {
                '$or': [
                    {'employee_name': {'$regex': search_term, '$options': 'i'}},
                    {'employee_id': {'$regex': search_term, '$options': 'i'}},
                    {'phone_number': {'$regex': search_term, '$options': 'i'}}
                ],
                'status': 'active'
            }
            
            employees = list(self.db.employees.find(query))
            
            # Convert ObjectId to string for JSON serialization
            for employee in employees:
                employee['_id'] = str(employee['_id'])
                if employee.get('created_at'):
                    employee['created_at'] = employee['created_at'].isoformat()
                if employee.get('updated_at'):
                    employee['updated_at'] = employee['updated_at'].isoformat()
            
            return employees
        except Exception as e:
            print(f"Error searching employees: {e}")
            return []