import base64
from flask import Blueprint, flash, request, render_template, session

# Create a Blueprint for the tag-related operations
tags_blueprint = Blueprint('tags', __name__)

@tags_blueprint.route('/')
def tags_home():
    return render_template('tags.html')

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

@tags_blueprint.route('/popular-tags')
def popular_tags():
    from app import conn
    cur = conn.cursor()
    cur.execute("""
        SELECT Tags.words, COUNT(Tagged.photo_id) as photo_count 
        FROM Tags
        JOIN Tagged ON Tags.tag_id = Tagged.tag_id
        GROUP BY Tags.words
        ORDER BY photo_count DESC;
    """)
    tags = cur.fetchall()
    tagsAlt = []
    for tag in tags:
        if not tag[0]:
            continue
        tagsAlt.append([tag[0], tag[1]])
    cur.close()
    return render_template('popular_tags.html', tags=tagsAlt)

@tags_blueprint.route('/search-by-tag', methods=['GET', 'POST'])
def search_by_tag():
    if request.method == 'POST':
        tags = request.form['tags'].split()
        if not tags or tags[0] == '' or tags[0] == ' ':
            flash('Please enter at least one tag.', 'is-danger')
            return render_template('tag_search.html')
        tags = [tag.lower() for tag in tags]
        from app import conn
        cur = conn.cursor()
        placeholders = ', '.join(['%s'] * len(tags))  # Create placeholders for query
        query = f"""
            SELECT P.photo_id, P.caption, P.data
            FROM Photos P
            JOIN Tagged T ON P.photo_id = T.photo_id
            JOIN Tags Ta ON T.tag_id = Ta.tag_id
            WHERE Ta.words IN ({placeholders})
            GROUP BY P.photo_id, P.caption, P.data
            HAVING COUNT(DISTINCT Ta.words) = %s;
        """
        cur = conn.cursor()
        cur.execute(query, tags + [len(tags)])  # Execute query with tags and count
        photos = []
        for row in cur.fetchall():
            photo_id, caption, data = row
            # Ensure data is a bytes object and encode it in base64
            photos.append([photo_id, base64.b64encode(data).decode(), caption ])
        cur.close()
        return render_template('tag_search_results.html', photos=photos, tags=' & '.join(tags))
    
    return render_template('tag_search.html')
