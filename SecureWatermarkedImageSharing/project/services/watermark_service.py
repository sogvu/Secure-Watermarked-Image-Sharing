import os, uuid
from config import UPLOAD_FOLDER, WATERMARK_FOLDER
from watermark.visible import VisibleWatermark
from watermark.invisible import InvisibleWatermark
from crypto.hash_utils import sha256_file
from database.database import log_audit


def apply_watermark(image_id: str, filename: str, owner_id: str,
                    receiver_id: str = None, watermark_type: str = "visible"):
    input_path  = os.path.join(UPLOAD_FOLDER,    filename)
    os.makedirs(WATERMARK_FOLDER, exist_ok=True)
    output_path = os.path.join(WATERMARK_FOLDER, filename)

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"File not found: {filename}")

    if watermark_type == "invisible":
        InvisibleWatermark.apply(input_path, output_path, owner_id)
    else:
        VisibleWatermark.apply(input_path, output_path, owner_id)

    # watermark_hash = SHA-256 của file SAU KHI gắn watermark
    watermark_hash = sha256_file(output_path)

    log_audit("WATERMARK", image_id=image_id, filename=filename,
              owner_id=owner_id, receiver_id=receiver_id,
              detail=f"type:{watermark_type} hash:{watermark_hash[:16]}...")

    return output_path, watermark_hash