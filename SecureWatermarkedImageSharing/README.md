# 🔐 Secure Watermarked Image Sharing

> **Đề tài 9** — FIT4012 | Hệ thống gửi ảnh có gắn watermark bảo mật

---

## Tổng quan hệ thống

Hệ thống cho phép người gửi:
1. **Upload** ảnh gốc
2. **Gắn watermark** (Visible hoặc Invisible/LSB)
3. **Mã hóa** bằng AES-256-GCM (AEAD — có xác thực)
4. **Tạo metadata** gồm: `image_id` (UUID), `owner_id`, `receiver_id`, `watermark_hash` (SHA-256), `timestamp` (UTC), `nonce`
5. **Gửi gói** (ciphertext + metadata.json) qua kênh an toàn

Người nhận:
1. **Giải mã** — xác thực `receiver_id` + AES-GCM tag
2. **Trích xuất & kiểm tra watermark**
3. **Phát hiện sửa đổi** — so hash, kiểm tra chữ ký RSA metadata

---

## Cấu trúc thư mục

```
SecureWatermarkedImageSharing/
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── config.py               # Đường dẫn thư mục
│   ├── crypto/
│   │   ├── aes_gcm.py          # AES-256-GCM encrypt/decrypt
│   │   ├── hash_utils.py       # SHA-256
│   │   └── rsa_utils.py        # RSA-PSS ký metadata
│   ├── database/
│   │   └── database.py         # SQLite audit log
│   ├── routes/                 # Flask blueprints (upload/watermark/encrypt/decrypt/verify)
│   ├── services/               # Business logic
│   │   ├── metadata_service.py
│   │   ├── watermark_service.py
│   │   ├── encrypt_service.py
│   │   ├── decrypt_service.py
│   │   ├── verify_service.py
│   │   └── tamper_service.py
│   ├── watermark/
│   │   ├── visible.py          # Visible watermark (PIL)
│   │   └── invisible.py        # Invisible watermark (LSB steganography)
│   ├── utils/
│   ├── templates/index.html
│   └── static/
├── tests/
│   ├── test_valid_flow.py
│   ├── test_tampering.py
│   ├── test_replay.py
│   └── test_invalid_key.py
├── docs/
│   ├── threat_model.md
│   ├── protocol_design.md
│   ├── test_report.md
│   └── benchmark.md
├── report/
│   └── figures/
├── sample_data/
└── requirements.txt
```

---

## Cài đặt & Chạy

```bash
# 1. Clone & tạo môi trường ảo
git clone <repo-url>
cd SecureWatermarkedImageSharing
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 2. Cài thư viện
pip install -r requirements.txt

# 3. (Tùy chọn) Đặt khóa AES cố định
export AES_SECRET_KEY=$(python -c "import os,base64; print(base64.b64encode(os.urandom(32)).decode())")

# 4. Chạy server
cd backend
python app.py
# → http://127.0.0.1:5000
```

---

## Chạy kiểm thử tự động

```bash
cd backend
pytest ../tests/ -v
```

---

## API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/upload` | Upload ảnh, nhận `image_id` |
| POST | `/watermark` | Gắn watermark, nhận `watermark_hash` |
| POST | `/encrypt` | Mã hóa AES-GCM, tạo metadata.json |
| POST | `/decrypt` | Giải mã (xác thực receiver_id) |
| POST | `/verify` | Kiểm tra watermark |
| POST | `/verify/tamper` | Phát hiện sửa đổi |
| GET | `/audit/<image_id>` | Xem audit log |

---

## Kiểm thử bắt buộc (12.1.0.44)

| # | Tình huống | Kết quả mong đợi | Script |
|---|-----------|-----------------|--------|
| 1 | Gửi ảnh hợp lệ | Watermark + giải mã thành công | `test_valid_flow.py` |
| 2 | Sửa ciphertext | AES-GCM xác thực thất bại | `test_tampering.py` |
| 3 | Crop ảnh sau giải mã | watermark_hash không khớp | `test_tampering.py` |
| 4 | Xóa watermark | Watermark không tìm thấy | `test_tampering.py` |
| 5 | Sai receiver_id | Giải mã thất bại (403) | `test_invalid_key.py` |

---

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|-----------|----------|
| Backend | Python 3.x, Flask |
| Mã hóa | AES-256-GCM (`cryptography`) |
| Chữ ký số | RSA-2048-PSS |
| Hash | SHA-256 |
| Watermark ẩn | LSB Steganography (NumPy) |
| Watermark hiện | PIL/Pillow |
| Database | SQLite |
| Frontend | HTML5, CSS3, JavaScript thuần |