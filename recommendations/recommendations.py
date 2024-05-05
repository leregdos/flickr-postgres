from flask import Blueprint, flash, request, render_template, redirect, session, url_for
from auth import user
from utils import functions
import base64


# Create a Blueprint for the tag-related operations
recommendations_blueprint = Blueprint('recommendations', __name__)

@recommendations_blueprint.route('/')
def recommendations_home():
    return render_template('recommendations.html')

@recommendations_blueprint.route('/friends', methods=['POST', 'GET'])
def recommendations_friends():
    user_id = session.get('userid')
    if not user_id:
        flash("You need to be logged in to view this page", "is-danger")
        return redirect(url_for('user.login'))
    
    # If the request is add friend
    if request.method == 'POST':
        return functions.add_friend(request.form['add_friend'], 1)
    
    friends, users = set(), {}
    from app import conn
    cur = conn.cursor()

    # find the ids of all friends of user
    sql = """
        SELECT U.user_id FROM Users U
        WHERE U.user_id IN (
            SELECT F.user2_id FROM Friends F WHERE F.user1_id = {0}
            UNION
            SELECT F.user1_id FROM Friends F WHERE F.user2_id = {0}
        );
    """.format(user_id)
    cur.execute(sql)
    for item in cur.fetchall():
        if not item[0]:
            continue
        friends.add(item[0])

    # find all friends of each friend of user and keep count of the occurrence
    for friend in friends:
        
        sql = """
            SELECT U.user_id, U.first_name, U.last_name, U.email FROM Users U
            WHERE U.user_id <> {0} AND U.user_id IN (
                SELECT F.user2_id FROM Friends F WHERE F.user1_id = {1}
                UNION
                SELECT F.user1_id FROM Friends F WHERE F.user2_id = {1}
            );
        """.format(user_id, friend)
        cur.execute(sql)
        for item in cur.fetchall():
            if not item[0]:
                continue
            # don't count if the user is already a friend
            if item[0] in friends:
                continue
            if item not in users:
                users[item] = 0
            users[item] += 1
    users = {user: cnt for user, cnt in sorted(users.items(), key=lambda item: item[1], reverse=True)}
    cur.close()
    return render_template('recommend_friend.html', users=users)

@recommendations_blueprint.route('/you-may-also-like', methods=['POST', 'GET'])
def you_may_also_like():
    user_id = session.get('userid')

    from app import conn
    cur = conn.cursor()

    sql = """
        WITH UserPhotos AS (
            -- Select all photos belonging to this user
            SELECT P.photo_id, P.caption, P.data
            FROM Photos P
            JOIN Albums A ON P.album_id = A.album_id
            WHERE A.owner = {0} 
        ),
        TopTags AS (
            -- Get top five tags of the user
            SELECT tag_id 
            FROM Tagged TG JOIN UserPhotos UP ON TG.photo_id = UP.photo_id
            GROUP BY tag_id 
            ORDER BY COUNT(*) DESC
            LIMIT 5
        ),
        TaggedPhoto AS (
            -- get photos that is tagged with the top tags
            SELECT DISTINCT photo_id
            FROM Tagged
            WHERE tag_id in (
                SELECT TT.tag_id
                FROM TopTags TT
            )
        )
        SELECT P.photo_id, P.data, P.caption
        FROM Photos P JOIN TaggedPhoto TP ON P.photo_id = TP.photo_id
        ORDER BY (
            -- count of the top tag
            SELECT COUNT(*)
            FROM Tagged TG
            JOIN TopTags TT ON TG.tag_id = TT.tag_id
            WHERE TG.photo_id = P.photo_id
        ) DESC, 
        (
            -- count of the number of tag in total
            SELECT COUNT(*)
            FROM Tagged TG
            WHERE TG.photo_id = P.photo_id
        ) ASC;
        """.format(user_id)
    
    cur.execute(sql)
    recommended_photos = cur.fetchall()
    cur.close()
    photos = []
    rank = 1
    for photo in recommended_photos:
        (photo_id, data, caption) = photo
        photo_dict = {}
        photo_dict['photo_id'] = photo_id
        photo_dict['rank'] = rank
        rank += 1
        photo_dict['data'] = base64.b64encode(data).decode()
        photo_dict['caption'] = caption

        # get all tags associated with this photo
        sql = """
            SELECT words 
            FROM Tags T JOIN Tagged TG ON T.tag_id = TG.tag_id
            WHERE TG.photo_id = {0};
            """.format(photo_id)
        cur = conn.cursor()
        cur.execute(sql)
        tags = []
        for tag in cur.fetchall():
            (tag,) = tag
            if tag:
                tags.append("#"+str(tag))
        photo_dict['tags_str'] = ','.join(tags)
        
        photos.append(photo_dict)
    


    return render_template('you_may_also_like.html', photos = photos)
