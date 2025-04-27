from flask import Blueprint

contracts_bp = Blueprint('contracts', __name__)

@contracts_bp.route('/')
def index():
    return "Projects Contracts Index"