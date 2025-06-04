from db import db
from models import User
from werkzeug.security import generate_password_hash
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    username = "admin"
    email = "admin@example.com"
    password = "admin123"  # Đổi thành mật khẩu mạnh
    if not User.query.filter_by(username=username).first():
        admin = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")