from flask import Blueprint, jsonify, render_template
from flask_swagger_ui import get_swaggerui_blueprint

# Define Swagger routes
swagger_bp = Blueprint('swagger', __name__)

# Register Swagger UI Blueprint
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
API_URL = '/api/swagger.json'  # URL to API definition

swagger_ui_bp = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Construction Dashboard API"
    }
)

@swagger_bp.route('/swagger.json')
def swagger_json():
    """Serve swagger specification"""
    with open('app/api/swagger.json', 'r') as f:
        return jsonify(json.load(f))

@swagger_bp.route('/')
def api_home():
    """API Home page with documentation links"""
    return render_template('api/index.html')