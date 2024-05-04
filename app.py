from flask import Flask
from index import index
from auth import user
from photos import photos
from tags import tags
from comments import comments
from friends import friends
from flask_session import Session
import psycopg2

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "cachelib"
Session(app)

# Setup Database connection
DB_HOST = "localhost"  # Database host
DB_NAME = "flickr_postgres"  # Database name
DB_USER = "username"  # Database username
DB_PASS = "pass"  # Database password
# Establish a connection to the PostgreSQL database with the above credentials
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

# Register the Blueprints
app.register_blueprint(index.index_blueprint, url_prefix='/')
app.register_blueprint(user.user_blueprint, url_prefix='/user')
app.register_blueprint(photos.photos_blueprint, url_prefix='/photos')
app.register_blueprint(tags.tags_blueprint, url_prefix='/tags')
app.register_blueprint(comments.comments_blueprint, url_prefix='/comments')
app.register_blueprint(friends.friends_blueprint, url_prefix='/friends')




if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=8000)