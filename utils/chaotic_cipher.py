class ChaoticCipher:
    def __init__(self, seed: float = 0.7, r: float = 3.99):
        self.x = seed
        self.r = r

    def get_stream(self, length: int) -> bytes:
        key_stream = bytearray()
        for _ in range(length):
            self.x = self.r * self.x * (1 - self.x)
            key_stream.append(int(self.x * 256) % 256)
        return bytes(key_stream)
    
    def encrypt(self, data: bytes) -> bytes:
        stream = self.get_stream(len(data))
        encrypted_data = bytes([b ^ k for b, k in zip(data, stream)])
        return encrypted_data
    
    
# def chaotic_stream_key(length: int, seed: float = 0.7, r: float = 3.99):
#     x = seed
#     key_stream = bytearray()
#     for _ in range(length):
#         x = r * x * (1 - x)
#         key_stream.append(int(x * 256) % 256)
#     return bytes(key_stream)

# def chaotic_encrypt(data: bytes, seed: float = 0.7) -> bytes:
#     stream = chaotic_stream_key(len(data), seed)
#     return bytes([b ^ k for b, k in zip(data, stream)])

# def chaotic_decrypt(data: bytes, seed: float = 0.7) -> bytes:
#     stream = chaotic_stream_key(len(data), seed)
#     return bytes([b ^ k for b, k in zip(data, stream)])