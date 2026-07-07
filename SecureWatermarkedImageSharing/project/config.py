import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
WATERMARK_FOLDER = os.path.join(BASE_DIR, "watermark")
ENCRYPT_FOLDER = os.path.join(BASE_DIR, "encrypted")
DECRYPT_FOLDER = os.path.join(BASE_DIR, "decrypted")
METADATA_FOLDER = os.path.join(BASE_DIR, "metadata")
LOG_FOLDER = os.path.join(BASE_DIR, "logs")
KEY_FOLDER = os.path.join(BASE_DIR, "keys")

# Đảm bảo tất cả thư mục đều tồn tại
for folder in (
    UPLOAD_FOLDER, WATERMARK_FOLDER, ENCRYPT_FOLDER, 
    DECRYPT_FOLDER, METADATA_FOLDER, LOG_FOLDER, KEY_FOLDER
):
    os.makedirs(folder, exist_ok=True)