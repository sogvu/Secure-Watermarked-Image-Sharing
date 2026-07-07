import os
from config import UPLOAD_FOLDER, WATERMARK_FOLDER
from utils.image_compare import compare_images
from watermark.invisible import InvisibleWatermark


def verify_visible(filename: str) -> dict:
    is_present = compare_images(filename)
    return {
        "type": "visible",
        "valid": is_present,
        "message": "Visible watermark detected" if is_present else "No visible watermark / tampered",
    }


def verify_invisible(filename: str, expected_owner: str = None) -> dict:
    watermarked_path = os.path.join(WATERMARK_FOLDER, filename)

    if not os.path.isfile(watermarked_path):
        return {"type": "invisible", "valid": False, "message": "File not found"}

    extracted = InvisibleWatermark.extract(watermarked_path)

    if extracted is None:
        return {"type": "invisible", "valid": False, "message": "No invisible watermark found"}

    if expected_owner is not None and extracted != expected_owner:
        return {
            "type": "invisible",
            "valid": False,
            "message": f"Owner mismatch: expected '{expected_owner}', found '{extracted}'",
        }

    return {"type": "invisible", "valid": True, "message": "Verified", "owner": extracted}