#!/usr/bin/env python3
"""
Configuration file for SolidBeam Solution ClamAV Web Interface
"""

import os
from pathlib import Path

# Application Configuration
APP_NAME = "SolidBeam Solution - ClamAV Web Interface"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Enterprise-grade ClamAV Web Interface with Docker support"

# Flask Configuration
FLASK_HOST = os.environ.get('CLAMAV_WEB_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('CLAMAV_WEB_PORT', 5000))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
FLASK_ENV = os.environ.get('FLASK_ENV', 'production')

# Security Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB

# ClamAV Configuration
CLAMAV_SCAN_TIMEOUT = int(os.environ.get('SCAN_TIMEOUT', 300))  # 5 minutes
CLAMAV_MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB
CLAMAV_QUARANTINE_ENABLED = os.environ.get('QUARANTINE_ENABLED', 'True').lower() == 'true'
CLAMAV_LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Path Configuration
BASE_DIR = Path('/opt/clamav-web')
DATA_DIR = Path(os.environ.get('CLAMAV_DB_PATH', str(BASE_DIR / 'data')))
QUARANTINE_DIR = Path(os.environ.get('CLAMAV_QUARANTINE_PATH', str(BASE_DIR / 'quarantine')))
LOGS_DIR = Path(os.environ.get('CLAMAV_LOGS_PATH', str(BASE_DIR / 'logs')))
UPLOAD_DIR = Path('/tmp/uploads')

# Database Configuration
DATABASE_FILE = DATA_DIR / 'clamav_web.db'
DATABASE_TIMEOUT = 30

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE = LOGS_DIR / 'clamav_web.log'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Scan Configuration
QUICK_SCAN_PATHS = [
    '/tmp',
    '/var/tmp',
    '/home'
]

CUSTOM_SCAN_DEFAULT_PATH = '/tmp'
CUSTOM_SCAN_DEFAULT_RECURSIVE = True

# UI Configuration
METRICS_REFRESH_INTERVAL = 5000  # 5 seconds
HISTORY_DEFAULT_LIMIT = 50
DIAGNOSTICS_TIMEOUT = 30  # seconds

# File Type Restrictions
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg',
    'mp3', 'mp4', 'avi', 'mov', 'wmv',
    'zip', 'rar', '7z', 'tar', 'gz',
    'exe', 'msi', 'dmg', 'deb', 'rpm',
    'py', 'js', 'html', 'css', 'php', 'java', 'cpp', 'c',
    'sh', 'bat', 'ps1', 'vbs'
}

# Virus Database Configuration
VIRUS_DB_UPDATE_INTERVAL = 3600  # 1 hour
VIRUS_DB_UPDATE_ENABLED = True

# Performance Configuration
WORKER_PROCESSES = int(os.environ.get('WORKER_PROCESSES', 1))
WORKER_THREADS = int(os.environ.get('WORKER_THREADS', 4))
WORKER_CONNECTIONS = int(os.environ.get('WORKER_CONNECTIONS', 1000))

# Monitoring Configuration
HEALTH_CHECK_INTERVAL = 30  # seconds
HEALTH_CHECK_TIMEOUT = 10  # seconds
HEALTH_CHECK_RETRIES = 3

# Backup Configuration
BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'True').lower() == 'true'
BACKUP_INTERVAL = int(os.environ.get('BACKUP_INTERVAL', 86400))  # 24 hours
BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 7))

# Email Configuration (for notifications)
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'False').lower() == 'true'
EMAIL_SMTP_SERVER = os.environ.get('EMAIL_SMTP_SERVER', 'localhost')
EMAIL_SMTP_PORT = int(os.environ.get('EMAIL_SMTP_PORT', 587))
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'clamav@localhost')
EMAIL_TO = os.environ.get('EMAIL_TO', '').split(',')

# Notification Configuration
NOTIFY_ON_INFECTION = os.environ.get('NOTIFY_ON_INFECTION', 'True').lower() == 'true'
NOTIFY_ON_SCAN_COMPLETE = os.environ.get('NOTIFY_ON_SCAN_COMPLETE', 'False').lower() == 'true'
NOTIFY_ON_ERROR = os.environ.get('NOTIFY_ON_ERROR', 'True').lower() == 'true'

# API Configuration
API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')
API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 300))  # 5 minutes

# Development Configuration
DEBUG_MODE = FLASK_DEBUG
RELOAD_ON_CHANGE = FLASK_DEBUG
PROFILING_ENABLED = os.environ.get('PROFILING_ENABLED', 'False').lower() == 'true'

# Docker Configuration
DOCKER_MODE = os.environ.get('DOCKER_MODE', 'True').lower() == 'true'
CONTAINER_NAME = os.environ.get('CONTAINER_NAME', 'solidbeam-clamav-web')

# Feature Flags
FEATURE_QUARANTINE = CLAMAV_QUARANTINE_ENABLED
FEATURE_UPLOAD_SCAN = True
FEATURE_CUSTOM_SCAN = True
FEATURE_QUICK_SCAN = True
FEATURE_HISTORY = True
FEATURE_METRICS = True
FEATURE_DIAGNOSTICS = True
FEATURE_BACKUP = BACKUP_ENABLED
FEATURE_NOTIFICATIONS = EMAIL_ENABLED

