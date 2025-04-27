from flask import Blueprint

admin_bp = Blueprint('api', __name__)

from . import routes