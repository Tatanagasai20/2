from models.database import db, AttendanceRecord, Employee
from datetime import datetime, timedelta
import pytz
from config import Config
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, or_

class AttendanceModel:
    def __init__(self):
        pass
    
    def record_attendance(self, data):
        """Record login/logout attendance"""
        try:
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            ist_timestamp = timestamp.astimezone(Config.TIMEZONE)
            date_obj = ist_timestamp.date()
            
            if data['action'] == 'login':
                return self._handle_login(data, ist_timestamp, date_obj)
            elif data['action'] == 'logout':
                return self._handle_logout(data, ist_timestamp, date_obj)
        except Exception as e:
            print(f"Error recording attendance: {e}")
            return None
    
    def _handle_login(self, data, timestamp, date_obj):
        """Handle login record"""
        try:
            # Check if already logged in today
            existing_record = AttendanceRecord.query.filter_by(
                telegram_id=data['telegram_id'],
                date=date_obj,
                status='logged_in'
            ).first()
            
            if existing_record:
                return {"error": "Already logged in today"}
            
            # Create new attendance record
            record = AttendanceRecord(
                employee_id=data.get('employee_id'),
                employee_name=data['employee_name'],
                phone_number=data.get('phone_number'),
                telegram_id=data['telegram_id'],
                date=date_obj,
                login_time=timestamp,
                logout_time=None,
                duration=None,
                status='logged_in',
                is_grace_applied=data.get('is_grace_applied', False),
                original_timestamp=datetime.fromisoformat(data.get('original_timestamp', data['timestamp']).replace('Z', '+00:00'))
            )
            
            db.session.add(record)
            db.session.commit()
            return {"success": True, "record_id": record.id}
        except Exception as e:
            db.session.rollback()
            print(f"Error in login: {e}")
            return {"error": str(e)}
    
    def _handle_logout(self, data, timestamp, date_obj):
        """Handle logout record"""
        try:
            # Find active login record for today
            login_record = AttendanceRecord.query.filter_by(
                telegram_id=data['telegram_id'],
                date=date_obj,
                status='logged_in'
            ).first()
            
            if not login_record:
                return {"error": "No active login found for today"}
            
            # Calculate duration
            login_time = login_record.login_time
            if login_time.tzinfo is None:
                login_time = Config.TIMEZONE.localize(login_time)
            
            duration = timestamp - login_time
            duration_str = self._format_duration(duration)
            
            # Update record with logout information
            login_record.logout_time = timestamp
            login_record.duration = duration_str
            login_record.duration_seconds = int(duration.total_seconds())
            login_record.status = 'logged_out'
            login_record.updated_at = datetime.utcnow()
            
            db.session.commit()
            return {"success": True, "duration": duration_str}
        except Exception as e:
            db.session.rollback()
            print(f"Error in logout: {e}")
            return {"error": str(e)}
    
    def _format_duration(self, duration):
        """Format duration to readable string"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def get_daily_attendance(self, date=None):
        """Get attendance records for a specific date"""
        try:
            if date is None:
                date_obj = datetime.now(Config.TIMEZONE).date()
            else:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            
            records = AttendanceRecord.query.filter_by(date=date_obj).order_by(AttendanceRecord.login_time).all()
            return [record.to_dict() for record in records]
        except Exception as e:
            print(f"Error getting daily attendance: {e}")
            return []
    
    def get_employee_attendance(self, employee_identifier, start_date=None, end_date=None):
        """Get attendance records for a specific employee (by ID or phone number)"""
        try:
            # Build query for employee_id or phone_number
            query = AttendanceRecord.query.filter(
                or_(
                    AttendanceRecord.employee_id == employee_identifier,
                    AttendanceRecord.phone_number == employee_identifier
                )
            )
            
            # Add date range filter if provided
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(
                    and_(
                        AttendanceRecord.date >= start_date_obj,
                        AttendanceRecord.date <= end_date_obj
                    )
                )
            
            records = query.order_by(AttendanceRecord.date.desc()).all()
            return [record.to_dict() for record in records]
        except Exception as e:
            print(f"Error getting employee attendance: {e}")
            return []
    
    def update_attendance_record(self, record_id, updates):
        """Update attendance record (for HR manual edits)"""
        try:
            record = AttendanceRecord.query.get(record_id)
            if not record:
                return False
            
            # Convert time strings back to datetime objects if needed
            if 'login_time' in updates:
                updates['login_time'] = datetime.fromisoformat(updates['login_time'])
            if 'logout_time' in updates:
                updates['logout_time'] = datetime.fromisoformat(updates['logout_time'])
            
            # Recalculate duration if both times are present
            if 'login_time' in updates and 'logout_time' in updates:
                duration = updates['logout_time'] - updates['login_time']
                updates['duration'] = self._format_duration(duration)
                updates['duration_seconds'] = int(duration.total_seconds())
            
            # Update record fields
            for key, value in updates.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            record.updated_at = datetime.utcnow()
            record.manually_edited = True
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating record: {e}")
            return False
    
    def get_attendance_summary(self, start_date=None, end_date=None):
        """Get attendance summary with statistics"""
        try:
            query = db.session.query(
                AttendanceRecord.employee_id,
                func.max(AttendanceRecord.employee_name).label('employee_name'),
                func.max(AttendanceRecord.phone_number).label('phone_number'),
                func.count(AttendanceRecord.id).label('total_days'),
                func.sum(AttendanceRecord.duration_seconds).label('total_seconds'),
                func.sum(func.case((AttendanceRecord.status == 'logged_in', 1), else_=0)).label('logged_in_days'),
                func.sum(func.case((AttendanceRecord.status == 'logged_out', 1), else_=0)).label('completed_days')
            ).group_by(AttendanceRecord.employee_id)
            
            # Add date range filter if provided
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(
                    and_(
                        AttendanceRecord.date >= start_date_obj,
                        AttendanceRecord.date <= end_date_obj
                    )
                )
            
            results = query.all()
            
            summary = []
            for result in results:
                total_hours = (result.total_seconds or 0) / 3600
                hours = int(total_hours)
                minutes = int((total_hours - hours) * 60)
                
                summary.append({
                    '_id': result.employee_id,
                    'employee_name': result.employee_name,
                    'phone_number': result.phone_number,
                    'total_days': result.total_days,
                    'total_hours': result.total_seconds,
                    'total_hours_formatted': f"{hours}h {minutes}m",
                    'logged_in_days': result.logged_in_days,
                    'completed_days': result.completed_days
                })
            
            return summary
        except Exception as e:
            print(f"Error getting attendance summary: {e}")
            return []
    
    def get_current_status(self, date=None):
        """Get current login status of all employees"""
        try:
            if date is None:
                date_obj = datetime.now(Config.TIMEZONE).date()
            else:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Get latest record for each employee for the given date
            subquery = db.session.query(
                AttendanceRecord.employee_id,
                func.max(AttendanceRecord.id).label('max_id')
            ).filter(AttendanceRecord.date == date_obj).group_by(AttendanceRecord.employee_id).subquery()
            
            records = db.session.query(AttendanceRecord).join(
                subquery, AttendanceRecord.id == subquery.c.max_id
            ).all()
            
            return [record.to_dict() for record in records]
        except Exception as e:
            print(f"Error getting current status: {e}")
            return []