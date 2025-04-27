from flask import Flask, request, g, current_app
from app.extensions import db, migrate, login_manager, csrf, mail, moment, cache, limiter, app_monitor
from app.utils.security import configure_security
import os
import logging
import time
from sqlalchemy import text, inspect
from datetime import datetime, timedelta
from app.models import *
from markupsafe import Markup
import uuid


# Define Swagger URL constant for API documentation
SWAGGER_URL = '/api/docs'


def configure_jinja_filters(app: Flask) -> None:
    """
    Configures custom Jinja2 filters for the application.

    Args:
        app (Flask): The Flask application instance.
    """

    @app.template_filter('nl2br')
    def nl2br_filter(text: str) -> Markup:
        """Converts newlines to HTML line breaks."""
        if not text:
            return ""
        text = text.replace('\n', Markup('<br>'))
        return Markup(text)


def create_app(config_class=None) -> Flask:
    """Creates and configures the Flask application."""
    if config_class is None:
        from app.config_factory import get_config
        config_class = get_config()
        
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(config_class) # Load configuration from config object

    # Initialize Flask extensions with the application
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    # Configure caching with a default timeout
    cache_config = {
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300
    }
    app.config.from_mapping(cache_config)
    cache.init_app(app)

    
    # Initialize rate limiting to prevent abuse
    # Configure logging for uncaught errors
    if not app.debug:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler('logs/app_errors.log')  # Replace with your log file path
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
    limiter.init_app(app)

    # Initialize application monitoring for tracking performance and errors
    app_monitor.init_app(app)

    # Configure security settings and middleware
    configure_security(app)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register before and after request middleware functions
    register_middleware(app)

    # Register application blueprints to structure the app
    register_blueprints(app)

    # Register error handling for different error codes
    register_error_handlers(app)

    # Register context processors to add common data to Jinja2 templates
    register_context_processors(app)

    # Configure logging to record application activities using a utility function
    from app.utils.logger import configure_logging
    configure_logging(app)

    # Register shell context processor for Flask shell access
    register_shell_context(app)

    # Run startup tasks like database and directory setup
    run_startup_tasks(app)

    # Configures Jinja Filters
    configure_jinja_filters(app)
    return app


def register_middleware(app: Flask) -> None:
    """
    Registers request middleware functions.

    Args:
        app (Flask): The Flask application instance.
    """
    @app.before_request
    def before_request():
        app.logger.info(f"Request: {request.method} {request.path}")
        g.start_time = time.time()
        g.request_id = generate_request_id()
    
    @app.after_request
    def after_request(response):
        # Calculate request duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Log slow requests if they exceed a threshold
            if duration > app.config.get('SLOW_REQUEST_THRESHOLD', 0.5):
                app.logger.warning(f"Slow request: {request.method} {request.path} - {duration:.4f}s")
            
            # Record request in monitoring
            endpoint = request.endpoint or 'unknown'
            app_monitor.record_request(endpoint, request.method, response.status_code, duration)
            
        # Add security headers to enhance security
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'  # Enable XSS protection in browsers
        
        return response
    
    # Register error tracking
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        app_monitor.record_error(e, request.endpoint, request.method, request.path)
        # Continue with normal error handling
        raise e


def register_blueprints(app: Flask) -> None:
    """
    Registers all application blueprints in an organized way.

    Args:
        app (Flask): The Flask application instance.
    """
    # Import blueprints for core parts of the application
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.projects.routes import projects_bp
    from app.admin.routes import admin_bp
    from app.api.routes import api_bp
    
    # Register blueprints with appropriate URL prefixes
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


from app.projects import *


def register_project_blueprints(app: Flask) -> None:
    """
    Registers all project-related module blueprints.

    Args:
        app (Flask): The Flask application instance.
    """
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


def register_context_processors(app: Flask) -> None:
    """
    Registers context processors to make common data available to Jinja2 templates.

    Args:
        app (Flask): The Flask application instance.
    """
    @app.context_processor # Make these functions available in Jinja2 templates
    def inject_globals():
        from datetime import datetime
        return {
            'current_year': datetime.now().year,
            'app_name': app.config.get('COMPANY_NAME', 'Construction Dashboard'),
            'app_version': '1.0.0',
            'is_debug': app.debug
        } # Inject global variables into templates

    
    """Adds utility functions to the template context."""
    
    
    # Add utility context processor to format common types of data
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

def register_error_handlers(app: Flask) -> None:
    """
    Registers custom error handlers for the application.

    Args:
        app (Flask): The Flask application instance.
    """
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
    """
    Generates a unique ID for the current request.
    
    Returns:
        str: A unique UUID string.
    """
    return str(uuid.uuid4())


def register_shell_context(app: Flask) -> None:
    """
    Registers objects to be available in the Flask shell.

    Args:
        app (Flask): The Flask application instance.
    """
    @app.shell_context_processor
    def make_shell_context():
        """Exposes database and models to the Flask shell."""

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


def check_db_connection() -> bool:
    """
    Checks the database connection.
    
    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        result = db.session.execute(text('SELECT 1')).scalar()
        return result == 1
    except Exception as e:
        current_app.logger.error(f"Database connection failed: {str(e)}")
        return False


def exempt_csrf_for_api_routes(app: Flask) -> None:
    """
    Exempts API routes from CSRF protection.
    
    Args:
        app (Flask): The Flask application instance.
    """
    # Exclude API routes from CSRF protection
    @csrf.exempt
    def csrf_exempt_api(): # Skip CSRF for any route that begins with /api/
        """Check if the current route should be exempted from CSRF."""
        if request.path.startswith('/api/'):
            return True
        return False

def clean_temp_files(app):
    """
    Clean temporary files
    Removes temporary files and directories from the upload folder.

    Args:
        app (Flask): The Flask application instance.
    """
    try:
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
    Collects and logs statistics about the database.
    - Collects statistics for active users
    
    Args:
        app (Flask): The Flask application instance.
    
    Returns:
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
    """
    Run tasks at application startup
    Performs various setup tasks, such as creating database tables, directories, and loading feature flags.

    Args:
        app (Flask): The Flask application instance.
    """
    with app.app_context():  # Use an app context for database operations
        # Check and create required database tables
        if app.config.get('AUTO_MIGRATE', False):
            try:
                db.create_all()
                app.logger.info('Database tables created or already existed')
            except Exception as e:
                app.logger.error(f'Error creating or accessing database tables: {e}')
        
        # Check and create required directories for uploads and logs
        required_dirs = [
            os.path.join(app.config['UPLOAD_FOLDER'], 'documents'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'photos'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'temp'),
            'logs'
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                app.logger.info(f'Created directory: {directory}')  # Log directory creation
        
        # Check and load feature flags if module exists
        try:
            from app.utils.feature_flags import load_feature_flags
            load_feature_flags()
            app.logger.info('Feature flags loaded')  # Log flag loading
        except ImportError as e:
            app.logger.info('Feature flags module not found, skipping') # Log flag skipping
        
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

app: Flask = create_app()
