from flask import Blueprint, flash, request, render_template, redirect, session, url_for
from utils import functions
# Create a Blueprint for the contributor-related operations
contributors_blueprint = Blueprint('contributors', __name__)

@contributors_blueprint.route('/')
def contributors_home():

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

    return render_template('top_contributors.html', top_users = top_users)
