-- Employee Attendance System - MySQL Database Schema
-- Run this script to create the database structure

-- Create database (if needed)
CREATE DATABASE IF NOT EXISTS employee_attendance;
USE employee_attendance;

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL UNIQUE,
    employee_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    telegram_id BIGINT UNIQUE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_employee_id (employee_id),
    INDEX idx_phone_number (phone_number),
    INDEX idx_telegram_id (telegram_id),
    INDEX idx_status (status)
);

-- Create attendance_records table
CREATE TABLE IF NOT EXISTS attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    employee_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    telegram_id BIGINT NOT NULL,
    date DATE NOT NULL,
    login_time DATETIME NULL,
    logout_time DATETIME NULL,
    duration VARCHAR(20) NULL,
    duration_seconds INT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'logged_in',
    is_grace_applied BOOLEAN NOT NULL DEFAULT FALSE,
    original_timestamp DATETIME NULL,
    manually_edited BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    INDEX idx_employee_date (employee_id, date),
    INDEX idx_telegram_date (telegram_id, date),
    INDEX idx_date_status (date, status),
    INDEX idx_date (date),
    INDEX idx_status (status)
);

-- Sample data (optional - remove if not needed)
-- INSERT INTO employees (employee_id, employee_name, phone_number) VALUES
-- ('EMP001', 'John Doe', '+1234567890'),
-- ('EMP002', 'Jane Smith', '+0987654321'),
-- ('EMP003', 'Bob Johnson', '+1122334455');

-- Show tables
SHOW TABLES;

-- Show table structures
DESCRIBE employees;
DESCRIBE attendance_records;