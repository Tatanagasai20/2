from models.database import get_db
from datetime import datetime, timedelta
import pytz
from config import Config
from bson import ObjectId

class AttendanceModel:
    def __init__(self):
        self.db = get_db()
    
    def record_attendance(self, data):
        """Record login/logout attendance"""
        try:
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            ist_timestamp = timestamp.astimezone(Config.TIMEZONE)
            date_obj = ist_timestamp.strftime('%Y-%m-%d')
            
            if data['action'] == 'login':
                return self._handle_login(data, ist_timestamp, date_obj)
            elif data['action'] == 'logout':
                return self._handle_logout(data, ist_timestamp, date_obj)
        except Exception as e:
            print(f"Error recording attendance: {e}")
            return {"error": str(e)}
    
    def _handle_login(self, data, timestamp, date_obj):
        """Handle login record"""
        try:
            # Check if already logged in today
            existing_record = self.db.attendance_records.find_one({
                'telegram_id': data['telegram_id'],
                'date': date_obj,
                'status': 'logged_in'
            })
            
            if existing_record:
                return {"error": "Already logged in today"}
            
            # Create new attendance record
            record = {
                'employee_id': data.get('employee_id'),
                'employee_name': data['employee_name'],
                'phone_number': data.get('phone_number'),
                'telegram_id': data['telegram_id'],
                'date': date_obj,
                'login_time': timestamp,
                'logout_time': None,
                'duration': None,
                'duration_seconds': None,
                'status': 'logged_in',
                'is_grace_applied': data.get('is_grace_applied', False),
                'original_timestamp': datetime.fromisoformat(data.get('original_timestamp', data['timestamp']).replace('Z', '+00:00')),
                'manually_edited': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.db.attendance_records.insert_one(record)
            return {"success": True, "record_id": str(result.inserted_id)}
        except Exception as e:
            print(f"Error in login: {e}")
            return {"error": str(e)}
    
    def _handle_logout(self, data, timestamp, date_obj):
        """Handle logout record"""
        try:
            # Find active login record for today
            login_record = self.db.attendance_records.find_one({
                'telegram_id': data['telegram_id'],
                'date': date_obj,
                'status': 'logged_in'
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
            self.db.attendance_records.update_one(
                {'_id': login_record['_id']},
                {
                    '$set': {
                        'logout_time': timestamp,
                        'duration': duration_str,
                        'duration_seconds': int(duration.total_seconds()),
                        'status': 'logged_out',
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return {"success": True, "duration": duration_str}
        except Exception as e:
            print(f"Error in logout: {e}")
            return {"error": str(e)}
    
    def _format_duration(self, duration):
        """Format duration to readable string"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def get_daily_attendance(self, date=None):
        """Get daily attendance records"""
        try:
            if not date:
                date = datetime.now(Config.TIMEZONE).strftime('%Y-%m-%d')
            
            records = list(self.db.attendance_records.find({'date': date}))
            
            # Convert ObjectId to string for JSON serialization
            for record in records:
                record['_id'] = str(record['_id'])
                if record.get('login_time'):
                    record['login_time'] = record['login_time'].isoformat()
                if record.get('logout_time'):
                    record['logout_time'] = record['logout_time'].isoformat()
                if record.get('created_at'):
                    record['created_at'] = record['created_at'].isoformat()
                if record.get('updated_at'):
                    record['updated_at'] = record['updated_at'].isoformat()
            
            return records
        except Exception as e:
            print(f"Error getting daily attendance: {e}")
            return []
    
    def get_employee_attendance(self, employee_identifier, start_date=None, end_date=None):
        """Get attendance records for specific employee"""
        try:
            query = {}
            
            # Build query based on identifier type
            if employee_identifier.isdigit():
                query['telegram_id'] = int(employee_identifier)
            else:
                query['$or'] = [
                    {'employee_id': employee_identifier},
                    {'phone_number': employee_identifier}
                ]
            
            # Add date range if provided
            if start_date and end_date:
                query['date'] = {
                    '$gte': start_date,
                    '$lte': end_date
                }
            
            records = list(self.db.attendance_records.find(query))
            
            # Convert ObjectId to string for JSON serialization
            for record in records:
                record['_id'] = str(record['_id'])
                if record.get('login_time'):
                    record['login_time'] = record['login_time'].isoformat()
                if record.get('logout_time'):
                    record['logout_time'] = record['logout_time'].isoformat()
                if record.get('created_at'):
                    record['created_at'] = record['created_at'].isoformat()
                if record.get('updated_at'):
                    record['updated_at'] = record['updated_at'].isoformat()
            
            return records
        except Exception as e:
            print(f"Error getting employee attendance: {e}")
            return []
    
    def get_attendance_summary(self, start_date=None, end_date=None):
        """Get attendance summary with statistics"""
        try:
            if not start_date:
                start_date = datetime.now(Config.TIMEZONE).strftime('%Y-%m-%d')
            if not end_date:
                end_date = start_date
            
            pipeline = [
                {
                    '$match': {
                        'date': {'$gte': start_date, '$lte': end_date}
                    }
                },
                {
                    '$group': {
                        '_id': '$date',
                        'total_employees': {'$sum': 1},
                        'logged_in': {
                            '$sum': {'$cond': [{'$eq': ['$status', 'logged_in']}, 1, 0]}
                        },
                        'logged_out': {
                            '$sum': {'$cond': [{'$eq': ['$status', 'logged_out']}, 1, 0]}
                        }
                    }
                },
                {'$sort': {'_id': 1}}
            ]
            
            summary = list(self.db.attendance_records.aggregate(pipeline))
            
            # Convert ObjectId to string for JSON serialization
            for record in summary:
                record['_id'] = str(record['_id'])
            
            return summary
        except Exception as e:
            print(f"Error getting attendance summary: {e}")
            return []
    
    def get_current_status(self, date=None):
        """Get current login status of all employees"""
        try:
            if not date:
                date = datetime.now(Config.TIMEZONE).strftime('%Y-%m-%d')
            
            records = list(self.db.attendance_records.find({
                'date': date,
                'status': 'logged_in'
            }))
            
            # Convert ObjectId to string for JSON serialization
            for record in records:
                record['_id'] = str(record['_id'])
                if record.get('login_time'):
                    record['login_time'] = record['login_time'].isoformat()
                if record.get('created_at'):
                    record['created_at'] = record['created_at'].isoformat()
                if record.get('updated_at'):
                    record['updated_at'] = record['updated_at'].isoformat()
            
            return records
        except Exception as e:
            print(f"Error getting current status: {e}")
            return []
    
    def update_attendance_record(self, record_id, data):
        """Update attendance record (HR manual edit)"""
        try:
            # Convert string ID to ObjectId
            obj_id = ObjectId(record_id)
            
            update_data = {
                'updated_at': datetime.utcnow(),
                'manually_edited': True
            }
            
            # Add fields to update
            if 'login_time' in data:
                update_data['login_time'] = datetime.fromisoformat(data['login_time'])
            if 'logout_time' in data:
                update_data['logout_time'] = datetime.fromisoformat(data['logout_time'])
            if 'duration' in data:
                update_data['duration'] = data['duration']
            if 'status' in data:
                update_data['status'] = data['status']
            
            result = self.db.attendance_records.update_one(
                {'_id': obj_id},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating attendance record: {e}")
            return False