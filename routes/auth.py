# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file
from db import db
from models import User, RegisterForm, LoginForm
from base64 import b64decode
import json

from utils.crypto_utils import decrypt_aes_gcm

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():

    encrypted_data = b64decode(request.json["data"])
    client_pubkey = b64decode(request.json["client_public_key"])




    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))
        if existing_email:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', form=LoginForm())

    if request.method == "POST":
        try:
            shared_key = b64decode(session['shared_key'])

            encrypted_json = json.loads(request.form["encrypted_data"])

            data = encrypted_json["data"]
            iv = bytes(data["iv"])
            ciphertext = bytes(data["ciphertext"])

            decrypted_data = decrypt_aes_gcm(iv, ciphertext, shared_key)
            data = json.loads(decrypted_data.decode('utf-8'))

            username = data.get('username')
            password = data.get('password')

            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Tên đăng nhập hoặc mật khẩu sai.', 'danger')

        except Exception as e:
            flash('Lỗi giải mã hoặc xử lý dữ liệu.', 'danger')

    return render_template('login.html', form=LoginForm())


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))