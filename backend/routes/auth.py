from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """HR login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Validate credentials
        if username == Config.HR_USERNAME and password == Config.HR_PASSWORD:
            # Generate JWT token
            token = jwt.encode({
                'username': username,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, Config.JWT_SECRET_KEY, algorithm='HS256')
            
            return jsonify({
                'success': True,
                'token': token,
                'username': username
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed'
        }), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'valid': False}), 401
        
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Decode token
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        
        return jsonify({
            'valid': True,
            'username': payload['username']
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'message': 'Invalid token'}), 401