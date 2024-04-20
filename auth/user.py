# auth.py
from flask import Blueprint, request, render_template, redirect, url_for

# Create a Blueprint for the user-related operations
user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/')
def index():
    return "User index"

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process login
        return redirect(url_for('user.profile'))
    return render_template('login.html')

@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Process registration
        return redirect(url_for('user.profile'))
    return render_template('register.html')
