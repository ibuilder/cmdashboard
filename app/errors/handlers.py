from flask import Blueprint, render_template, current_app, request
import traceback

error_bp = Blueprint('errors', __name__)

@error_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@error_bp.app_errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@error_bp.app_errorhandler(500)
def internal_error(error):
    # Log the error
    current_app.logger.error(f"Server Error: {str(error)}")
    current_app.logger.error(traceback.format_exc())
    
    return render_template('errors/500.html'), 500

@error_bp.app_errorhandler(Exception)
def handle_unexpected_error(error):
    current_app.logger.error(f"Unhandled Exception: {str(error)}")
    current_app.logger.error(traceback.format_exc())
    
    return render_template('errors/500.html'), 500