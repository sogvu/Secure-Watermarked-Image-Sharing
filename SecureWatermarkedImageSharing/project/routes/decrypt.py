from flask import Blueprint, request, jsonify
from services.decrypt_service import decrypt_file
from database.database import log_audit

decrypt_bp = Blueprint("decrypt", __name__)

@decrypt_bp.route("/", methods=["POST"])
def decrypt():
    d = request.get_json(silent=True) or {}
    image_id    = d.get("image_id")
    receiver_id = d.get("receiver_id", "")

    if not image_id:
        return jsonify({"error": "Thiếu image_id"}), 400

    log_audit("RECEIVE", image_id=image_id, receiver_id=receiver_id,
              detail=f"receiver_id:{receiver_id}")

    try:
        output_path = decrypt_file(image_id, receiver_id)
    except PermissionError as e:
        return jsonify({"error": str(e), "result": "FAIL"}), 403
    except (ValueError, FileNotFoundError) as e:
        return jsonify({"error": str(e), "result": "FAIL"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Decrypted", "file": output_path})