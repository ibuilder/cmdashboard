from flask import Blueprint
import time
from flask import g
from app.utils import generate_request_id

# Create the blueprint with a unique name
api_bp = Blueprint('api_v1', __name__, url_prefix='/api')

@api_bp.before_request
def before_api_request():
    """Execute before each API request"""
    # Record request start time for performance monitoring
    g.start_time = time.time()
    
    # Generate unique request ID for tracing
    g.request_id = generate_request_id('API')

@api_bp.after_request
def after_api_request(response):
    """Execute after each API request"""
    # Add request ID to response headers
    if hasattr(g, 'request_id'):
        response.headers['X-Request-ID'] = g.request_id
    
    # Add processing time to response headers
    if hasattr(g, 'start_time'):
        process_time = time.time() - g.start_time
        response.headers['X-Process-Time'] = f"{process_time:.4f}s"
    
    # Set CORS headers for API
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
    
    return response

# Import routes after blueprint definition
from app.api import routes