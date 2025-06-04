from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import Video, User
from db import db
from functools import wraps
import os
import logging

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admins only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    video_count = Video.query.count()
    return render_template('admin/dashboard.html', user_count=user_count, video_count=video_count)

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/videos')
@login_required
@admin_required
def videos():
    videos = Video.query.all()
    return render_template('admin/videos.html', videos=videos)

@admin.route('/logs')
@login_required
@admin_required
def logs():
    log_path = os.path.join('logs', 'stream.log')
    logs = []
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            logs = f.readlines()[-200:]  
    return render_template('admin/logs.html', logs=logs)

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user and user.role != 'admin':
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.username} deleted.", "success")
    else:
        flash("Cannot delete admin or user not found.", "danger")
    return redirect(url_for('admin.users'))

@admin.route('/delete_video/<int:video_id>', methods=['POST'])
@login_required
@admin_required
def delete_video(video_id):
    video = Video.query.get(video_id)
    if video:
        # Xóa file vật lý nếu tồn tại
        try:
            if os.path.exists(video.filepath):
                os.remove(video.filepath)
        except Exception as e:
            logging.error(f"Failed to delete video file: {e}")
        db.session.delete(video)
        db.session.commit()
        flash(f"Video {video.filename} deleted.", "success")
    else:
        flash("Video not found.", "danger")
    return redirect(url_for('admin.videos'))