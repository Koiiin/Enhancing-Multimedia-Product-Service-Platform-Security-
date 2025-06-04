import os, uuid, secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort, after_this_request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

import logging
from models import Video
from db import db
from utils.key_utils import generate_video_key, encrypt_dek_with_kek, decrypt_dek_with_kek
from utils.crypto_utils import aes_encrypt_file, aes_decrypt_file
from utils.chaotic_cipher import chaotic_encrypt, chaotic_decrypt
from functools import wraps
from flask import abort

main = Blueprint('main', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@main.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)


@main.route('/upload', methods=['GET', 'POST'])
@login_required
@role_required('content_provider')
def upload():
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
            ext = filename.rsplit('.', 1)[1].lower()
            enc_filename = f"enc_{uuid.uuid4().hex}.{ext}"
            enc_path = os.path.join(encrypted_folder, enc_filename)

            try:
                file.save(raw_path)
                logging.info(f"[UPLOAD] Saved raw file to {raw_path}")
            except Exception as e:
                logging.error(f"[UPLOAD ERROR] Failed to save raw file: {e}")
                flash("Tải lên thất bại. Không thể lưu tệp gốc.")
                return redirect(request.url)


            # ➤ Sinh AES DEK & mã hóa
            dek = generate_video_key()
            aes_encrypt_file(raw_path, enc_path, dek)

            # ➤ Sinh chaotic seed
            session_key = secrets.SystemRandom().uniform(0.6, 0.99)

            # ➤ Chaotic Encrypt nội dung AES
            with open(enc_path, 'rb') as aes_file:
                encrypted_data = aes_file.read()

            chaotic_data = chaotic_encrypt(encrypted_data, seed=session_key)

            with open(enc_path, 'wb') as final_file:
                final_file.write(chaotic_data)

            # ➤ Mã hóa DEK và lưu seed chung 
            encrypted_dek = encrypt_dek_with_kek(dek)
            encrypted_dek_combined = f"{encrypted_dek}|{session_key}"

            # ➤ Xóa tệp gốc
            if os.path.exists(raw_path):
                os.remove(raw_path)


            video = Video(
                filename=filename,
                filepath=enc_path,
                uploaded_by=current_user.id,
                encrypted_dek=encrypted_dek_combined
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

    try:
        # ➤ Tách DEK + chaotic seed
        encrypted_dek = video.encrypted_dek
        parts = encrypted_dek.split('|')
        dek = decrypt_dek_with_kek(parts[0])
        session_key = float(parts[1])
    except Exception as e:
        flash("Failed to load encryption key.", "danger")
        logging.error(f"[KEY ERROR] {e}")
        return redirect(url_for('main.index'))

    ext = video.filename.rsplit('.', 1)[1].lower()
    temp_folder = current_app.config['TEMP_FOLDER']
    os.makedirs(temp_folder, exist_ok=True)

    aes_path = os.path.join(temp_folder, f"chaotic_decrypted_{video.id}.{ext}")
    clean_path = os.path.join(temp_folder, f"clean_{video.id}.{ext}")
    mime_type = 'audio/mpeg' if ext == 'mp3' else 'video/mp4'

    try:
        # ➤ Giải mã chaotic trước
        with open(encrypted_path, 'rb') as f:
            chaotic_encrypted = f.read()
        aes_data = chaotic_decrypt(chaotic_encrypted, seed=session_key)

        with open(aes_path, 'wb') as f:
            f.write(aes_data)

        # ➤ Giải mã AES
        aes_decrypt_file(aes_path, clean_path, dek)

    except Exception as e:
        flash("Failed to decrypt video.", "danger")
        logging.error(f"[DECRYPT ERROR] {e}")
        return redirect(url_for('main.index'))

    # ➤ Stream file rõ đến client
    def generate():
        try:
            with open(clean_path, 'rb') as f:
                while chunk := f.read(4096):
                    yield chunk
        finally:
            for path in [aes_path, clean_path]:
                try:
                    os.remove(path)
                except Exception as e:
                    logging.error(f"[CLEANUP ERROR] {e}")

    return current_app.response_class(generate(), mimetype=mime_type)