# Validation Configuration
VALIDATE_PATHS = True
VALIDATE_FILE_TYPES = True
VALIDATE_FILE_SIZE = True
VALIDATE_PERMISSIONS = True

# Error Handling Configuration
RETRY_ATTEMPTS = int(os.environ.get('RETRY_ATTEMPTS', 3))
RETRY_DELAY = int(os.environ.get('RETRY_DELAY', 1))  # seconds
ERROR_LOG_LEVEL = 'ERROR'

# Cache Configuration
CACHE_ENABLED = os.environ.get('CACHE_ENABLED', 'True').lower() == 'true'
CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))  # 5 minutes
CACHE_MAX_SIZE = int(os.environ.get('CACHE_MAX_SIZE', 100))

# Session Configuration
SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))  # 1 hour
SESSION_SECURE = os.environ.get('SESSION_SECURE', 'False').lower() == 'true'
SESSION_HTTPONLY = True

# CORS Configuration
CORS_ENABLED = True
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
CORS_HEADERS = ['Content-Type', 'Authorization']

# SSL/TLS Configuration
SSL_ENABLED = os.environ.get('SSL_ENABLED', 'False').lower() == 'true'
SSL_CERT_FILE = os.environ.get('SSL_CERT_FILE', '')
SSL_KEY_FILE = os.environ.get('SSL_KEY_FILE', '')

# Load Balancing Configuration
LOAD_BALANCER_ENABLED = os.environ.get('LOAD_BALANCER_ENABLED', 'False').lower() == 'true'
LOAD_BALANCER_HEALTH_CHECK_PATH = '/health'
LOAD_BALANCER_HEALTH_CHECK_INTERVAL = 30

# Metrics Configuration
METRICS_ENABLED = True
METRICS_COLLECTION_INTERVAL = 5  # seconds
METRICS_RETENTION_HOURS = 24
METRICS_DISK_USAGE_THRESHOLD = 80  # percentage
METRICS_MEMORY_USAGE_THRESHOLD = 80  # percentage
METRICS_CPU_USAGE_THRESHOLD = 80  # percentage

# Quarantine Configuration
QUARANTINE_MAX_SIZE = int(os.environ.get('QUARANTINE_MAX_SIZE', 10 * 1024 * 1024 * 1024))  # 10GB
QUARANTINE_RETENTION_DAYS = int(os.environ.get('QUARANTINE_RETENTION_DAYS', 30))
QUARANTINE_AUTO_CLEANUP = os.environ.get('QUARANTINE_AUTO_CLEANUP', 'True').lower() == 'true'

# Scan Engine Configuration
SCAN_ENGINE_TIMEOUT = CLAMAV_SCAN_TIMEOUT
SCAN_ENGINE_MAX_FILES = int(os.environ.get('SCAN_ENGINE_MAX_FILES', 10000))
SCAN_ENGINE_MAX_DEPTH = int(os.environ.get('SCAN_ENGINE_MAX_DEPTH', 100))
SCAN_ENGINE_FOLLOW_SYMLINKS = os.environ.get('SCAN_ENGINE_FOLLOW_SYMLINKS', 'False').lower() == 'true'
SCAN_ENGINE_CROSS_FILESYSTEMS = os.environ.get('SCAN_ENGINE_CROSS_FILESYSTEMS', 'False').lower() == 'true'

# Database Migration Configuration
DB_MIGRATION_ENABLED = True
DB_MIGRATION_AUTO = True
DB_MIGRATION_VERSION = '1.0.0'

# API Documentation Configuration
API_DOCS_ENABLED = os.environ.get('API_DOCS_ENABLED', 'True').lower() == 'true'
API_DOCS_PATH = '/api/docs'
API_DOCS_TITLE = f'{APP_NAME} API Documentation'
API_DOCS_VERSION = APP_VERSION

# Webhook Configuration
WEBHOOK_ENABLED = os.environ.get('WEBHOOK_ENABLED', 'False').lower() == 'true'
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
WEBHOOK_EVENTS = ['scan_complete', 'infection_found', 'error_occurred']

# Audit Configuration
AUDIT_ENABLED = os.environ.get('AUDIT_ENABLED', 'True').lower() == 'true'
AUDIT_LOG_FILE = LOGS_DIR / 'audit.log'
AUDIT_RETENTION_DAYS = int(os.environ.get('AUDIT_RETENTION_DAYS', 90))

# Performance Monitoring Configuration
PERFORMANCE_MONITORING_ENABLED = os.environ.get('PERFORMANCE_MONITORING_ENABLED', 'False').lower() == 'true'
PERFORMANCE_MONITORING_INTERVAL = int(os.environ.get('PERFORMANCE_MONITORING_INTERVAL', 60))  # seconds

# Security Headers Configuration
SECURITY_HEADERS_ENABLED = True
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; img-src 'self' data:; font-src 'self' cdnjs.cloudflare.com;"
}