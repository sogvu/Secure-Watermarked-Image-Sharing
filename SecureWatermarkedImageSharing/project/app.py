import os
from flask import Flask, jsonify, send_from_directory, abort, render_template
from routes.upload    import upload_bp
from routes.watermark import watermark_bp
from routes.encrypt   import encrypt_bp
from routes.decrypt   import decrypt_bp
from routes.verify    import verify_bp
from config import UPLOAD_FOLDER, WATERMARK_FOLDER, DECRYPT_FOLDER
from database.database import init_db, get_audit_log, get_all_images

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

init_db()

app.register_blueprint(upload_bp,    url_prefix="/upload")
app.register_blueprint(watermark_bp, url_prefix="/watermark")
app.register_blueprint(encrypt_bp,   url_prefix="/encrypt")
app.register_blueprint(decrypt_bp,   url_prefix="/decrypt")
app.register_blueprint(verify_bp,    url_prefix="/verify")

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File quá lớn (tối đa 20MB)"}), 413

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/audit/<image_id>")
def audit(image_id):
    return jsonify({"image_id": image_id, "log": get_audit_log(image_id)})

@app.route("/images")
def list_images():
    return jsonify({"images": get_all_images()})

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    if ".." in filename: abort(400)
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/watermarked/<path:filename>")
def serve_watermark(filename):
    if ".." in filename: abort(400)
    return send_from_directory(WATERMARK_FOLDER, filename)

@app.route("/decrypted/<path:filename>")
def serve_decrypted(filename):
    if ".." in filename: abort(400)
    return send_from_directory(DECRYPT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)