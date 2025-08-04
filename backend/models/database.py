from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from config import Config

db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    employee_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=True, index=True)
    status = db.Column(db.String(20), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    attendance_records = db.relationship('AttendanceRecord', backref='employee', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'phone_number': self.phone_number,
            'telegram_id': self.telegram_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, index=True)
    employee_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    telegram_id = db.Column(db.BigInteger, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    login_time = db.Column(db.DateTime(timezone=True), nullable=True)
    logout_time = db.Column(db.DateTime(timezone=True), nullable=True)
    duration = db.Column(db.String(20), nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='logged_in')  # logged_in, logged_out
    is_grace_applied = db.Column(db.Boolean, default=False, nullable=False)
    original_timestamp = db.Column(db.DateTime(timezone=True), nullable=True)
    manually_edited = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Composite index for efficient queries
    __table_args__ = (
        db.Index('idx_employee_date', 'employee_id', 'date'),
        db.Index('idx_telegram_date', 'telegram_id', 'date'),
        db.Index('idx_date_status', 'date', 'status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'phone_number': self.phone_number,
            'telegram_id': self.telegram_id,
            'date': self.date.isoformat() if self.date else None,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'duration': self.duration,
            'duration_seconds': self.duration_seconds,
            'status': self.status,
            'is_grace_applied': self.is_grace_applied,
            'original_timestamp': self.original_timestamp.isoformat() if self.original_timestamp else None,
            'manually_edited': self.manually_edited,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
def get_db():
    """Get database instance"""
    return db