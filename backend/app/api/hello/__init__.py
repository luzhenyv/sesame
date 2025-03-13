from flask import Blueprint

bp = Blueprint("hello", __name__)

from app.api.hello import routes
