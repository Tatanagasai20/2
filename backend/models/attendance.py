from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from config import Config

class AttendanceModel:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI)
        self.db = self.client.employee_attendance
        self.collection = self.db.attendance_records
        
        # Create indexes for better performance
        self.collection.create_index([("telegram_id", 1), ("date", 1)])
        self.collection.create_index([("employee_username", 1)])
        self.collection.create_index([("timestamp", 1)])
    
    def record_attendance(self, data):
        """Record login/logout attendance"""
        try:
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            ist_timestamp = timestamp.astimezone(Config.TIMEZONE)
            date_str = ist_timestamp.strftime('%Y-%m-%d')
            
            if data['action'] == 'login':
                return self._handle_login(data, ist_timestamp, date_str)
            elif data['action'] == 'logout':
                return self._handle_logout(data, ist_timestamp, date_str)
        except Exception as e:
            print(f"Error recording attendance: {e}")
            return None
    
    def _handle_login(self, data, timestamp, date_str):
        """Handle login record"""
        # Check if already logged in today
        existing_record = self.collection.find_one({
            "telegram_id": data['telegram_id'],
            "date": date_str,
            "status": "logged_in"
        })
        
        if existing_record:
            return {"error": "Already logged in today"}
        
        # Create new attendance record
        record = {
            "employee_name": data['employee_name'],
            "employee_username": data['employee_username'],
            "telegram_id": data['telegram_id'],
            "date": date_str,
            "login_time": timestamp,
            "logout_time": None,
            "duration": None,
            "status": "logged_in",
            "is_grace_applied": data.get('is_grace_applied', False),
            "original_timestamp": datetime.fromisoformat(data.get('original_timestamp', data['timestamp']).replace('Z', '+00:00')),
            "created_at": datetime.utcnow()
        }
        
        result = self.collection.insert_one(record)
        return {"success": True, "record_id": str(result.inserted_id)}
    
    def _handle_logout(self, data, timestamp, date_str):
        """Handle logout record"""
        # Find active login record for today
        login_record = self.collection.find_one({
            "telegram_id": data['telegram_id'],
            "date": date_str,
            "status": "logged_in"
        })
        
        if not login_record:
            return {"error": "No active login found for today"}
        
        # Calculate duration
        login_time = login_record['login_time']
        if login_time.tzinfo is None:
            login_time = Config.TIMEZONE.localize(login_time)
        
        duration = timestamp - login_time
        duration_str = self._format_duration(duration)
        
        # Update record with logout information
        self.collection.update_one(
            {"_id": login_record['_id']},
            {
                "$set": {
                    "logout_time": timestamp,
                    "duration": duration_str,
                    "duration_seconds": duration.total_seconds(),
                    "status": "logged_out",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"success": True, "duration": duration_str}
    
    def _format_duration(self, duration):
        """Format duration to readable string"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def get_daily_attendance(self, date=None):
        """Get attendance records for a specific date"""
        if date is None:
            date = datetime.now(Config.TIMEZONE).strftime('%Y-%m-%d')
        
        records = list(self.collection.find(
            {"date": date},
            {"_id": 0}
        ).sort("login_time", 1))
        
        return records
    
    def get_employee_attendance(self, employee_username, start_date=None, end_date=None):
        """Get attendance records for a specific employee"""
        query = {"employee_username": employee_username}
        
        if start_date and end_date:
            query["date"] = {"$gte": start_date, "$lte": end_date}
        
        records = list(self.collection.find(
            query,
            {"_id": 0}
        ).sort("date", -1))
        
        return records
    
    def update_attendance_record(self, record_id, updates):
        """Update attendance record (for HR manual edits)"""
        try:
            from bson import ObjectId
            
            # Convert time strings back to datetime objects if needed
            if 'login_time' in updates:
                updates['login_time'] = datetime.fromisoformat(updates['login_time'])
            if 'logout_time' in updates:
                updates['logout_time'] = datetime.fromisoformat(updates['logout_time'])
            
            # Recalculate duration if both times are present
            if 'login_time' in updates and 'logout_time' in updates:
                duration = updates['logout_time'] - updates['login_time']
                updates['duration'] = self._format_duration(duration)
                updates['duration_seconds'] = duration.total_seconds()
            
            updates['updated_at'] = datetime.utcnow()
            updates['manually_edited'] = True
            
            result = self.collection.update_one(
                {"_id": ObjectId(record_id)},
                {"$set": updates}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating record: {e}")
            return False
    
    def get_attendance_summary(self, start_date=None, end_date=None):
        """Get attendance summary with statistics"""
        match_stage = {}
        if start_date and end_date:
            match_stage["date"] = {"$gte": start_date, "$lte": end_date}
        
        pipeline = [
            {"$match": match_stage},
            {"$group": {
                "_id": "$employee_username",
                "employee_name": {"$first": "$employee_name"},
                "total_days": {"$sum": 1},
                "total_hours": {"$sum": "$duration_seconds"},
                "logged_in_days": {"$sum": {"$cond": [{"$eq": ["$status", "logged_in"]}, 1, 0]}},
                "completed_days": {"$sum": {"$cond": [{"$eq": ["$status", "logged_out"]}, 1, 0]}}
            }},
            {"$addFields": {
                "total_hours_formatted": {
                    "$concat": [
                        {"$toString": {"$floor": {"$divide": ["$total_hours", 3600]}}},
                        "h ",
                        {"$toString": {"$floor": {"$divide": [{"$mod": ["$total_hours", 3600]}, 60]}}},
                        "m"
                    ]
                }
            }}
        ]
        
        return list(self.collection.aggregate(pipeline))