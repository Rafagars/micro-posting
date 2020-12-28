from flask import Blueprint

session = Blueprint('session', __name__, template_folder='templates', static_folder='static')

from . import routes