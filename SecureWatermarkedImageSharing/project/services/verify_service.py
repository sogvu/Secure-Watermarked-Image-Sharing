import os
from config import WATERMARK_FOLDER, DECRYPT_FOLDER
from watermark.verify import verify_visible, verify_invisible
from services.metadata_service import load_metadata, verify_metadata_integrity
from database.database import log_audit


def verify_image(image_id: str, watermark_type: str = "visible") -> dict:
    meta = load_metadata(image_id)
    if not meta:
        return {"valid": False, "message": "Không tìm thấy metadata"}

    filename = meta["filename"]
    owner_id = meta.get("owner_id")

    if watermark_type == "invisible":
        result = verify_invisible(filename, expected_owner=owner_id)
    else:
        result = verify_visible(filename)

    result["metadata_intact"] = verify_metadata_integrity(image_id)
    result["owner_id"]   = owner_id
    result["receiver_id"] = meta.get("receiver_id")
    result["timestamp"]  = meta.get("timestamp")
    result["image_id"]   = image_id

    log_audit("VERIFY", image_id=image_id, filename=filename,
              owner_id=owner_id,
              detail=f"watermark_hash_match:{result.get('valid')}",
              result="SUCCESS" if result.get("valid") else "FAIL")

    return result