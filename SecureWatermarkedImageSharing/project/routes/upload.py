import uuid
from flask import Blueprint, request, jsonify
from services.upload_service import UploadService
from database.database import log_audit

upload_bp = Blueprint("upload", __name__)

@upload_bp.route("/", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file"}), 400
    if not UploadService.allowed(file.filename):
        return jsonify({"error": "Chỉ nhận png/jpg/jpeg"}), 400

    image_id = str(uuid.uuid4())   # tạo ngay khi nhận ảnh
    try:
        filename = UploadService.save(file)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    log_audit("CREATE", image_id=image_id, filename=filename,
              detail=f"image_id:{image_id}")

    return jsonify({"message": "Upload success",
                    "filename": filename,
                    "image_id": image_id})