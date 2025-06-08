# utils/key_utils.py
import os
from cryptography.fernet import Fernet
from utils.KMS import KeyManagementSystem

MASTER_KEY_PATH = 'master_key.key'

# Tạo Master Key (KEK) 1 lần duy nhất khi chưa có

kms = KeyManagementSystem()

def generate_master_key():
    return kms.ensure_master_key()


def load_master_key():
    return kms.load_master_key()

def generate_video_key():
    return kms.generate_dek()


def encrypt_dek_with_kek(dek: bytes) -> str:
    return kms.encrypt_dek(dek)


def decrypt_dek_with_kek(encrypted_dek: str) -> bytes:
    return kms.decrypt_dek(encrypted_dek)
