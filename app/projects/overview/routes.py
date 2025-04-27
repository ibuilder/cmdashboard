from flask import Blueprint

overview_bp = Blueprint('overview', __name__)

@overview_bp.route('/')
def index():
    return "Projects Overview Index"