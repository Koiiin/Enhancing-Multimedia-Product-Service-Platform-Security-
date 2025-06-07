import os, uuid, secrets
from flask import Blueprint, render_template, stream_with_context, request, session, redirect, url_for, flash, current_app, abort, after_this_request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

import logging
from models import Video
from db import db
from utils.key_utils import generate_video_key, encrypt_dek_with_kek, decrypt_dek_with_kek
from utils.crypto_utils import aes_encrypt_file, aes_decrypt_file
from functools import wraps
from flask import abort
from models import ViewingHistory
from utils.chaotic_cipher import ChaoticCipher
import subprocess
from ffmpeg_config import ffmpeg_path

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

def convert_to_fragmented_mp4(input_path):
    # Ghi đè file chính nó bằng fragmented version
    temp_output = input_path + '.frag.mp4'
    subprocess.run([
        f"{ffmpeg_path}",
        "-i", f"{input_path}",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-movflags", "+frag_keyframe+empty_moov+default_base_moof",
        "-f", "mp4",
        f"{temp_output}"
    ], check=True)
    os.replace(temp_output, input_path)  # Ghi đè video cũ bằng version đã fragmented

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
                convert_to_fragmented_mp4(raw_path)  # Chuyển đổi sang fragmented MP4
                logging.info(f"[UPLOAD] Saved raw file to {raw_path}")
            except Exception as e:
                logging.error(f"[UPLOAD ERROR] Failed to save raw file: {e}")
                flash("Tải lên thất bại. Không thể lưu tệp gốc.")
                return redirect(request.url)


            # ➤ Sinh AES DEK & mã hóa
            dek = generate_video_key()
            aes_encrypt_file(raw_path, enc_path, dek)

            # # ➤ Mã hóa DEK 
            encrypted_dek = encrypt_dek_with_kek(dek)

            # ➤ Xóa tệp gốc
            if os.path.exists(raw_path):
                os.remove(raw_path)


            video = Video(
                filename=filename,
                filepath=enc_path,
                uploaded_by=current_user.id,
                uploaded_by_user=current_user,
                # encrypted_dek=encrypted_dek_combined,
                encrypted_dek = encrypted_dek,
                # chaotic_seed=session_key
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

    # Sinh chaotic seed một lần duy nhất
    chaotic_seed = secrets.SystemRandom().uniform(0.6, 0.99)
    session['chaotic_seed'] = chaotic_seed
    session['chaotic_video_id'] = video_id  # Ràng buộc phiên

    ext = video.filename.rsplit('.', 1)[1].lower()
    mime_type = 'video/mp4; codecs="avc1.42E01E, mp4a.40.2"' if ext == 'mp4' else 'audio/mpeg'

    return render_template('watch.html', video=video, seed=chaotic_seed, video_id=video_id, mime_type=mime_type)

@main.route('/stream/<int:video_id>')
@login_required
def stream_video(video_id):
    if session.get('chaotic_video_id') != video_id:
        abort(403)

    chaotic_seed = session.get('chaotic_seed')
    if chaotic_seed is None:
        abort(403)

    video = Video.query.get(video_id)
    if not video:
        abort(404)

    encrypted_path = video.filepath
    if not os.path.exists(encrypted_path):
        abort(404)

    try:
        encrypted_dek = video.encrypted_dek
        dek = decrypt_dek_with_kek(encrypted_dek)
    except Exception as e:
        logging.error(f"[KEY ERROR] {e}")
        return abort(500)

    ext = video.filename.rsplit('.', 1)[1].lower()
    temp_folder = current_app.config['TEMP_FOLDER']
    os.makedirs(temp_folder, exist_ok=True)

    aes_path = os.path.join(temp_folder, f"decrypted_{video.id}.{ext}")
    clean_path = os.path.join(temp_folder, f"clean_{video.id}.{ext}")
    mime_type = 'video/mp4; codecs="avc1.42E01E, mp4a.40.2"' if ext == 'mp4' else 'audio/mpeg'

    try:
        with open(encrypted_path, 'rb') as f:
            aes_data = f.read()
        with open(aes_path, 'wb') as f:
            f.write(aes_data)
        aes_decrypt_file(aes_path, clean_path, dek)
    except Exception as e:
        logging.error(f"[DECRYPT ERROR] {e}")
        return abort(500)
    a = []
    def generate():
        try:
            chaotic = ChaoticCipher(seed=chaotic_seed)
            with open(clean_path, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    else:
                        chaotic_chunk = chaotic.encrypt(chunk)
                        chaotic_chunk =  chaotic_chunk 
                        yield chaotic_chunk
        finally:
            for path in [aes_path, clean_path]:
                try:
                    os.remove(path)
                except Exception as e:
                    logging.error(f"[CLEANUP ERROR] {e}")

    response = current_app.response_class(stream_with_context(generate()), mimetype=mime_type)
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Content-Disposition'] = 'inline'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main.route('/history')
@login_required
def history():
    records = ViewingHistory.query.filter_by(user_id=current_user.id).order_by(ViewingHistory.timestamp.desc()).all()
    return render_template('history.html', records=records)
