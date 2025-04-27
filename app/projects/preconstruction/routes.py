from flask import Blueprint

preconstruction_bp = Blueprint('preconstruction', __name__)

@preconstruction_bp.route('/')
def index():
    return "Projects Preconstruction Index"