from flask import Blueprint, request, jsonify
from services.verify_service import verify_image
from services.tamper_service import tamper_check
from config import DECRYPT_FOLDER
import os

verify_bp = Blueprint("verify", __name__)

@verify_bp.route("/", methods=["POST"])
def verify():
    d = request.get_json(silent=True) or {}
    image_id       = d.get("image_id")
    watermark_type = d.get("watermark_type", "visible")
    if not image_id:
        return jsonify({"error": "Thiếu image_id"}), 400
    return jsonify(verify_image(image_id, watermark_type))

@verify_bp.route("/tamper", methods=["POST"])
def tamper():
    d = request.get_json(silent=True) or {}
    image_id = d.get("image_id")
    if not image_id:
        return jsonify({"error": "Thiếu image_id"}), 400

    # Cần ảnh đã giải mã
    from services.metadata_service import load_metadata
    meta = load_metadata(image_id)
    if not meta:
        return jsonify({"error": "Không tìm thấy metadata"}), 404

    dec_path = os.path.join(DECRYPT_FOLDER, meta["filename"])
    if not os.path.isfile(dec_path):
        return jsonify({"error": "Chưa giải mã – hãy giải mã trước"}), 400

    return jsonify(tamper_check(image_id, dec_path))