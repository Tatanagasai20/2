from flask import Flask
from flask_cors import CORS
from routes.auth import auth_bp
from routes.attendance import attendance_bp
from config import Config
from models.database import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    init_db(app)
    
    with app.app_context():
        db.create_all(checkfirst=True)
    
    # Enable CORS for all routes
    CORS(app, origins=['*'])
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'attendance-backend', 'database': 'mysql'}
    
    @app.route('/')
    def index():
        return {
            'message': 'Employee Attendance System API',
            'version': '1.0.0',
            'database': 'MySQL',
            'endpoints': {
                'auth': '/api/auth/login',
                'attendance': '/api/attendance/',
                'health': '/health'
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    # Bind to all interfaces for Docker deployment
    app.run(host='0.0.0.0', port=5000, debug=True)
