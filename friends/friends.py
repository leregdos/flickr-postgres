from flask import Blueprint, flash, request, render_template, redirect, session, url_for
from utils import functions
# Create a Blueprint for the friend-related operations
friends_blueprint = Blueprint('friends', __name__)

@friends_blueprint.route('/')
def friends_home():

    from app import conn
    cur = conn.cursor()
    sql = """
        WITH PhotoCnt AS (
            SELECT A.owner, COUNT(*)
            FROM Albums A JOIN Photos P ON A.album_id = P.album_id
            GROUP BY A.owner
        ),
        CommentCnt AS (
            SELECT C.owner, COUNT(*)
            FROM Comments C 
            WHERE C.owner IS NOT NULL
            GROUP BY C.owner
        )
        SELECT U.first_name, U.last_name, U.email
        FROM Users U
        ORDER BY (
            SELECT PC.count + CC.count
            FROM PhotoCnt PC, CommentCnt CC
            WHERE PC.owner = U.user_id AND CC.owner = U.user_id
        ) DESC
        LIMIT 10;
        """
    
    cur.execute(sql)
    top_users = []
    rank = 1
    for user in cur.fetchall():
        (first_name, last_name, email) = user
        user_dict = {}
        user_dict['name'] = f"{first_name} {last_name} ({email})"
        user_dict['rank'] = rank
        rank += 1
        top_users.append(user_dict)

    return render_template('friends.html', top_users = top_users)

@friends_blueprint.route('/list')
def friends_list():
    user_id = session.get('userid')
    if not user_id:
        flash("You need to be logged in to view this page", "is-danger")
        return redirect(url_for('user.login'))
    friends = []
    from app import conn
    cur = conn.cursor()
    sql = """
        SELECT U.first_name, U.last_name, U.email FROM Users U
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
        friends.append(item)
    cur.close()

    return render_template('list_friends.html', users=friends)

@friends_blueprint.route('/add', methods=['POST', 'GET'])
def friends_add():
    user_id = session.get('userid')
    if not user_id:
        flash("You need to be logged in to view this page", "is-danger")
        return redirect(url_for('user.login'))
    
    from app import conn
    cur = conn.cursor()
    users, query = [], ''
    # If the request is add friend
    if request.method == 'POST' and 'add_friend' in request.form:
        return functions.add_friend(request.form['add_friend'], 0)
    # If the request is a search request
    elif request.method == 'POST':
        search_query = request.form.get('search_query', '')
        if search_query:
            sql = """
                SELECT U.user_id, U.first_name, U.last_name, U.email FROM Users U
                WHERE (U.first_name ILIKE '{0}' OR U.last_name ILIKE '{0}' OR U.email ILIKE '{0}') AND U.user_id <> {1};
            """.format(search_query, user_id)
            cur.execute(sql)
            for item in cur.fetchall():
                if not item[0]:
                    continue
                users.append(item)
            query = search_query
        else:
            sql = """
                SELECT U.user_id, U.first_name, U.last_name, U.email FROM Users U
                WHERE U.user_id <> {0} AND U.user_id NOT IN (
                    SELECT F.user2_id FROM Friends F WHERE F.user1_id = {0}
                    UNION
                    SELECT F.user1_id FROM Friends F WHERE F.user2_id = {0}
                );
            """.format(user_id)
            cur.execute(sql)
            for item in cur.fetchall():
                if not item[0]:
                    continue
                users.append(item)
    # If it's a GET request, list all users the user is not friends with
    else:
        sql = """
                SELECT U.user_id, U.first_name, U.last_name, U.email FROM Users U
                WHERE U.user_id <> {0} AND U.user_id NOT IN (
                    SELECT F.user2_id FROM Friends F WHERE F.user1_id = {0}
                    UNION
                    SELECT F.user1_id FROM Friends F WHERE F.user2_id = {0}
                );
            """.format(user_id)
        cur.execute(sql)
        for item in cur.fetchall():
            if not item[0]:
                continue
            users.append(item)
    cur.close()
    return render_template('add_friend.html', users=users, query=query)
