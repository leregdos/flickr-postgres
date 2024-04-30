import base64
from flask import Blueprint, flash, request, render_template, redirect, session, url_for
# from index import index

# Create a Blueprint for the tag-related operations
tags_blueprint = Blueprint('tags', __name__)

@tags_blueprint.route('/')
def root():
    return redirect(url_for('photos.index'))

@tags_blueprint.route('/<string:tag_name>')
def view_tag(tag_name):
    from app import conn
    cur = conn.cursor()

    user_id = session.get('userid')
    if request.args.get('own') == 'true' and user_id:
        # Fetch only user's photos with the tag
        sql = """
            SELECT P.photo_id, P.data, P.caption FROM Photos P
            JOIN Tagged T ON P.photo_id = T.photo_id
            JOIN Tags Ta ON Ta.tag_id = T.tag_id
            JOIN Albums A ON A.album_id = P.album_id
            WHERE Ta.words = '{0}' AND A.owner = {1};
        """.format(tag_name, user_id)
        cur.execute(sql)
    elif request.args.get('own') == 'true' and not user_id:
        # Check if user is logged in
        return render_template('view_tag.html', photos=[], tag_name=tag_name)
    else:
        # Fetch all photos with the tag
        sql = """
            SELECT P.photo_id, P.data, P.caption FROM Photos P
            JOIN Tagged T ON P.photo_id = T.photo_id
            JOIN Tags Ta ON Ta.tag_id = T.tag_id
            WHERE Ta.words = '{0}';
        """.format(tag_name)
        cur.execute(sql)

    photos = []
    for row in cur.fetchall():
        photo_id, data, caption = row
        # Ensure data is a bytes object and encode it in base64
        photos.append([photo_id, base64.b64encode(data).decode(), caption ])
    cur.close()

    return render_template('view_tag.html', photos=photos, tag_name=tag_name)
