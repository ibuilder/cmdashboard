# app/config.py
import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    # Load from environment or use default
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    
    # Session security settings
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)  # Limit session lifetime
    SESSION_COOKIE_SECURE = os.environ.get('SECURE_COOKIES', 'False').lower() == 'true'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 1800)),
    }
    
    # Upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or \
        os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar'}
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Web3 settings for blockchain integration
    WEB3_PROVIDER_URL = os.environ.get('WEB3_PROVIDER_URL') or 'http://127.0.0.1:8545'
    WEB3_ACCOUNT_ADDRESS = os.environ.get('WEB3_ACCOUNT_ADDRESS')
    WEB3_PRIVATE_KEY = os.environ.get('WEB3_PRIVATE_KEY')
    
    # Push notification service
    PUSH_SERVICE_URL = os.environ.get('PUSH_SERVICE_URL')
    PUSH_API_KEY = os.environ.get('PUSH_API_KEY')
    
    # Mobile API settings
    MOBILE_API_ENABLED = True
    MOBILE_SYNC_MAX_DAYS = 30  # Maximum days of history for mobile sync
    MOBILE_UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10MB max upload for mobile
    MOBILE_API_VERSION = '1.0.0'
    
    # Application settings
    COMPANY_NAME = os.environ.get('COMPANY_NAME') or 'Construction Dashboard'
    ITEMS_PER_PAGE = 20
    JWT_TOKEN_EXPIRATION = timedelta(hours=1)
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    
    # Security settings
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('SECURE_COOKIES', 'False').lower() == 'true'
    REMEMBER_COOKIE_SECURE = os.environ.get('SECURE_COOKIES', 'False').lower() == 'true'
    
    # Monitoring and performance settings
    SLOW_REQUEST_THRESHOLD = float(os.environ.get('SLOW_REQUEST_THRESHOLD', 0.5))  # seconds
    ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY')
    MONITORING_ENABLED = os.environ.get('MONITORING_ENABLED', 'True').lower() == 'true'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # IP restrictions for admin access (comma-separated list)
    ADMIN_IP_ALLOWLIST = os.environ.get('ADMIN_IP_ALLOWLIST', '').split(',') if os.environ.get('ADMIN_IP_ALLOWLIST') else []
    
    # Rate limiting settings
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day, 50 per hour')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_STRATEGY = os.environ.get('RATELIMIT_STRATEGY', 'fixed-window')
    
    # Caching settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')  # Options: simple, redis, filesystem
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_DIR = os.environ.get('CACHE_DIR', '/tmp/flask_cache')
    
    # Caching timeouts for specific types of data (in seconds)
    CACHE_TIMEOUTS = {
        'project_list': 3600,         # 1 hour
        'project_details': 1800,      # 30 minutes
        'user_preferences': 86400,    # 24 hours
        'static_data': 604800,        # 1 week
        'dashboard': 300,             # 5 minutes
        'reports': 1800,              # 30 minutes
    }
    
    # Scheduled tasks
    SCHEDULER_ENABLED = os.environ.get('SCHEDULER_ENABLED', 'True').lower() == 'true'
    
    # Backup settings
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'True').lower() == 'true'
    BACKUP_TIME = os.environ.get('BACKUP_TIME', '02:00')  # Daily backup time (24h format)
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 7))
    BACKUP_S3_BUCKET = os.environ.get('BACKUP_S3_BUCKET')
    
    # AWS settings for backups and storage
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    
    # Content Security Policy
    CSP_SETTINGS = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", "data:", "blob:"],
        'font-src': ["'self'", "data:"],
        'connect-src': ["'self'"],
        'frame-ancestors': ["'self'"],
        'form-action': ["'self'"],
    }
    
    # Feature flags
    FEATURE_FLAGS = {
        'enable_blockchain': os.environ.get('FEATURE_BLOCKCHAIN', 'False').lower() == 'true',
        'enable_mobile_sync': os.environ.get('FEATURE_MOBILE_SYNC', 'True').lower() == 'true',
        'enable_push_notifications': os.environ.get('FEATURE_PUSH_NOTIFICATIONS', 'True').lower() == 'true',
        'enable_weather_api': os.environ.get('FEATURE_WEATHER_API', 'True').lower() == 'true',
        'enable_analytics': os.environ.get('FEATURE_ANALYTICS', 'True').lower() == 'true',
        'show_cost_module': os.environ.get('FEATURE_COST_MODULE', 'True').lower() == 'true',
        'show_safety_module': os.environ.get('FEATURE_SAFETY_MODULE', 'True').lower() == 'true',
        'show_rfis_module': os.environ.get('FEATURE_RFIS_MODULE', 'True').lower() == 'true',
        'show_submittals_module': os.environ.get('FEATURE_SUBMITTALS_MODULE', 'True').lower() == 'true',
        'enable_file_versioning': os.environ.get('FEATURE_FILE_VERSIONING', 'False').lower() == 'true',
    }
    
    # Weather API settings
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    WEATHER_API_URL = os.environ.get('WEATHER_API_URL', 'https://api.openweathermap.org/data/2.5')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    
    # Less secure settings for development
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    
    # Simplified cache for development
    CACHE_TYPE = 'simple'
    
    # Enable all features in development
    FEATURE_FLAGS = {k: True for k in Config.FEATURE_FLAGS}
    
    # More verbose logging in dev mode
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False
    
    # Disable scheduled tasks in tests
    SCHEDULER_ENABLED = False
    
    # Disable external services in tests
    MAIL_SUPPRESS_SEND = True
    
    # Test-specific settings
    SERVER_NAME = 'localhost'
    
    # Clean feature flags for testing
    FEATURE_FLAGS = {k: False for k in Config.FEATURE_FLAGS}
    FEATURE_FLAGS['enable_mobile_sync'] = True  # Enable only what we test


class ProductionConfig(Config):
    """Production configuration"""
    # Override with better secret key
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Enable secure cookies in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Stricter security settings
    ADMIN_IP_ALLOWLIST = os.environ.get('ADMIN_IP_ALLOWLIST', '').split(',')
    
    # Use Redis cache in production
    CACHE_TYPE = 'redis'
    
    # Better rate limiting storage
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
    
    # Stricter CSP settings for production
    CSP_SETTINGS = {
        'default-src': ["'self'"],
        'script-src': ["'self'"],  # No unsafe-inline in production
        'style-src': ["'self'"],   # No unsafe-inline in production
        'img-src': ["'self'", "data:"],
        'font-src': ["'self'", "data:"],
        'connect-src': ["'self'"],
        'frame-ancestors': ["'none'"],  # Prevents clickjacking
        'form-action': ["'self'"],
        'base-uri': ["'self'"],
        'object-src': ["'none'"],
        'upgrade-insecure-requests': [],
    }
    
    # Production error handling
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'ERROR')  # Default to ERROR in production
    
    # Database engine options for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 1800)),  # Recycle connections after 30 min
        'pool_pre_ping': True,  # Enable connection verification before use
    }

