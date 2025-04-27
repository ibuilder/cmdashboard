from flask import Blueprint

safety_bp = Blueprint('safety', __name__)

@safety_bp.route('/')
def index():
    return "Projects Safety Index"