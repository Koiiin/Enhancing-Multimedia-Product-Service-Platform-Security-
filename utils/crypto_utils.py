# utils/crypto_utils.py
import base64
from utils.aes_crypto import aes_encrypt_file, aes_decrypt_file
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

__all__ = [
    'aes_encrypt_file',
    'aes_decrypt_file'
]

def serialize_private_key(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

def deserialize_private_key(private_key_bytes):
    return serialization.load_pem_private_key(
        private_key_bytes,
        password=None
    )

def encrypt_aes_gcm( iv: bytes, plaintext: bytes, shared_key: bytes) -> bytes:
    nonce = os.urandom(12) 
    cipher = Cipher(algorithms.AES(shared_key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    
    return nonce + ciphertext + encryptor.tag

def decrypt_aes_gcm(iv: bytes, ciphertext: bytes, shared_key: bytes) -> bytes:


    if len(ciphertext) < 16:
        raise ValueError("Ciphertext too short, missing tag.")

    tag = ciphertext[-16:]
    ciphertext = ciphertext[:-16]

    cipher = Cipher(algorithms.AES(shared_key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    return decrypted_data