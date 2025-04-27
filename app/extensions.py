# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_moment import Moment
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask
from datetime import datetime
import threading
import logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
moment = Moment()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Configure login
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

# Monitoring system
class ApplicationMonitor:
    """Monitor application performance and health"""
    
    def __init__(self, app=None):
        self.app = app
        self.stats = {
            'requests': {
                'total': 0,
                'by_endpoint': {},
                'by_method': {},
                'by_status': {},
            },
            'response_times': [],
            'errors': [],
            'last_reset': datetime.now().isoformat()
        }
        self.stats_lock = threading.Lock()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the monitor with the Flask app"""
        self.app = app
        app.logger.info("Application monitoring initialized")

    def record_request(self, endpoint, method, status_code, duration):
        """Record a request for monitoring"""
        with self.stats_lock:
            self.stats['requests']['total'] += 1
            
            # By endpoint
            if endpoint not in self.stats['requests']['by_endpoint']:
                self.stats['requests']['by_endpoint'][endpoint] = 0
            self.stats['requests']['by_endpoint'][endpoint] += 1
            
            # By method
            if method not in self.stats['requests']['by_method']:
                self.stats['requests']['by_method'][method] = 0
            self.stats['requests']['by_method'][method] += 1
            
            # By status
            status_str = str(status_code)
            if status_str not in self.stats['requests']['by_status']:
                self.stats['requests']['by_status'][status_str] = 0
            self.stats['requests']['by_status'][status_str] += 1
            
            # Response times (keep last 1000)
            self.stats['response_times'].append({
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'duration': duration,
                'method': method,
                'status': status_code
            })
            if len(self.stats['response_times']) > 1000:
                self.stats['response_times'] = self.stats['response_times'][-1000:]

    def record_error(self, error, endpoint, method, path):
        """Record an error for monitoring"""
        with self.stats_lock:
            self.stats['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'type': error.__class__.__name__,
                'description': str(error),
                'endpoint': endpoint,
                'method': method,
                'path': path
            })
            # Keep last 100 errors
            if len(self.stats['errors']) > 100:
                self.stats['errors'] = self.stats['errors'][-100:]

    def get_stats(self):
        """Get a copy of current statistics"""
        with self.stats_lock:
            import copy
            return copy.deepcopy(self.stats)

    def reset_stats(self):
        """Reset all statistics"""
        with self.stats_lock:
            self.stats = {
                'requests': {
                    'total': 0,
                    'by_endpoint': {},
                    'by_method': {},
                    'by_status': {},
                },
                'response_times': [],
                'errors': [],
                'last_reset': datetime.now().isoformat()
            }
            return {'success': True, 'timestamp': self.stats['last_reset']}

# Initialize monitor
monitor = ApplicationMonitor()

# Task scheduler for background tasks
from app.utils.scheduler import TaskScheduler
scheduler = TaskScheduler()
