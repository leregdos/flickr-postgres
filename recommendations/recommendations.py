from flask import Blueprint, flash, request, render_template, redirect, session, url_for
from auth import user
from utils import functions


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