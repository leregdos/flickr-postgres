from flask import flash, redirect, session, url_for

def add_friend(friend_id, index):
    user_id = session.get('userid')
    from app import conn
    cur = conn.cursor()
    # Check if the friendship already exists
    sql = """
        SELECT 1 FROM Friends F
        WHERE (F.user1_id = {0} AND F.user2_id = {1}) 
        OR (user1_id = {1} AND user2_id = {0});
    """.format(user_id, friend_id)
    cur.execute(sql)
    if cur.fetchone():
        flash("This user is already your friend.", "is-danger")
        cur.close()
        return redirect(url_for('friends.friends_add')) if not index else redirect(url_for('recommendations.recommendations_friends'))

    # Insert new friendship
    sql = """
        INSERT INTO Friends (user1_id, user2_id) VALUES ({0}, {1});
    """.format(user_id, friend_id)
    cur.execute(sql)
    conn.commit()
    cur.close()
    flash("Friend added successfully!", "is-success")

    return redirect(url_for('friends.friends_add')) if not index else redirect(url_for('recommendations.recommendations_friends'))
