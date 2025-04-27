from flask import Blueprint

engineering_bp = Blueprint('engineering', __name__)

@engineering_bp.route('/')
def index():
    return "Projects Engineering Index"