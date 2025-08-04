from models.database import db, Employee
from datetime import datetime
from sqlalchemy.exc import IntegrityError

class EmployeeModel:
    def __init__(self):
        pass
    
    def add_employee(self, employee_data):
        """Add a new employee"""
        try:
            employee = Employee(
                employee_id=employee_data['employee_id'],
                employee_name=employee_data['employee_name'],
                phone_number=employee_data['phone_number'],
                telegram_id=employee_data.get('telegram_id'),
                status='active'
            )
            
            db.session.add(employee)
            db.session.commit()
            return {"success": True, "id": employee.id}
        except IntegrityError as e:
            db.session.rollback()
            if "employee_id" in str(e):
                return {"error": "Employee ID already exists"}
            elif "phone_number" in str(e):
                return {"error": "Phone number already exists"}
            else:
                return {"error": "Employee already exists"}
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}
    
    def get_employee_by_phone(self, phone_number):
        """Get employee by phone number"""
        employee = Employee.query.filter_by(phone_number=phone_number, status='active').first()
        return employee.to_dict() if employee else None
    
    def get_employee_by_id(self, employee_id):
        """Get employee by employee ID"""
        employee = Employee.query.filter_by(employee_id=employee_id, status='active').first()
        return employee.to_dict() if employee else None
    
    def get_employee_by_telegram(self, telegram_id):
        """Get employee by telegram ID"""
        employee = Employee.query.filter_by(telegram_id=telegram_id, status='active').first()
        return employee.to_dict() if employee else None
    
    def update_telegram_id(self, employee_id, telegram_id):
        """Update telegram ID for an employee"""
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if employee:
                employee.telegram_id = telegram_id
                employee.updated_at = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            return False
    
    def get_all_employees(self):
        """Get all active employees"""
        employees = Employee.query.filter_by(status='active').order_by(Employee.employee_name).all()
        return [emp.to_dict() for emp in employees]
    
    def update_employee(self, employee_id, updates):
        """Update employee information"""
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if employee:
                for key, value in updates.items():
                    if hasattr(employee, key):
                        setattr(employee, key, value)
                employee.updated_at = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            return False
    
    def deactivate_employee(self, employee_id):
        """Deactivate an employee"""
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if employee:
                employee.status = 'inactive'
                employee.updated_at = datetime.utcnow()
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            return False