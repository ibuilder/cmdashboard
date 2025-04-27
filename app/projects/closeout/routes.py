from flask import Blueprint

closeout_bp = Blueprint('closeout', __name__)

@closeout_bp.route('/')
def index():
    return "Projects Closeout Index"