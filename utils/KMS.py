import os
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from datetime import datetime, timedelta
from models import Video
from db import db
from utils.chaotic_cipher import ChaoticCipher
import secrets

logging.basicConfig(
    filename=os.path.join('logs', 'kms.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

MASTER_KEY_PATH = 'master_key.key'
KEY_ROTATION_INTERVAL = timedelta(days=90)  # Xoay vòng khóa sau 90 ngày

class KeyManagementSystem:
    def __init__(self):
        self.ensure_master_key()
        self.logger = logging.getLogger('KMS')

    def ensure_master_key(self):
        """Tạo hoặc tải KEK (Key Encryption Key)"""
        if not os.path.exists(MASTER_KEY_PATH):
            self.logger.info("Generating new master key (KEK)")
            key = Fernet.generate_key()
            with open(MASTER_KEY_PATH, 'wb') as f:
                f.write(key)
            os.chmod(MASTER_KEY_PATH, 0o600)  # Chỉ root có quyền đọc/ghi

    def load_master_key(self):
        """Tải KEK từ file"""
        if not os.path.exists(MASTER_KEY_PATH):
            raise FileNotFoundError("Master key not found. Please generate it first.")
        with open(MASTER_KEY_PATH, 'rb') as f:
            key = f.read()
        self.logger.info("Master key loaded successfully")
        return key

    def generate_dek(self):
        """Tạo Data Encryption Key (DEK) cho video"""
        dek = os.urandom(32)  
        self.logger.info("Generated new DEK")
        return dek

    def encrypt_dek(self, dek: bytes) -> str:
        """Mã hóa DEK bằng KEK"""
        kek = self.load_master_key()
        f = Fernet(kek)
        encrypted_dek = f.encrypt(dek)
        self.logger.info("DEK encrypted with KEK")
        return encrypted_dek.decode()

    def decrypt_dek(self, encrypted_dek: str) -> bytes:
        """Giải mã DEK bằng KEK"""
        kek = self.load_master_key()
        f = Fernet(kek)
        try:
            dek = f.decrypt(encrypted_dek.encode())
            self.logger.info("DEK decrypted successfully")
            return dek
        except Exception as e:
            self.logger.error(f"Failed to decrypt DEK: {str(e)}")
            raise

    def generate_chaotic_seed(self):
        """Tạo seed ngẫu nhiên cho Chaotic Cipher"""
        seed = secrets.SystemRandom().uniform(0.6, 0.99)
        self.logger.info(f"Generated chaotic seed: {seed}")
        return seed

    def rotate_master_key(self):
        """Xoay vòng KEK và mã hóa lại tất cả DEK"""
        old_kek = self.load_master_key()
        new_kek = Fernet.generate_key()
        
        # Mã hóa lại tất cả DEK trong database
        videos = Video.query.all()
        for video in videos:
            try:
                old_dek = self.decrypt_dek(video.encrypted_dek)
                f = Fernet(new_kek)
                video.encrypted_dek = f.encrypt(old_dek).decode()
                db.session.commit()
                self.logger.info(f"Re-encrypted DEK for video ID: {video.id}")
            except Exception as e:
                self.logger.error(f"Failed to re-encrypt DEK for video ID {video.id}: {str(e)}")
                db.session.rollback()
                raise

        # Lưu KEK mới
        with open(MASTER_KEY_PATH, 'wb') as f:
            f.write(new_kek)
        os.chmod(MASTER_KEY_PATH, 0o600)
        self.logger.info("Master key rotated successfully")

    def check_key_rotation(self):
        """Kiểm tra xem KEK có cần xoay vòng không"""
        if os.path.exists(MASTER_KEY_PATH):
            last_modified = datetime.fromtimestamp(os.path.getmtime(MASTER_KEY_PATH))
            if datetime.now() - last_modified > KEY_ROTATION_INTERVAL:
                self.logger.info("Key rotation triggered due to interval expiration")
                self.rotate_master_key()
            else:
                self.logger.info("No key rotation needed")

    def revoke_dek(self, video_id: int):
        """Thu hồi DEK của video cụ thể"""
        video = Video.query.get(video_id)
        if video:
            video.encrypted_dek = None
            db.session.commit()
            self.logger.info(f"DEK revoked for video ID: {video.id}")
        else:
            self.logger.error(f"Video ID {video_id} not found for DEK revocation")
            raise ValueError("Video not found")