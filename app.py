from flask import Flask, current_app
import os
from db import db
from config import Config
from flask_login import LoginManager
from models import User
from routes.main import main
from routes.auth import auth
from routes.admin import admin
from utils.key_utils import generate_master_key
# import logging

# os.makedirs('logs', exist_ok=True)
# logging.basicConfig(
#     filename='logs/stream.log',
#     level=logging.INFO,
#     format='%(asctime)s %(levelname)s: %(message)s'
# )

generate_master_key() 

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        return db.session.get(User, int(user_id))
# Đăng ký blueprint
app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)