from flask import Blueprint

field_bp = Blueprint('field', __name__)

@field_bp.route('/')
def index():
    return "Projects Field Index"