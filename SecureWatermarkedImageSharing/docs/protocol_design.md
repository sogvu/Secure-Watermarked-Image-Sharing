# Protocol Design — Secure Watermarked Image Sharing

## 1. Tổng quan giao thức

```
NGƯỜI GỬI                                    NGƯỜI NHẬN
    │                                              │
    │  1. Upload ảnh gốc                           │
    │  2. Gắn watermark (Visible / LSB)            │
    │  3. Tính watermark_hash = SHA-256(ảnh_wm)    │
    │  4. Mã hóa: ciphertext, nonce = AES-GCM(ảnh_wm)
    │  5. Tạo metadata = {                         │
    │       image_id, owner_id, receiver_id,       │
    │       watermark_hash, timestamp, nonce       │
    │     }                                        │
    │  6. signature = RSA-PSS(SHA256(metadata))    │
    │  7. Gửi: {ciphertext, metadata.json}         │
    │ ─────────── Kênh TLS/HTTPS ──────────────────►
    │                                              │  1. Nhận gói
    │                                              │  2. Xác thực receiver_id
    │                                              │  3. Giải mã: plaintext = AES-GCM(ciphertext, nonce)
    │                                              │     (nếu sai → từ chối)
    │                                              │  4. Xác minh chữ ký RSA metadata
    │                                              │  5. So sánh SHA-256(plaintext) == watermark_hash
    │                                              │  6. Trích xuất LSB watermark (nếu invisible)
    │                                              │  7. Hiển thị ảnh + kết quả kiểm tra
```

---

## 2. Chi tiết từng bước

### Bước 1 — Upload
- Client gửi `multipart/form-data` lên `POST /upload`
- Server sinh `image_id = uuid4()`, lưu file, ghi audit `CREATE`
- Trả về `{image_id, filename}`

### Bước 2 — Watermark
- `POST /watermark` với `{image_id, filename, owner_id, receiver_id, watermark_type}`
- **Visible**: PIL vẽ text `© {owner_id}` góc phải dưới ảnh
- **Invisible**: nhúng `owner_id + ###END###` vào LSB kênh R của từng pixel
- Tính `watermark_hash = SHA-256(file sau watermark)`
- Ghi audit `WATERMARK`

### Bước 3 — Mã hóa
- `POST /encrypt` với `{image_id, filename, watermark_hash}`
- `nonce = os.urandom(12)` (96-bit, chuẩn GCM)
- `ciphertext = AESGCM(key).encrypt(nonce, plaintext, None)`
- Lưu ciphertext (không kèm nonce) vào `encrypted/{filename}.enc`
- Tạo `metadata.json`:
  ```json
  {
    "image_id": "uuid",
    "owner_id": "...",
    "receiver_id": "...",
    "watermark_hash": "sha256hex",
    "timestamp": "2025-05-16 10:00:03 UTC",
    "nonce": "hex",
    "file_hash": "sha256hex",
    "signature": "rsahex"
  }
  ```
- Ghi audit `ENCRYPT`

### Bước 4 — Giải mã
- `POST /decrypt` với `{image_id, receiver_id}`
- Đọc metadata → kiểm tra `receiver_id` khớp → HTTP 403 nếu sai
- `nonce = bytes.fromhex(metadata["nonce"])`
- `plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)`
  - Nếu Authentication Tag sai → `InvalidTag` → HTTP 400
- Lưu vào `decrypted/`
- Ghi audit `RECEIVE` rồi `DECRYPT`

### Bước 5 — Verify & Tamper Check
- `POST /verify` → kiểm tra watermark còn nguyên
- `POST /verify/tamper`:
  - So `SHA-256(decrypted_file)` với `metadata.watermark_hash`
  - Trích xuất LSB nếu `watermark_type = invisible`
  - Xác minh chữ ký RSA của metadata
- Ghi audit `VERIFY` và `TAMPER_CHECK`

---

## 3. Sơ đồ bảo mật

```
Lớp 1 — Bảo mật nội dung:   AES-256-GCM (confidentiality + integrity)
Lớp 2 — Bảo mật quyền sở hữu: Watermark (visible/invisible)
Lớp 3 — Bảo mật metadata:   RSA-2048-PSS signature
Lớp 4 — Kiểm toán:          SQLite audit log (không thể xóa qua UI)
```

---

## 4. Thư viện & Tham số kỹ thuật

| Thành phần | Thư viện | Tham số |
|-----------|---------|---------|
| AES-GCM | `cryptography.hazmat.primitives.ciphers.aead.AESGCM` | 256-bit key, 96-bit nonce |
| SHA-256 | `hashlib.sha256` | — |
| RSA-PSS | `cryptography.hazmat.primitives.asymmetric.rsa` | 2048-bit, SHA-256, PSS-MAX |
| LSB Steganography | `numpy`, `Pillow` | 1 bit/pixel kênh R |
| Visible Watermark | `Pillow` | Font DejaVuSans 40pt, góc phải dưới |
