import os
from config import ENCRYPT_FOLDER, DECRYPT_FOLDER
from crypto.aes_gcm import decrypt_data
from services.metadata_service import load_metadata
from database.database import log_audit


def decrypt_file(image_id: str, receiver_id: str) -> str:
    """
    Theo sơ đồ: phải xác thực receiver_id khớp metadata trước khi giải mã.
    Sai người nhận → Giải mã thất bại.
    """
    meta = load_metadata(image_id)
    if not meta:
        raise ValueError("Không tìm thấy metadata cho image_id này")

    # Kiểm tra receiver_id
    if meta.get("receiver_id") and meta["receiver_id"] != receiver_id:
        log_audit("DECRYPT", image_id=image_id,
                  receiver_id=receiver_id,
                  detail="receiver_id không khớp", result="FAIL")
        raise PermissionError(
            f"Sai người nhận. File này dành cho '{meta['receiver_id']}'")

    filename = meta["filename"]
    nonce_hex = meta["nonce"]

    enc_path = os.path.join(ENCRYPT_FOLDER, filename + ".enc")
    if not os.path.isfile(enc_path):
        raise FileNotFoundError(f"Ciphertext không tìm thấy: {filename}.enc")

    with open(enc_path, "rb") as f:
        ciphertext = f.read()

    try:
        plaintext = decrypt_data(ciphertext, nonce_hex)
    except Exception:
        log_audit("DECRYPT", image_id=image_id,
                  detail="AES-GCM xác thực thất bại – dữ liệu bị sửa đổi",
                  result="FAIL")
        raise ValueError("Giải mã thất bại: ciphertext bị sửa đổi hoặc sai khóa")

    os.makedirs(DECRYPT_FOLDER, exist_ok=True)
    out_path = os.path.join(DECRYPT_FOLDER, filename)
    with open(out_path, "wb") as f:
        f.write(plaintext)

    log_audit("DECRYPT", image_id=image_id, filename=filename,
              receiver_id=receiver_id, detail="AES-GCM verify OK")

    return out_path