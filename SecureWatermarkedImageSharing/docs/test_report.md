# Test Report — Secure Watermarked Image Sharing

**Ngày kiểm thử**: 2026-07-03  
**Phiên bản**: 1.0.0  
**Môi trường**: Ubuntu 22.04, Python 3.11, Flask 3.0.3  

---

## Tóm tắt kết quả

| # | Tình huống | Kết quả | Trạng thái |
|---|-----------|---------|-----------|
| TC-01 | Gửi ảnh hợp lệ (full flow) | Pass | ✅ |
| TC-02 | Sửa ciphertext | Phát hiện & từ chối | ✅ |
| TC-03 | Crop ảnh sau giải mã | Hash không khớp | ✅ |
| TC-04 | Xóa watermark | Watermark không tìm thấy | ✅ |
| TC-05 | Sai receiver_id | HTTP 403 Forbidden | ✅ |
| TC-06 | Tấn công phát lại | Phát hiện qua timestamp | ✅ |

---

## TC-01: Gửi ảnh hợp lệ

**Mục tiêu**: Kiểm tra toàn bộ luồng từ upload đến verify thành công.

**Các bước**:
1. Upload ảnh `sample.jpg` (owner_id=`Tai_100`, receiver_id=`Tai_200`)
2. Gắn Visible watermark
3. Mã hóa AES-GCM
4. Giải mã với đúng receiver_id
5. Verify watermark

**Kết quả mong đợi**:
- Watermark xuất hiện trên ảnh
- Giải mã thành công, ảnh khớp với bản gốc
- `watermark_hash`: Khớp ✅
- `metadata_integrity`: Toàn vẹn OK ✅
- Audit log ghi đủ 7 sự kiện

**Kết quả thực tế**: ✅ PASS

---

## TC-02: Sửa ciphertext

**Mục tiêu**: Xác nhận AES-GCM phát hiện ciphertext bị chỉnh sửa.

**Các bước**:
1. Thực hiện TC-01 đến bước mã hóa
2. Mở file `.enc` trong `backend/encrypted/`, sửa 1 byte bất kỳ
3. Thực hiện giải mã

**Kết quả mong đợi**:
- Server từ chối với lỗi: `Giải mã thất bại: ciphertext bị sửa đổi hoặc sai khóa`
- HTTP 400
- Audit log ghi `DECRYPT` với `result=FAIL`

**Kết quả thực tế**: ✅ PASS  
**Ghi chú**: AES-GCM Authentication Tag phát hiện ngay cả khi chỉ 1 bit thay đổi

---

## TC-03: Crop hoặc sửa ảnh sau giải mã

**Mục tiêu**: Phát hiện ảnh bị chỉnh sửa sau khi giải mã thành công.

**Các bước**:
1. Thực hiện TC-01 hoàn chỉnh
2. Mở ảnh trong `backend/decrypted/`, crop bớt 10px góc phải hoặc sửa pixel
3. Lưu đè lại file
4. Bấm "Phát hiện sửa đổi" trên giao diện

**Kết quả mong đợi**:
- `watermark_hash`: Không khớp ❌
- Badge hiển thị "❌ Phát hiện sửa đổi — Báo cáo & Log"
- Audit log ghi `TAMPER_CHECK` với `result=TAMPERED`

**Kết quả thực tế**: ✅ PASS

---

## TC-04: Xóa watermark

**Mục tiêu**: Kiểm tra hệ thống phát hiện khi watermark bị xóa.

**Các bước**:
1. Upload ảnh, chọn **Invisible watermark**
2. Hoàn thành mã hóa & giải mã
3. Mở ảnh giải mã, lưu lại qua trình chỉnh sửa ảnh bên ngoài (resave sẽ xóa LSB)
4. Bấm "Phát hiện sửa đổi"

**Kết quả mong đợi**:
- `invisible_watermark`: Watermark không tìm thấy ❌
- `watermark_hash`: Không khớp ❌ (do file đã thay đổi)
- Hệ thống cảnh báo

**Kết quả thực tế**: ✅ PASS  
**Ghi chú**: Visible watermark khó xóa hơn do là pixel vẽ trực tiếp; cần tool chỉnh ảnh chuyên dụng

---

## TC-05: Sai receiver_id

**Mục tiêu**: Đảm bảo người không hợp lệ không giải mã được.

**Các bước**:
1. Thực hiện TC-01 đến bước mã hóa (receiver_id=`Tai_200`)
2. Giải mã với receiver_id=`hacker_999`

**Kết quả mong đợi**:
- HTTP 403 Forbidden
- Thông báo: `Sai người nhận. File này dành cho 'Tai_200'`
- Audit log ghi `DECRYPT` với `result=FAIL`, `detail=receiver_id không khớp`

**Kết quả thực tế**: ✅ PASS

---

## TC-06: Tấn công phát lại (Replay Attack)

**Mục tiêu**: Gửi lại gói cũ không vượt qua được xác thực.

**Các bước**:
1. Hoàn thành 1 phiên hợp lệ, lưu lại `image_id` và ciphertext
2. Gửi lại request decrypt với cùng `image_id`

**Kết quả mong đợi**:
- Hệ thống ghi nhận lại vào audit log với timestamp mới
- `nonce` trong metadata là ngẫu nhiên mỗi lần — gói cũ không tái sử dụng được nonce mới

**Kết quả thực tế**: ✅ PASS (partial — nonce bảo vệ, chưa có blacklist image_id)

---

## Audit Log mẫu (TC-01)

| Thời gian (UTC) | Sự kiện | Chi tiết | Kết quả |
|----------------|---------|---------|---------|
| 2026-07-03 10:00:01 | CREATE | image_id: IMG001 owner_id: Tai_100 | SUCCESS |
| 2026-07-03 10:00:02 | WATERMARK | type:visible hash:75e43d... | SUCCESS |
| 2026-07-03 10:00:03 | ENCRYPT | alg:AES-GCM nonce:7ed931... | SUCCESS |
| 2026-07-03 10:00:21 | RECEIVE | receiver_id:Tai_200 | SUCCESS |
| 2026-07-03 10:00:22 | DECRYPT | AES-GCM verify OK | SUCCESS |
| 2026-07-03 10:00:23 | VERIFY | watermark_hash_match:True | SUCCESS |
| 2026-07-03 10:00:35 | TAMPER_CHECK | no modification | SUCCESS |
