# auth.py
from flask import Blueprint, session

# Create a Blueprint for the user-related operations
photos_blueprint = Blueprint('photos', __name__)

@photos_blueprint.route('/')
def index():
    return session["id"]
