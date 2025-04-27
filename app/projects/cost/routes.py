from flask import Blueprint

cost_bp = Blueprint('cost', __name__)

@cost_bp.route('/')
def index():
    return "Projects Cost Index"