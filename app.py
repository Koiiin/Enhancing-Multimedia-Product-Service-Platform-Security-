from flask import Flask, current_app
import os
from db import db
from config import Config
from flask_login import LoginManager
from models import User
from routes.main import main
from routes.auth import auth
from routes.admin import admin
from routes.payment import payment
from utils.key_utils import generate_master_key
from flask_migrate import Migrate
from sqlalchemy import text
import os
import sys

if sys.platform.startswith('win'):
    ffmpeg_path = r'.\\ffmpeg\\bin\\ffmpeg.exe'  # Windows path
else:
    ffmpeg_path = './ffmpeg/bin/ffmpeg'  # Linux/macOS path (không có .exe)

os.environ['FFMPEG_BINARY'] = ffmpeg_path

# Khởi tạo app
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

generate_master_key()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        return db.session.get(User, int(user_id))

app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(payment, url_prefix='/payment')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)