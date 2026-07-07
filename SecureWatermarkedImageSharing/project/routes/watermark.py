from flask import Blueprint, request, jsonify
from services.watermark_service import apply_watermark

watermark_bp = Blueprint("watermark", __name__)

@watermark_bp.route("/", methods=["POST"])
def watermark_file():
    d = request.get_json(silent=True) or {}
    image_id      = d.get("image_id")
    filename      = d.get("filename")
    owner_id      = d.get("owner_id")
    receiver_id   = d.get("receiver_id")
    watermark_type = d.get("watermark_type", "visible")

    if not all([image_id, filename, owner_id]):
        return jsonify({"error": "Thiếu image_id / filename / owner_id"}), 400
    if watermark_type not in ("visible", "invisible"):
        return jsonify({"error": "watermark_type phải là visible hoặc invisible"}), 400

    try:
        output_path, watermark_hash = apply_watermark(
            image_id, filename, owner_id, receiver_id, watermark_type)
    except FileNotFoundError:
        return jsonify({"error": "File không tồn tại"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Watermark applied",
                    "file": output_path,
                    "watermark_hash": watermark_hash})