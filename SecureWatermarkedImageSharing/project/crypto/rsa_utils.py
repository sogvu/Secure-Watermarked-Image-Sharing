"""
Dùng RSA để ký số (digital signature) lên metadata (hash ảnh + owner +
timestamp), giúp người nhận xác minh metadata này thực sự do server
tạo ra và không bị chỉnh sửa sau đó - khác với AES (aes_gcm.py) vốn
dùng để giữ BÍ MẬT nội dung ảnh, còn RSA ở đây dùng để đảm bảo TÍNH
TOÀN VẸN / XÁC THỰC.

Khóa được lưu trong thư mục `keys/` (tạo tự động nếu chưa có), KHÔNG
commit khóa private lên git khi deploy thật.
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

from config import BASE_DIR

_KEY_DIR = os.path.join(BASE_DIR, "keys")
_PRIVATE_KEY_PATH = os.path.join(_KEY_DIR, "private_key.pem")
_PUBLIC_KEY_PATH = os.path.join(_KEY_DIR, "public_key.pem")


def _generate_keypair():
    os.makedirs(_KEY_DIR, exist_ok=True)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with open(_PRIVATE_KEY_PATH, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(_PUBLIC_KEY_PATH, "wb") as f:
        f.write(
            private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    return private_key


def _load_or_create_keypair():
    if os.path.isfile(_PRIVATE_KEY_PATH):
        with open(_PRIVATE_KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    return _generate_keypair()


_private_key = _load_or_create_keypair()
_public_key = _private_key.public_key()


def sign_data(data: bytes) -> bytes:
    return _private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def verify_signature(data: bytes, signature: bytes) -> bool:
    try:
        _public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False