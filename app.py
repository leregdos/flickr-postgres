from flask import Flask
from index import index
from auth import user

app = Flask(__name__)

# Register the Blueprints
app.register_blueprint(index.index_blueprint, url_prefix='/')
app.register_blueprint(user.user_blueprint, url_prefix='/user')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
