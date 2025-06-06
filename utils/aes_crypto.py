from Crypto.Cipher import AES
import secrets
import ffmpeg
import os


# AES CTR Mode

def aes_encrypt_file(input_path, output_path, key):
    nonce = secrets.token_bytes(8)  # 64-bit nonce
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
        fout.write(nonce)  # prepend nonce for decryption
        while chunk := fin.read(4096):
            fout.write(cipher.encrypt(chunk))

def aes_decrypt_file(input_path, output_path, key):

    with open(input_path, 'rb') as fin:
        nonce = fin.read(8)
        cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        with open(output_path, 'wb') as fout:
            while chunk := fin.read(4096):
                fout.write(cipher.decrypt(chunk))
