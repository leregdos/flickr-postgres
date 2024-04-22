from flask import Blueprint, flash, request, render_template, redirect, session, url_for
from datetime import datetime
import sys
from index import index
import base64

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
    if not ('userid' in session):
        flash('You need to login first to create album.', 'is-danger')
        return render_template('login.html')

    if request.method == 'POST':
        from app import conn

        date = datetime.now()
        date.strftime('%Y-%m-%d')

        data = {
            'name': request.form['album_name'],
            'owner':session["userid"],
            'date_of_creation': date
        }
        cur = conn.cursor()

        # Check if album of the same name of this user already exists
        cur.execute("SELECT * FROM Albums A WHERE A.name = '{0}';".format(data['name']))
        if cur.fetchone():
            flash('You already have an album of the same name. Please use another album name.', 'is-danger')
            return render_template('create_album.html')
        
        # Filter out None values for optional fields
        columns, values = zip(*((k, v) for k, v in data.items() if v is not None))
        placeholders = ', '.join(['%s'] * len(values))
        sql = f"INSERT INTO Albums ({', '.join(columns)}) VALUES ({placeholders});"
        try:
            cur.execute(sql, values)
            conn.commit()
            flash(f'Album {data["name"]} successfully created!', 'is-success')
            # Set user info as session variables
            return redirect(url_for('index.index'))
        except Exception as e:
            conn.rollback()
            print("Failed to insert record into database:", e, file=sys.stderr)
            flash('Failed to create album. Please try again.', 'is-danger')
        finally:
            cur.close()

    return render_template('create_album.html')
                                                  
                                                 

@photos_blueprint.route('/upload-photo/<int:album_id>', methods=['GET', 'POST'])
def upload_photo(album_id):
    if not ('userid' in session):
        flash('You need to login first to upload photo.', 'is-danger')
        return render_template('login.html')

    # Check if the album belongs to the user
    from app import conn
    cur = conn.cursor()
    cur.execute("SELECT owner, name FROM Albums A WHERE A.album_id = '{0}';".format(album_id))

    (album_owner, album_name) = cur.fetchone()

    
    if album_owner != session['userid']:
        flash('You cannot upload photo to album that is not yours.', 'is-danger')
        return render_template('photos.html')
    cur.close()
    


    if request.method == 'POST':

        date = datetime.now()
        date.strftime('%Y-%m-%d')

        data = {
            'caption': request.form['caption'],
            'data': base64.b64encode(request.files['photo'].read()),
            'album_id': album_id
        }
        cur = conn.cursor()

        # Filter out None values for optional fields
        columns, values = zip(*((k, v) for k, v in data.items() if v is not None))
        placeholders = ', '.join(['%s'] * len(values))
        sql = f"INSERT INTO Photos ({', '.join(columns)}) VALUES ({placeholders});"
        try:
            cur.execute(sql, values)
            conn.commit()
            flash(f'Photo successfully uploaded to album {album_name}', 'is-success')
            return render_template('upload_photo.html', album_id = album_id, album_name = album_name)
        except Exception as e:
            conn.rollback()
            print("Failed to insert record into database:", e, file=sys.stderr)
            flash('Failed to upload photo. Please try again.', 'is-danger')
        finally:
            cur.close()

        render_template('upload_photo.html', album_id = album_id, album_name = album_name)

    return render_template('upload_photo.html', album_id = album_id, album_name = album_name)

