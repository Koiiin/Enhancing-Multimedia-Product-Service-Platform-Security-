from flask import Flask
from db import db
from config import Config
from flask_login import LoginManager
from models import User
from routes.main import main
from routes.auth import auth
from utils.key_utils import generate_master_key

generate_master_key() 

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Đăng ký blueprint
app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)