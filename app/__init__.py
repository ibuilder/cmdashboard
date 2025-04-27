# app/__init__.py
from flask import Flask, request, g, jsonify
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf, mail, moment, cache, limiter, monitor, scheduler
from app.utils.security import configure_security
import os
import logging
from logging.handlers import RotatingFileHandler
import time
from sqlalchemy import text
from datetime import datetime, timedelta
from app.models import *
# Define Swagger URL constant
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
from markupsafe import Markup
def configure_jinja_filters(app):
    """Configure custom Jinja2 filters for the application."""
    
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks."""
        if not text:
            return ""
        # Convert newlines to HTML line breaks
        text = text.replace('\n', Markup('<br>'))
        return Markup(text)

def create_app(config_class=None):
    if config_class is None:
        from app.config_factory import get_config
        config_class = get_config()
        
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    
    # Configure caching
    cache_config = {
        'CACHE_TYPE': 'simple',  # Use FileSystemCache or RedisCache in production
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    app.config.from_mapping(cache_config)
    cache.init_app(app)
    
    # Initialize rate limiting
    limiter.init_app(app)
    
    # Initialize monitoring
    monitor.init_app(app)
    
    # Initialize task scheduler
    scheduler.init_app(app)
    
    # Configure security middleware
    configure_security(app)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register middleware functions
    register_middleware(app)
    
    # Register blueprints in an organized way
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create context processor to make global variables available in templates
    register_context_processors(app)
    
    # Configure logging
    from app.utils.logger import configure_logging
    configure_logging(app)
    
    # Register shell context processor
    register_shell_context(app)
    
    # Run startup tasks
    run_startup_tasks(app)
    configure_jinja_filters(app)
    return app

def register_middleware(app):
    """Register middleware functions"""
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = generate_request_id()
    
    @app.after_request
    def after_request(response):
        # Calculate request duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Log slow requests
            if duration > app.config.get('SLOW_REQUEST_THRESHOLD', 0.5):
                app.logger.warning(f"Slow request: {request.method} {request.path} - {duration:.4f}s")
            
            # Record in monitoring
            endpoint = request.endpoint or 'unknown'
            monitor.record_request(endpoint, request.method, response.status_code, duration)
            
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    # Register error tracking
    @app.errorhandler(Exception)
    def handle_exception(e):
        monitor.record_error(e, request.endpoint, request.method, request.path)
        # Continue with normal error handling
        raise e

def register_blueprints(app):
    """Register all application blueprints in an organized way"""
    
    # Core blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.projects.routes import projects_bp
    from app.admin.routes import admin_bp
    from app.api.routes import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp) 
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # API Documentation
    from app.api.swagger import swagger_bp, swagger_ui_bp
    app.register_blueprint(swagger_bp, url_prefix='/api')
    app.register_blueprint(swagger_ui_bp, url_prefix=SWAGGER_URL)
    
    # Project section blueprints
    register_project_blueprints(app)

def register_project_blueprints(app):
    """Register all project-related module blueprints"""
    
    # First, register the main projects blueprint
    from app.projects.routes import projects_bp
    app.register_blueprint(projects_bp, url_prefix='/projects')
    
    # Then register the module blueprints with unique names
    from app.projects.overview.routes import overview_bp
    app.register_blueprint(overview_bp, url_prefix='/projects', name='projects_overview')
    
    from app.projects.engineering.routes import engineering_bp
    app.register_blueprint(engineering_bp, url_prefix='/projects', name='projects_engineering')
    
    from app.projects.field.routes import field_bp
    app.register_blueprint(field_bp, url_prefix='/projects', name='projects_field')
    
    from app.projects.safety.routes import safety_bp
    app.register_blueprint(safety_bp, url_prefix='/projects', name='projects_safety')
    
    from app.projects.contracts.routes import contracts_bp
    app.register_blueprint(contracts_bp, url_prefix='/projects', name='projects_contracts')
    
    from app.projects.cost.routes import cost_bp
    app.register_blueprint(cost_bp, url_prefix='/projects', name='projects_cost')
    
    from app.projects.bim.routes import bim_bp
    app.register_blueprint(bim_bp, url_prefix='/projects', name='projects_bim')
    
    from app.projects.closeout.routes import closeout_bp
    app.register_blueprint(closeout_bp, url_prefix='/projects', name='projects_closeout')
    
    # Add preconstruction blueprint with the correct name
    from app.projects.preconstruction.routes import preconstruction_bp
    app.register_blueprint(preconstruction_bp, url_prefix='/projects', name='projects_preconstruction')
    
    # Additional blueprint
    
    
    from app.projects.reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix='/projects', name='projects_reports')
    
    from app.projects.settings import settings_bp
    app.register_blueprint(settings_bp, url_prefix='/projects', name='projects_settings')
    
def register_context_processors(app):
    """Register context processors"""
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {
            'current_year': datetime.now().year,
            'app_name': app.config.get('COMPANY_NAME', 'Construction Dashboard'),
            'app_version': '1.0.0',
            'is_debug': app.debug
        }
    
    # Add utility context processor
    @app.context_processor
    def utility_processor():
        def format_currency(value):
            return "${:,.2f}".format(value) if value else "$0.00"
        
        def format_date(value, format='%m/%d/%Y'):
            if not value:
                return ""
            return value.strftime(format)
            
        def format_filesize(bytes):
            """Convert bytes to human-readable form"""
            if not bytes:
                return "0B"
            units = ['B', 'KB', 'MB', 'GB']
            i = 0
            while bytes >= 1024 and i < len(units) - 1:
                bytes /= 1024
                i += 1
            return f"{bytes:.2f} {units[i]}"
        
        def get_nav_modules():
            """Get all modules for navigation"""
            modules = [
                {'name': 'Overview', 'url': 'projects_overview.index', 'icon': 'home'},
                {'name': 'Preconstruction', 'url': 'projects.preconstruction.index', 'icon': 'clipboard'},
                {'name': 'Engineering', 'url': 'projects.engineering.index', 'icon': 'drafting-compass'},
                {'name': 'Field', 'url': 'projects.field.index', 'icon': 'hard-hat'},
                {'name': 'Safety', 'url': 'projects.safety.index', 'icon': 'shield-alt'},
                {'name': 'Contracts', 'url': 'projects.contracts.index', 'icon': 'file-contract'},
                {'name': 'Cost', 'url': 'projects.cost.index', 'icon': 'dollar-sign'},
                {'name': 'BIM', 'url': 'projects.bim.index', 'icon': 'cubes'},
                {'name': 'Closeout', 'url': 'projects.closeout.index', 'icon': 'check-circle'},
                {'name': 'Resources', 'url': 'projects.resources.index', 'icon': 'folder-open'},
                {'name': 'Reports', 'url': 'projects.reports.index', 'icon': 'chart-bar'},
                {'name': 'Settings', 'url': 'projects.settings.index', 'icon': 'cog'}
            ]
            return modules
            
        return dict(
            format_currency=format_currency,
            format_date=format_date,
            format_filesize=format_filesize,
            get_nav_modules=get_nav_modules
        )

def register_error_handlers(app):
    """Register error handlers"""
    from app.utils.error_handlers import (
        handle_400_error,
        handle_403_error,
        handle_404_error,
        handle_500_error
    )
    
    app.register_error_handler(400, handle_400_error)
    app.register_error_handler(403, handle_403_error)
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)
def generate_request_id():
    """Generate a unique ID for the current request"""
    import uuid
    return str(uuid.uuid4())

def register_shell_context(app):
    """Register shell context objects"""
    @app.shell_context_processor
    def make_shell_context():
        
        
        
        return {
            'db': db,
            'User': User,
            'Project': Project,
            'Comment': Comment,
            'Attachment': Attachment,
            'RFI': RFI,
            'Submittal': Submittal,
            'DailyReport': DailyReport,
            'SafetyObservation': SafetyObservation,
            'IncidentReport': IncidentReport,
            'Budget': Budget,
            'ChangeOrder': ChangeOrder,
            'Invoice': Invoice
        }

def check_db_connection():
    """Check database connection"""
    try:
        result = db.session.execute('SELECT 1').scalar()
        return result == 1
    except Exception as e:
        current_app.logger.error(f"Database connection failed: {str(e)}")
        return False

def exempt_csrf_for_api_routes(app):
    """Exempt API routes from CSRF protection"""
    # Updated approach for newer Flask-WTF versions
    @csrf.exempt
    def csrf_exempt_api():
        if request.path.startswith('/api/'):
            return True
        return False

def clean_temp_files(app):
    """
    Clean temporary files
    
    :param app: Flask application context
    """
    try:
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        if os.path.exists(temp_dir):
            import shutil
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    app.logger.error(f'Failed to delete {file_path}. Reason: {e}')
    except Exception as e:
        app.logger.error(f"Error in temp file cleanup: {e}")

def collect_db_stats(app):
    """
    Collect database statistics
    
    :param app: Flask application context
    """
    try:
        with app.app_context():
            # Calculate the timestamp for 24 hours ago
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            
            # Use SQLAlchemy's text() for database-agnostic query
            active_users = db.session.execute(
                text("SELECT COUNT(*) FROM users WHERE last_seen > :cutoff"),
                {'cutoff': twenty_four_hours_ago}
            ).scalar()
            
            app.logger.info(f"Daily active users: {active_users}")
    except Exception as e:
        app.logger.error(f"Error collecting DB stats: {str(e)}")

def run_startup_tasks(app):
    """Run tasks at application startup"""
    with app.app_context():
        # Check and create required database tables
        if app.config.get('AUTO_MIGRATE', False):
            try:
                db.create_all()
                app.logger.info('Database tables created')
            except Exception as e:
                app.logger.error(f'Error creating database tables: {e}')
        
        # Check and create required directories
        required_dirs = [
            os.path.join(app.config['UPLOAD_FOLDER'], 'documents'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'photos'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'temp'),
            'logs'
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                app.logger.info(f'Created directory: {directory}')
        
        # Check feature flags
        try:
            from app.utils.feature_flags import load_feature_flags
            load_feature_flags()
            app.logger.info('Feature flags loaded')
        except ImportError:
            app.logger.info('Feature flags module not found, skipping')
        
        # Use threading for background tasks
        import threading
        
        # Cleanup task
        def periodic_cleanup():
            while True:
                try:
                    with app.app_context():
                        clean_temp_files(app)
                except Exception as e:
                    app.logger.error(f"Error in periodic cleanup: {e}")
                
                # Sleep for 24 hours
                import time
                time.sleep(24 * 60 * 60)
        
        # DB stats collection task
        def periodic_db_stats():
            while True:
                try:
                    with app.app_context():
                        collect_db_stats(app)
                except Exception as e:
                    app.logger.error(f"Error in periodic DB stats: {e}")
                
                # Sleep for 6 hours
                import time
                time.sleep(6 * 60 * 60)
        
        # Start background threads
        if not app.testing:
            cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
            db_stats_thread = threading.Thread(target=periodic_db_stats, daemon=True)
            
            cleanup_thread.start()
            db_stats_thread.start()
    
    return app

