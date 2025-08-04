from flask import Blueprint, request, jsonify
import jwt
from functools import wraps
from models.attendance import AttendanceModel
from config import Config

attendance_bp = Blueprint('attendance', __name__)
attendance_model = AttendanceModel()

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token invalid'}), 401
        
        return f(*args, **kwargs)
    return decorated

@attendance_bp.route('/', methods=['POST'])
def record_attendance():
    """Record attendance from Telegram bot"""
    try:
        data = request.get_json()
        result = attendance_model.record_attendance(data)
        
        if result and result.get('success'):
            return jsonify(result)
        elif result and result.get('error'):
            return jsonify(result), 400
        else:
            return jsonify({'error': 'Failed to record attendance'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/daily', methods=['GET'])
@token_required
def get_daily_attendance():
    """Get daily attendance records"""
    try:
        date = request.args.get('date')  # Format: YYYY-MM-DD
        records = attendance_model.get_daily_attendance(date)
        
        return jsonify({
            'success': True,
            'records': records,
            'date': date or 'today'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/employee/<username>', methods=['GET'])
@token_required
def get_employee_attendance(username):
    """Get attendance records for specific employee"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        records = attendance_model.get_employee_attendance(username, start_date, end_date)
        
        return jsonify({
            'success': True,
            'records': records,
            'employee': username
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/summary', methods=['GET'])
@token_required
def get_attendance_summary():
    """Get attendance summary with statistics"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        summary = attendance_model.get_attendance_summary(start_date, end_date)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/update/<record_id>', methods=['PUT'])
@token_required
def update_attendance(record_id):
    """Update attendance record (HR manual edit)"""
    try:
        data = request.get_json()
        success = attendance_model.update_attendance_record(record_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Record updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update record'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/current-status', methods=['GET'])
@token_required
def get_current_status():
    """Get current login status of all employees"""
    try:
        from datetime import datetime
        today = datetime.now(Config.TIMEZONE).strftime('%Y-%m-%d')
        
        records = attendance_model.get_daily_attendance(today)
        
        # Group by employee and get latest status
        employee_status = {}
        for record in records:
            username = record['employee_username']
            if username not in employee_status:
                employee_status[username] = record
            else:
                # Keep the latest record
                current_time = employee_status[username].get('login_time')
                new_time = record.get('login_time')
                if new_time and (not current_time or new_time > current_time):
                    employee_status[username] = record
        
        return jsonify({
            'success': True,
            'current_status': list(employee_status.values()),
            'date': today
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500