"""
Metadata bắt buộc theo sơ đồ:
  image_id       : UUID
  owner_id       : ID người gửi/sở hữu
  receiver_id    : ID người nhận
  watermark_hash : SHA-256 của dữ liệu watermark
  timestamp      : UTC
  nonce          : từ AES-GCM (chống phát lại)
  file_hash      : SHA-256 ảnh gốc trước khi mã hóa
  signature      : RSA-PSS để xác thực toàn vẹn metadata
"""
import os, json, uuid, time
from datetime import datetime, timezone

from config import METADATA_FOLDER
from crypto.hash_utils import sha256_file, sha256_bytes
from crypto.rsa_utils import sign_data, verify_signature


def _meta_path(image_id: str) -> str:
    return os.path.join(METADATA_FOLDER, f"{image_id}.json")


def create_metadata(image_id: str, filename: str, source_path: str,
                    owner_id: str, receiver_id: str,
                    watermark_hash: str, nonce_hex: str):
    os.makedirs(METADATA_FOLDER, exist_ok=True)

    file_hash = sha256_file(source_path)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    payload = {
        "image_id":       image_id,
        "filename":       filename,
        "owner_id":       owner_id,
        "receiver_id":    receiver_id,
        "watermark_hash": watermark_hash,
        "timestamp":      timestamp,
        "nonce":          nonce_hex,
        "file_hash":      file_hash,
    }

    # Ký số toàn bộ payload
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    payload["signature"] = sign_data(payload_bytes).hex()

    with open(_meta_path(image_id), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return payload


def load_metadata(image_id: str):
    path = _meta_path(image_id)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def verify_metadata_integrity(image_id: str) -> bool:
    meta = load_metadata(image_id)
    if not meta:
        return False
    sig = bytes.fromhex(meta.pop("signature", ""))
    payload_bytes = json.dumps(meta, sort_keys=True).encode("utf-8")
    return verify_signature(payload_bytes, sig)