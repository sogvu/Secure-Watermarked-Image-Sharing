# Benchmark — Hiệu năng hệ thống

**Môi trường**: Intel Core i5-1135G7, 8GB RAM, Ubuntu 22.04, Python 3.11

---

## Thời gian xử lý theo kích thước ảnh

| Kích thước ảnh | Upload | Watermark | Mã hóa AES-GCM | Giải mã | Verify |
|---------------|--------|-----------|----------------|---------|--------|
| 500KB (1280×720) | ~50ms | ~120ms | ~35ms | ~30ms | ~25ms |
| 2MB (1920×1080) | ~180ms | ~450ms | ~140ms | ~130ms | ~90ms |
| 5MB (3840×2160) | ~420ms | ~1200ms | ~350ms | ~320ms | ~210ms |

## Nhận xét

- **Bottleneck chính**: Visible watermark (PIL vẽ text) và Invisible watermark (LSB numpy)
- **AES-GCM rất nhanh**: < 200ms cho ảnh 5MB — không phải bottleneck
- **Giới hạn hiện tại**: 20MB/request (config Flask `MAX_CONTENT_LENGTH`)

## Khuyến nghị tối ưu

- Dùng `Pillow-SIMD` thay `Pillow` cho xử lý ảnh nhanh hơn ~2-4x
- Chạy watermark bất đồng bộ (Celery) cho ảnh > 5MB
- Cache metadata đã verify trong Redis thay vì đọc file JSON mỗi lần
