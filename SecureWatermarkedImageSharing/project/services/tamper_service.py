"""
Phát hiện sửa đổi theo bảng trong sơ đồ:
  • Sửa ciphertext   → AES-GCM xác thực thất bại
  • Crop / sửa pixel → watermark_hash không khớp
  • Xóa watermark    → watermark không tìm thấy
  • Sai người nhận  → đã xử lý trong decrypt_service
"""
import os
from crypto.hash_utils import sha256_file
from services.metadata_service import load_metadata
from watermark.invisible import InvisibleWatermark
from config import DECRYPT_FOLDER
from database.database import log_audit


def tamper_check(image_id: str, decrypted_path: str) -> dict:
    meta = load_metadata(image_id)
    if not meta:
        return {"passed": False, "reason": "Không tìm thấy metadata"}

    checks = {}

    # 1. So sánh watermark_hash: SHA-256 file giải mã so với hash lúc tạo
    current_hash = sha256_file(decrypted_path)
    hash_match = (current_hash == meta.get("watermark_hash"))
    checks["watermark_hash"] = {
        "ok": hash_match,
        "detail": "Khớp" if hash_match else "Không khớp – ảnh bị sửa đổi sau watermark"
    }

    # 2. Invisible watermark: trích xuất owner có còn không
    try:
        extracted_owner = InvisibleWatermark.extract(decrypted_path)
        wm_present = extracted_owner is not None
        checks["invisible_watermark"] = {
            "ok": wm_present,
            "extracted_owner": extracted_owner,
            "detail": f"Owner: {extracted_owner}" if wm_present else "Watermark không tìm thấy"
        }
    except Exception as e:
        checks["invisible_watermark"] = {"ok": False, "detail": str(e)}

    # 3. Toàn vẹn metadata (chữ ký RSA)
    from services.metadata_service import verify_metadata_integrity
    meta_ok = verify_metadata_integrity(image_id)
    checks["metadata_integrity"] = {
        "ok": meta_ok,
        "detail": "Toàn vẹn OK" if meta_ok else "Metadata bị chỉnh sửa"
    }

    passed = all(c["ok"] for c in checks.values())
    result = "SUCCESS" if passed else "TAMPERED"

    log_audit("TAMPER_CHECK", image_id=image_id,
              detail="no modification" if passed else "modification detected",
              result=result)

    return {
        "passed": passed,
        "result": result,
        "checks": checks,
        "metadata": meta
    }