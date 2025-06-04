# utils/key_utils.py
import os
from cryptography.fernet import Fernet

MASTER_KEY_PATH = 'master_key.key'

# Tạo Master Key (KEK) 1 lần duy nhất khi chưa có

def generate_master_key():
    if not os.path.exists(MASTER_KEY_PATH):
        key = Fernet.generate_key()
        with open(MASTER_KEY_PATH, 'wb') as f:
            f.write(key)


def load_master_key():
    if not os.path.exists(MASTER_KEY_PATH):
        raise FileNotFoundError("Missing master_key.key. Please generate it first.")
    with open(MASTER_KEY_PATH, 'rb') as f:
        return f.read()


def generate_video_key():
    return os.urandom(32)


def encrypt_dek_with_kek(dek: bytes) -> str:
    kek = load_master_key()
    f = Fernet(kek)
    encrypted = f.encrypt(dek)
    return encrypted.decode()


def decrypt_dek_with_kek(encrypted_dek: str) -> bytes:
    kek = load_master_key()
    f = Fernet(kek)
    return f.decrypt(encrypted_dek.encode())
