from flask import Blueprint

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
def index():
    return "Projects Settings Index"