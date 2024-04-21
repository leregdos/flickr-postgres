from flask import Blueprint, flash, request, render_template, redirect, session, url_for
import sys
from index import index

# Create a Blueprint for the user-related operations
photos_blueprint = Blueprint('photos', __name__)

"""
CREATE TABLE Photos(
	photo_id SERIAL,
	caption VARCHAR(255),
	-- # base 64
	data BYTEA NOT NULL,
	album_id INTEGER,
	-- delete photos in an album if the album is deleted
	FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
	PRIMARY KEY (photo_id)
);
"""

@photos_blueprint.route('/')
def index():
    return session["id"]

@photos_blueprint.route('/create-album', methods=['GET', 'POST'])
def create_album():
    if request.method == 'POST':
        from app import conn
        data = {
            'name': request.form['album_name']
        }
        cur = conn.cursor()

        # Check if album of the same name of this user already exists
        cur.execute("SELECT * FROM Users U WHERE U.email = '{0}';".format(data['email']))
        if cur.fetchone():
            flash('This email has already been registered. Please use a different email.', 'is-danger')
            return render_template('signup.html')
        # Filter out None values for optional fields
        columns, values = zip(*((k, v) for k, v in data.items() if v is not None))
        placeholders = ', '.join(['%s'] * len(values))
        sql = f"INSERT INTO Users ({', '.join(columns)}) VALUES ({placeholders}) RETURNING user_id;"
        try:
            cur.execute(sql, values)
            user_id = cur.fetchone()[0]
            conn.commit()
            flash(f'Thanks for registering, {data["first_name"]}!', 'is-success')
            # Set user info as session variables
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

    return render_template('create_album.html')
                                                  
                                                 

@photos_blueprint.route('/upload-photo', methods=['GET', 'POST'])
def upload_photo():
    if request.method == 'POST':
        render_template('upload_photo.html')

    return render_template('upload_photo.html')

