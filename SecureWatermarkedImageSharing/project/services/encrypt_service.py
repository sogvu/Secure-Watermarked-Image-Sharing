import os
from config import WATERMARK_FOLDER, ENCRYPT_FOLDER
from crypto.aes_gcm import encrypt_data
from crypto.hash_utils import sha256_file
from database.database import log_audit


def encrypt_file(image_id: str, filename: str) -> tuple[str, str]:
    """Trả về (output_path, nonce_hex)"""
    input_path = os.path.join(WATERMARK_FOLDER, filename)
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"File not found: {filename}")

    with open(input_path, "rb") as f:
        data = f.read()

    ciphertext, nonce_hex = encrypt_data(data)   # nonce tách riêng

    os.makedirs(ENCRYPT_FOLDER, exist_ok=True)
    output_path = os.path.join(ENCRYPT_FOLDER, filename + ".enc")
    with open(output_path, "wb") as f:
        f.write(ciphertext)

    log_audit("ENCRYPT", image_id=image_id, filename=filename,
              detail=f"alg:AES-GCM nonce:{nonce_hex[:14]}...")

    return output_path, nonce_hex