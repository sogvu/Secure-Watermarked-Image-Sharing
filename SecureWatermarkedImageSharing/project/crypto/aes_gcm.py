"""
AES-256-GCM (AEAD).  
Theo sơ đồ: ciphertext có kèm Authentication Tag, nonce được lưu riêng
vào metadata.json (không nhúng trong file) để phía người nhận có thể
xác thực toàn vẹn trước khi giải mã.
"""
import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_NONCE_SIZE = 12

def _load_key() -> bytes:
    key_b64 = os.environ.get("AES_SECRET_KEY")
    if key_b64:
        key = base64.b64decode(key_b64)
        if len(key) != 32:
            raise ValueError("AES_SECRET_KEY phải là 32 byte sau khi decode base64")
        return key
    print("[CẢNH BÁO] AES_SECRET_KEY chưa set – dùng khóa ngẫu nhiên tạm thời (dev only)")
    return AESGCM.generate_key(bit_length=256)

_KEY = _load_key()
_aesgcm = AESGCM(_KEY)

def encrypt_data(data: bytes) -> tuple[bytes, str]:
    """Trả về (ciphertext_with_tag, nonce_hex)"""
    nonce = os.urandom(_NONCE_SIZE)
    ciphertext = _aesgcm.encrypt(nonce, data, None)
    return ciphertext, nonce.hex()          # ciphertext KHÔNG chứa nonce

def decrypt_data(data: bytes, nonce_hex: str) -> bytes:
    """Giải mã ciphertext bằng nonce từ metadata.json"""
    nonce = bytes.fromhex(nonce_hex)
    return _aesgcm.decrypt(nonce, data, None)