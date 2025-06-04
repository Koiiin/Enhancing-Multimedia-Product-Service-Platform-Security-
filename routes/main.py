import os, uuid, secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort, after_this_request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import Video
from db import db
from utils.key_utils import generate_video_key, encrypt_dek_with_kek, decrypt_dek_with_kek
from utils.crypto_utils import aes_encrypt_file, aes_decrypt_file
from utils.chaotic_cipher import chaotic_encrypt

main = Blueprint('main', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role != 'content_provider':
        flash('Only content providers can upload videos.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        file = request.files.get('file')

        if not file or file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            encrypted_folder = current_app.config['ENCRYPTED_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            os.makedirs(encrypted_folder, exist_ok=True)

            raw_path = os.path.join(upload_folder, filename)
            enc_path = os.path.join(encrypted_folder, f"enc_{uuid.uuid4().hex}.mp4")
            file.save(raw_path)

            dek = generate_video_key()
            aes_encrypt_file(raw_path, enc_path, dek)
            encrypted_dek_b64 = encrypt_dek_with_kek(dek)
            os.remove(raw_path)

            video = Video(
                filename=filename,
                filepath=enc_path,
                uploaded_by=current_user.id,
                encrypted_dek=encrypted_dek_b64
            )
            db.session.add(video)
            db.session.commit()

            flash('Upload & encryption successful!')
            return redirect(url_for('main.index'))

        else:
            flash('Invalid file type.')
            return redirect(request.url)

    return render_template('upload.html')

@main.route('/watch/<int:video_id>', endpoint='player')
@login_required
def watch(video_id):
    video = Video.query.get(video_id)
    if not video:
        abort(404)

    encrypted_path = video.filepath
    if not os.path.exists(encrypted_path):
        abort(404)

    dek = decrypt_dek_with_kek(video.encrypted_dek)
    decrypted_path = f"temp/decrypted_{video.id}.mp4"
    os.makedirs("temp", exist_ok=True)

    if not os.path.exists(decrypted_path):
        aes_decrypt_file(encrypted_path, decrypted_path, dek)

    # Sinh Session Key ngẫu nhiên mỗi lần xem
    session_key = secrets.SystemRandom().uniform(0.6, 0.99)
    
    @after_this_request
    def cleanup(response):
        try:
            os.remove(decrypted_path)
        except Exception:
            pass
        return response

    #  Chaotic mã hóa stream nội dung trước khi gửi
    def generate():
        with open(decrypted_path, 'rb') as f:
            while chunk := f.read(4096):
                encrypted_chunk = chaotic_encrypt(chunk, seed=session_key)
                yield encrypted_chunk

    return current_app.response_class(generate(), mimetype='video/mp4')