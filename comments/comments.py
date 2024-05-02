import base64
from flask import Blueprint, flash, request, render_template, redirect, session, url_for
from datetime import datetime
import sys

from photos import photos


# Create a Blueprint for the tag-related operations
comments_blueprint = Blueprint('comments', __name__)

@comments_blueprint.route('/', methods=['GET', 'POST'])
def comment_search():
    results_dict = {
        'query': "",
        'results': []
    }

    if request.method == 'POST':
        comment_query = request.form['comment_query']
        if not comment_query or comment_query == "":
            flash('Please enter non-empty comment to search.', 'is-danger')
            return render_template('comment_search.html')
        
        results_dict['query'] = comment_query

        # Get the user names sorted them in descending order
        from app import conn
        cur = conn.cursor()
        query = """SELECT U.user_id, U.first_name, U.last_name, COUNT(*) AS count 
                    FROM Comments C JOIN Users U ON C.owner = U.user_id 
                    WHERE C.comment_str LIKE '{0}'
                    GROUP BY U.user_id
                    ORDER BY count DESC;
                """.format(comment_query)


        cur = conn.cursor()
        cur.execute(query)  
        query_results = cur.fetchall()
        cur.close()
        # for each users, we find which photos they commented
        for row in query_results:
            (user_id, first_name, last_name, cnt) = row

            result = {
                'user_name': f"{first_name} {last_name}",
                'cnt': cnt,
                'photos': []
            }


            cur = conn.cursor()
            sql = "SELECT photo_id FROM Comments WHERE owner = {0} AND comment_str LIKE '{1}';".format(user_id, comment_query)
            cur.execute(sql)
            for photo in cur.fetchall():
                (photo_id,) = photo
                result['photos'].append(photo_id)
            cur.close()
            results_dict['results'].append(result)
            
        cur.close()
        return render_template('comment_search.html', results_dict = results_dict)
    
    return render_template('comment_search.html', results_dict = results_dict)

@comments_blueprint.route('/post-comment/<int:photo_id>', methods=['GET', 'POST'])
def post_comment(photo_id):
    if request.method == 'POST':

        date = datetime.now()
        date.strftime('%Y-%m-%d')

        from app import conn
        cur = conn.cursor()
        data = {
            'owner': None, # to represent that the comment is by visitor
            'photo_id': photo_id,
            'date': date,
            'comment_str': request.form['comment']
        }
        if session.get('userid'):
            data['owner'] = session['userid']

        columns, values = zip(*((k, v) for k, v in data.items() if v is not None))
        placeholders = ', '.join(['%s'] * len(values))
        sql = f"INSERT INTO Comments ({', '.join(columns)}) VALUES ({placeholders});"
        try:
            cur.execute(sql, values)
            conn.commit()
            flash(f'Comment posted!', 'is-success')
            return redirect(url_for('photos.view_photo', photo_id = photo_id))
        except Exception as e:
            conn.rollback()
            print("Failed to insert record into database:", e, file=sys.stderr)
            flash('Comment post failed', 'is-danger')
        finally:
            cur.close()

        return redirect(url_for('photos.view_photo', photo_id = photo_id))
    

    return redirect(url_for('photos.view_photo', photo_id = photo_id))


@comments_blueprint.route('/like-photo/<int:photo_id>', methods=['GET', 'POST'])
def like_photo(photo_id):
    if not ('userid' in session):
        flash('You need to login first to like a photo.', 'is-danger')
        return render_template('login.html')

    if request.method == 'POST':
        
        data = {
            'user_id': session['userid'], # to represent that the comment is by visitor
            'photo_id': photo_id,
        }


        from app import conn
        cur = conn.cursor()
        sql = "SELECT * FROM Likes WHERE user_id = {0} AND photo_id = {1};".format(session['userid'], photo_id)
        cur.execute(sql)
        if cur.fetchone():
            flash("You already liked this photo!", 'is-danger')
            return redirect(url_for('photos.view_photo', photo_id = photo_id))
        cur.close()


        cur = conn.cursor()
        columns, values = zip(*((k, v) for k, v in data.items() if v is not None))
        placeholders = ', '.join(['%s'] * len(values))
        sql = f"INSERT INTO Likes ({', '.join(columns)}) VALUES ({placeholders});"
        try:
            cur.execute(sql, values)
            conn.commit()
            flash(f'You liked this photo!', 'is-success')
            return redirect(url_for('photos.view_photo', photo_id = photo_id))
        except Exception as e:
            conn.rollback()
            print("Failed to insert record into database:", e, file=sys.stderr)
            flash('Like failed', 'is-danger')
        finally:
            cur.close()


    return redirect(url_for('photos.view_photo', photo_id = photo_id))
