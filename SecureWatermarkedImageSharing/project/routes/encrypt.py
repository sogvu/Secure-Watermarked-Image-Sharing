from flask import Blueprint, request, jsonify
from services.encrypt_service import encrypt_file
from services.metadata_service import create_metadata, load_metadata

encrypt_bp = Blueprint("encrypt", __name__)

@encrypt_bp.route("/", methods=["POST"])
def encrypt():
    d = request.get_json(silent=True) or {}
    image_id      = d.get("image_id")
    filename      = d.get("filename")
    watermark_hash = d.get("watermark_hash")

    if not all([image_id, filename, watermark_hash]):
        return jsonify({"error": "Thiếu image_id / filename / watermark_hash"}), 400

    try:
        output_path, nonce_hex = encrypt_file(image_id, filename)
    except FileNotFoundError:
        return jsonify({"error": "File không tồn tại"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Tạo metadata.json đầy đủ ngay sau khi mã hóa
    from config import WATERMARK_FOLDER
    import os
    source_path = os.path.join(WATERMARK_FOLDER, filename)

    # Lấy owner/receiver từ audit log (đã lưu ở bước watermark)
    from database.database import get_audit_log
    logs = get_audit_log(image_id)
    wm_log = next((l for l in logs if l["event"] == "WATERMARK"), {})

    meta = create_metadata(
        image_id=image_id,
        filename=filename,
        source_path=source_path,
        owner_id=wm_log.get("owner_id", ""),
        receiver_id=wm_log.get("receiver_id", ""),
        watermark_hash=watermark_hash,
        nonce_hex=nonce_hex
    )

    return jsonify({"message": "Encrypted",
                    "file": output_path,
                    "nonce": nonce_hex,
                    "metadata": meta})