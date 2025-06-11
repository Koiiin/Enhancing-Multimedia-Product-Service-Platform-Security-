from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
import os

class ECDH:
    def __init__(self):
        # Tạo key động mỗi lần khởi tạo
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()

    def get_public_bytes(self):
        # Pub key trao đổi với client
        return self.public_key.public_bytes(
            encoding = serialization.Encoding.X962,
            format = serialization.PublicFormat.UncompressedPoint
        )

    def generate_shared_key(self, peer_public_bytes: bytes) -> bytes:
        # Pub key của client được gửi đến server
        peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(),
            peer_public_bytes
        )

        # Tính toán shared secret
        shared_secret = self.private_key.exchange(ec.ECDH(), peer_public_key)


        return shared_secret
    

