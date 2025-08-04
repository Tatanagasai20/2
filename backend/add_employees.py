#!/usr/bin/env python3
"""
Script to manually add employee data to MongoDB database.
Run this script to add employees before they start using the Telegram bot.

Usage:
    python add_employees.py
"""

import sys
import os
from datetime import datetime

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.employee import EmployeeModel
from config import Config

def add_single_employee():
    """Add a single employee interactively"""
    print("\n=== Add New Employee ===")
    
    employee_id = input("Enter Employee ID: ").strip()
    if not employee_id:
        print("Employee ID is required!")
        return False
    
    employee_name = input("Enter Employee Name: ").strip()
    if not employee_name:
        print("Employee Name is required!")
        return False
    
    phone_number = input("Enter Phone Number: ").strip()
    if not phone_number:
        print("Phone Number is required!")
        return False
    
    # Create employee data
    employee_data = {
        "employee_id": employee_id,
        "employee_name": employee_name,
        "phone_number": phone_number
    }
    
    # Add to database
    employee_model = EmployeeModel()
    result = employee_model.add_employee(employee_data)
    
    if result.get('success'):
        print(f"✅ Employee added successfully!")
        print(f"   ID: {employee_id}")
        print(f"   Name: {employee_name}")
        print(f"   Phone: {phone_number}")
        return True
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return False

def add_multiple_employees():
    """Add multiple employees from input"""
    print("\n=== Add Multiple Employees ===")
    print("Enter employee data in format: ID,Name,Phone")
    print("Enter 'done' when finished")
    print("Example: EMP001,John Doe,+1234567890")
    
    employee_model = EmployeeModel()
    added_count = 0
    
    while True:
        line = input("\nEmployee data: ").strip()
        
        if line.lower() == 'done':
            break
        
        if not line:
            continue
        
        try:
            parts = [part.strip() for part in line.split(',')]
            if len(parts) != 3:
                print("❌ Invalid format. Use: ID,Name,Phone")
                continue
            
            employee_id, employee_name, phone_number = parts
            
            employee_data = {
                "employee_id": employee_id,
                "employee_name": employee_name,
                "phone_number": phone_number
            }
            
            result = employee_model.add_employee(employee_data)
            
            if result.get('success'):
                print(f"✅ Added: {employee_name} ({employee_id})")
                added_count += 1
            else:
                print(f"❌ Error adding {employee_name}: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error processing line: {e}")
    
    print(f"\n📊 Total employees added: {added_count}")

def list_employees():
    """List all employees in the database"""
    print("\n=== All Employees ===")
    
    employee_model = EmployeeModel()
    employees = employee_model.get_all_employees()
    
    if not employees:
        print("No employees found in database.")
        return
    
    print(f"Found {len(employees)} employees:")
    print("-" * 80)
    print(f"{'ID':<10} {'Name':<25} {'Phone':<15} {'Telegram':<10} {'Status'}")
    print("-" * 80)
    
    for emp in employees:
        telegram_status = "✅ Linked" if emp.get('telegram_id') else "❌ Not Linked"
        telegram_id = str(emp.get('telegram_id', 'N/A'))[:8] + "..." if emp.get('telegram_id') else "N/A"
        print(f"{emp['employee_id']:<10} {emp['employee_name']:<25} {emp['phone_number']:<15} {telegram_id:<10} {telegram_status}")
    
    print(f"\n📊 Summary:")
    total = len(employees)
    linked = len([emp for emp in employees if emp.get('telegram_id')])
    print(f"Total Employees: {total}")
    print(f"Linked to Telegram: {linked}")
    print(f"Not Linked: {total - linked}")
    
    if total - linked > 0:
        print(f"\n💡 Tip: Employees need to send 'login' message in Telegram group to get linked automatically.")

def main():
    """Main function"""
    print("🏢 Employee Management System")
    print("=" * 40)
    
    # Check MongoDB connection
    try:
        employee_model = EmployeeModel()
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print("Please check your MONGODB_URI in the .env file")
        return
    
    while True:
        print("\nOptions:")
        print("1. Add single employee")
        print("2. Add multiple employees")
        print("3. List all employees")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            add_single_employee()
        elif choice == '2':
            add_multiple_employees()
        elif choice == '3':
            list_employees()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please select 1-4.")

if __name__ == "__main__":
    main()