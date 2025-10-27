#!/usr/bin/env python3
"""
Script to add sample employees to the MongoDB database
Run this after setting up the backend and MongoDB
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import get_db
from models.employee import EmployeeModel

def add_sample_employees():
    """Add sample employees to the database"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize database and employee model
    db = get_db()
    employee_model = EmployeeModel()
    
    # Sample employee data
    sample_employees = [
        {
            "employee_id": "EMP001",
            "employee_name": "John Doe",
            "phone_number": "+1234567890",
            "telegram_id": 123456789,
            "status": "active"
        },
        {
            "employee_id": "EMP002",
            "employee_name": "Jane Smith",
            "phone_number": "+1234567891",
            "telegram_id": 123456790,
            "status": "active"
        },
        {
            "employee_id": "EMP003",
            "employee_name": "Mike Johnson",
            "phone_number": "+1234567892",
            "telegram_id": 123456791,
            "status": "active"
        },
        {
            "employee_id": "EMP004",
            "employee_name": "Sarah Wilson",
            "phone_number": "+1234567893",
            "telegram_id": 123456792,
            "status": "active"
        },
        {
            "employee_id": "EMP005",
            "employee_name": "David Brown",
            "phone_number": "+1234567894",
            "telegram_id": 123456793,
            "status": "active"
        }
    ]
    
    print("🚀 Adding sample employees to the database...")
    
    success_count = 0
    error_count = 0
    
    for employee_data in sample_employees:
        try:
            result = employee_model.add_employee(employee_data)
            if result.get('success'):
                print(f"✅ Added employee: {employee_data['employee_name']} ({employee_data['employee_id']})")
                success_count += 1
            else:
                print(f"❌ Failed to add employee {employee_data['employee_name']}: {result.get('error')}")
                error_count += 1
        except Exception as e:
            print(f"❌ Error adding employee {employee_data['employee_name']}: {str(e)}")
            error_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Successfully added: {success_count} employees")
    print(f"   ❌ Failed to add: {error_count} employees")
    
    if success_count > 0:
        print(f"\n🎉 Sample employees added successfully!")
        print(f"📱 You can now test the Telegram bot with these employees")
        print(f"🔑 HR can login to the frontend to view attendance data")
    else:
        print(f"\n⚠️ No employees were added. Please check your database connection.")

def list_employees():
    """List all employees in the database"""
    
    # Load environment variables
    load_dotenv()
    
    # Initialize database and employee model
    db = get_db()
    employee_model = EmployeeModel()
    
    print("📋 Listing all employees in the database...")
    
    try:
        employees = employee_model.get_all_employees()
        
        if not employees:
            print("📭 No employees found in the database")
            return
        
        print(f"\n👥 Found {len(employees)} employees:")
        print("-" * 80)
        print(f"{'ID':<10} {'Name':<20} {'Phone':<15} {'Telegram ID':<15} {'Status':<10}")
        print("-" * 80)
        
        for emp in employees:
            print(f"{emp['employee_id']:<10} {emp['employee_name']:<20} {emp['phone_number']:<15} {emp['telegram_id']:<15} {emp['status']:<10}")
        
        print("-" * 80)
        
    except Exception as e:
        print(f"❌ Error listing employees: {str(e)}")

if __name__ == "__main__":
    print("🏢 Employee Attendance System - Sample Data Setup")
    print("=" * 50)
    
    # Check if database is accessible
    try:
        db = get_db()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("Please check your MongoDB connection and try again")
        sys.exit(1)
    
    # Show menu
    while True:
        print("\n📋 Choose an option:")
        print("1. Add sample employees")
        print("2. List all employees")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            add_sample_employees()
        elif choice == "2":
            list_employees()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")