from flask import Flask
from index import index
from auth import user
import psycopg2

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)