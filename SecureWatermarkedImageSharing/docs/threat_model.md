# Threat Model — Secure Watermarked Image Sharing

## 1. Tài sản cần bảo vệ (Assets)

| Tài sản | Mức độ nhạy cảm | Mô tả |
|---------|----------------|-------|
| Ảnh gốc | Cao | Nội dung chưa watermark |
| Ciphertext | Cao | Ảnh mã hóa trên đường truyền |
| metadata.json | Cao | Chứa nonce, hash, chữ ký RSA |
| Khóa AES | Rất cao | Mất = mất toàn bộ bảo mật |
| Khóa RSA private | Rất cao | Dùng ký metadata |
| Thông tin owner/receiver | Trung bình | Dữ liệu cá nhân |

---

## 2. Tác nhân đe dọa (Threat Actors)

| Tác nhân | Khả năng | Mục tiêu |
|---------|---------|---------|
| Người nghe lén (Eavesdropper) | Chặn gói trên mạng | Xem nội dung ảnh |
| Người giả mạo (Impersonator) | Giả làm receiver hợp lệ | Giải mã ảnh không thuộc quyền |
| Kẻ sửa đổi (Tamperer) | Chỉnh sửa ciphertext/ảnh | Phá vỡ tính toàn vẹn |
| Nội gián (Insider) | Truy cập server trực tiếp | Đánh cắp dữ liệu gốc |
| Kẻ tấn công phát lại (Replay) | Gửi lại gói cũ | Lừa hệ thống chấp nhận dữ liệu cũ |

---

## 3. Mô hình tấn công (Attack Scenarios)

### 3.1 Sửa ciphertext
- **Mô tả**: Kẻ tấn công chỉnh sửa file `.enc` trước khi người nhận giải mã
- **Biện pháp**: AES-GCM có Authentication Tag — bất kỳ thay đổi nào → giải mã thất bại ngay lập tức
- **Kết quả**: `ValueError: Giải mã thất bại`

### 3.2 Sai người nhận
- **Mô tả**: Người nhận không hợp lệ cố giải mã
- **Biện pháp**: `receiver_id` trong metadata được ký RSA, kiểm tra trước khi decrypt
- **Kết quả**: HTTP 403 Forbidden

### 3.3 Crop/sửa pixel ảnh sau giải mã
- **Mô tả**: Người nhận chỉnh sửa ảnh rồi phủ nhận đã nhận ảnh gốc
- **Biện pháp**: `watermark_hash` SHA-256 lưu trong metadata được ký — hash của ảnh sửa sẽ khác
- **Kết quả**: `tamper_check` → `watermark_hash: Không khớp`

### 3.4 Xóa watermark
- **Mô tả**: Cố xóa dấu © khỏi ảnh để phủ nhận quyền sở hữu
- **Biện pháp**: Invisible watermark (LSB) không xóa được bằng mắt thường; visible watermark để lại dấu vết hash
- **Kết quả**: `invisible_watermark: Không tìm thấy` → cảnh báo

### 3.5 Tấn công phát lại (Replay Attack)
- **Mô tả**: Gửi lại gói cũ (ciphertext + metadata) đã từng hợp lệ
- **Biện pháp**: `nonce` ngẫu nhiên mỗi lần mã hóa + `timestamp` UTC trong metadata được ký
- **Kết quả**: Hệ thống có thể phát hiện qua timestamp và image_id đã tồn tại

### 3.6 Giả mạo metadata
- **Mô tả**: Chỉnh sửa `metadata.json` để thay đổi owner_id hoặc receiver_id
- **Biện pháp**: Chữ ký RSA-PSS trên toàn bộ payload metadata
- **Kết quả**: `metadata_integrity: Bị chỉnh sửa`

---

## 4. Ma trận rủi ro (Risk Matrix)

| Tấn công | Khả năng xảy ra | Mức độ ảnh hưởng | Biện pháp hiện có |
|---------|----------------|-----------------|------------------|
| Sửa ciphertext | Trung bình | Cao | AES-GCM tag ✅ |
| Sai receiver | Cao | Cao | receiver_id check ✅ |
| Crop ảnh | Cao | Trung bình | watermark_hash ✅ |
| Xóa watermark | Trung bình | Trung bình | LSB + hash ✅ |
| Replay attack | Thấp | Trung bình | nonce + timestamp ✅ |
| Giả mạo metadata | Thấp | Cao | RSA signature ✅ |
| Lộ khóa AES | Rất thấp | Rất cao | Env variable ⚠️ |

---

## 5. Giới hạn của hệ thống

- Khóa AES dùng chung cho tất cả ảnh (symmetric) — production nên dùng per-user key hoặc hybrid RSA+AES
- Invisible watermark LSB dễ bị phá bởi nén JPEG mạnh (lossy compression)
- Chưa có cơ chế thu hồi (revocation) nếu khóa bị lộ
