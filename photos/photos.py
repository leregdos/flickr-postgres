from flask import Blueprint, flash, request, render_template, redirect, session, url_for
from datetime import datetime
import sys
from index import index
import base64

# Create a Blueprint for the user-related operations
photos_blueprint = Blueprint('photos', __name__)

# url '/photos'
# this shows a list of albums and photos of all users
@photos_blueprint.route('/')
def index():
    from app import conn
    cur = conn.cursor()
    cur.execute("SELECT album_id, name, date_of_creation, owner FROM Albums A ;")
    album_list = []
    albums_rows = cur.fetchall()
    cur.close()
    for album_row in albums_rows:
        (album_id, name, date_of_creation, owner) = album_row
        
        album = {}
        album['album_id'] = album_id
           
        cur = conn.cursor()
        cur.execute("SELECT first_name, last_name FROM Users U WHERE U.user_id = {id};".format(id = owner))
        (first_name, last_name) = cur.fetchone()
        cur.close()

        album['display_str'] = "{album_name} (by {first_name} {last_name})".format(album_name = name, first_name = first_name, last_name = last_name)
        

        photo_list = []
        cur = conn.cursor()
        cur.execute("SELECT photo_id, caption, data FROM Photos P WHERE P.album_id = {id};".format(id = album_id))
        photos_rows = cur.fetchall()
        cur.close()
        for photo_row in photos_rows:
            (photo_id, caption, data) = photo_row
            photo = {
                'photo_id': photo_id, 
                'caption': caption,
                'data': base64.b64encode(data).decode()
            }
            photo_list.append(photo)

        album['photos'] = photo_list
        album_list.append(album)

    return render_template('photos.html', albums = album_list)

# view a single album
@photos_blueprint.route('/view-album/<int:album_id>', methods=['GET', 'POST'])
def view_album(album_id):
    # post request delete the album
    if request.method == 'POST':
        from app import conn
        cur = conn.cursor()
        sql = "DELETE FROM Albums WHERE album_id = '{0}';".format(album_id)
        try:
            cur.execute(sql)
            conn.commit()
            flash(f'Successfully deleted album!', 'is-success')
            return redirect(url_for('photos.index'))
        except Exception as e:
            conn.rollback()
            print("Failed to delete record from database:", e, file=sys.stderr)
            flash('Failed to delete photo. Please try again.', 'is-danger')
        finally:
            cur.close()

        return redirect(url_for('photos.index'))


    from app import conn
    cur = conn.cursor()
    cur.execute("SELECT name, owner, date_of_creation FROM Albums A WHERE album_id = {0};".format(album_id))
    (name, owner, date_of_creation) = cur.fetchone()
    cur.close()

    album = {
        'album_id': album_id,
        'name': name,
        'date_of_creation': date_of_creation
    }

    cur = conn.cursor()
    cur.execute("SELECT user_id, first_name, last_name FROM Users U WHERE U.user_id = {id};".format(id = owner))
    (user_id, first_name, last_name) = cur.fetchone()
    cur.close()

    album['owner'] = "{first_name} {last_name}".format(first_name = first_name, last_name = last_name)
    album['owner_id'] = user_id

    photo_list = []
    cur = conn.cursor()
    cur.execute("SELECT photo_id, caption, data FROM Photos P WHERE P.album_id = {0};".format(album_id))
    photos_rows = cur.fetchall()
    cur.close()
    for photo_row in photos_rows:
        (photo_id, caption, data) = photo_row
        photo = {
            'photo_id': photo_id, 
            'caption': caption,
            'data': base64.b64encode(data).decode()
        }
        photo_list.append(photo)

    album['photos'] = photo_list

    # This is to check if the user has the privilege to delete photo
    user_id = -1
    if session.get('userid'):
        user_id = session['userid']

    return render_template('view_album.html', user_id = user_id, album = album)


# view a single photo  
@photos_blueprint.route('/view-photo/<int:photo_id>', methods=['GET', 'POST'])
def view_photo(photo_id):
    # post request delete the photo
    if request.method == 'POST':
        from app import conn
        cur = conn.cursor()
        sql = "DELETE FROM Photos WHERE photo_id = '{0}';".format(photo_id)

        try:
            cur.execute(sql)
            conn.commit()
            flash(f'Successfully deleted photo!', 'is-success')
            return redirect(url_for('photos.index'))
        except Exception as e:
            conn.rollback()
            print("Failed to delete record from database:", e, file=sys.stderr)
            flash('Failed to delete photo. Please try again.', 'is-danger')
        finally:
            cur.close()

        return redirect(url_for('photos.index'))

    from app import conn
    cur = conn.cursor()
    cur.execute("SELECT caption, data, album_id FROM Photos P WHERE P.photo_id={0};".format(photo_id))
    (caption, data, album_id) = cur.fetchone()
    cur.close()

    # get the owner of the photo from the album it belongs to
    cur = conn.cursor()
    cur.execute("SELECT owner FROM Albums WHERE album_id = '{0}';".format(album_id))
    (owner,) = cur.fetchone()
    cur.close()
    photo = {
        'owner': owner,
        'photo_id': photo_id, 
        'photo': base64.b64encode(data).decode(), 
        'caption': caption
    }
    
    # only the owner of the photo has privilege to delete it
    user_id = -1
    if session.get('userid'):
        user_id = session['userid']

    return render_template('view_photo.html',  user_id = user_id, photo = photo)


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
            'data': request.files['photo'].stream.read(),
            'album_id': album_id
        }
        cur = conn.cursor()

        columns, values = zip(*((k, v) for k, v in data.items() if v is not None))
        placeholders = ', '.join(['%s'] * len(values))
        sql = f"INSERT INTO Photos ({', '.join(columns)}) VALUES ({placeholders}) RETURNING photo_id;"
        try:
            cur.execute(sql, values)
            photo_id = cur.fetchone()[0] # get the id of the one just inserted
            cur.close()
            
            # adding tags
            words = request.form['tags'].split(' ')
            for word in words:
                # first check if the current tag already exist
                cur = conn.cursor()
                cur.execute("SELECT tag_id FROM Tags where words = '{0}';".format(word))
                
                tag_id = cur.fetchone()
                
                # if it doesn't exist, safely add the tag
                if not tag_id: 
                    # saving tag
                    cur.close()
                    cur = conn.cursor()
                    tag = {
                        'words': word
                    }
                    columns, values = zip(*((k, v) for k, v in tag.items() if v is not None))
                    placeholders = ', '.join(['%s'] * len(values))
                    sql = f"INSERT INTO Tags ({', '.join(columns)}) VALUES ({placeholders}) RETURNING tag_id;"
                    cur.execute(sql, values)
                    tag_id = cur.fetchone()[0]
                    cur.close()
                else: # otherwise unpack the query and get the tag_id
                    (tag_id,) = tag_id 

                # saving tagged relation
                cur = conn.cursor()
                tagged = {
                    'tag_id': tag_id,
                    'photo_id': photo_id
                }
                columns, values = zip(*((k, v) for k, v in tagged.items() if v is not None))
                placeholders = ', '.join(['%s'] * len(values))
                sql = f"INSERT INTO Tagged ({', '.join(columns)}) VALUES ({placeholders});"
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

