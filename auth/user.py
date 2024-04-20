# auth.py
from flask import Blueprint, flash, request, render_template, redirect, session, url_for
import sys
from index import index
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
        from app import conn
        gender = request.form.get('gender', None)
        if gender == 'male':
            gender = 'M'
        elif gender == 'female':
            gender = 'F'
        else:
            gender = None
        data = {
        'email': request.form['email'],
        'first_name': request.form['firstName'],
        'last_name': request.form['lastName'],
        'password': request.form['password'],  # Ideally, this should be hashed even for prototypes
        'date_of_birth': request.form.get('dateOfBirth', None) or None,
        'hometown': request.form.get('hometown', None) or None,
        'gender': gender or None
        }

        # Check if email already exists
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Users U WHERE U.email = '{0}';".format(data['email']))
            if cur.fetchone():
                flash('This email has already been registered. Please use a different email.', 'is-danger')
                return render_template('signup.html')
        # Filter out None values for optional fields
        columns, values = zip(*((k, v) for k, v in data.items() if v is not None))
        placeholders = ', '.join(['%s'] * len(values))
        sql = f"INSERT INTO Users ({', '.join(columns)}) VALUES ({placeholders}) RETURNING user_id;"
        cur = conn.cursor()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                user_id = cur.fetchone()[0]
                conn.commit()
                flash(f'Thanks for registering, {data["first_name"]}!', 'is-success')
            session['userid'] = user_id
            session['first_name'] = data["first_name"]
            session['last_name'] = data["last_name"]
            session['email'] = data["email"]
            if data['date_of_birth'] is not None:
                session['date_of_birth'] = data['date_of_birth']
            if data['gender'] is not None:
                session['gender'] = data['gender']
            if data['hometown'] is not None:
                session['hometown'] = data['hometown']
            return redirect(url_for('index.index'))
        except Exception as e:
            conn.rollback()
            print("Failed to insert record into database:", e, file=sys.stderr)
            flash('Failed to register. Please try again.', 'is-danger')
        finally:
            cur.close()
        return redirect(url_for('user.register'))

    return render_template('signup.html')

@user_blueprint.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('You have been logged out.', 'is-success')
    return redirect(url_for('index.index'))

@user_blueprint.route('/profile', methods=['GET'])
def profile():
    return session['id']
