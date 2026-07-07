"""
Hàm compare_images cũ chỉ nhận 1 filename - không rõ so sánh với cái gì
(so sánh ảnh với chính nó luôn = True, vô nghĩa). Sửa lại: so sánh ảnh
trong UPLOAD_FOLDER (gốc) với ảnh cùng tên trong WATERMARK_FOLDER (đã
gắn watermark) để xác nhận watermark có tồn tại / ảnh có bị chỉnh sửa
thêm hay không, dùng similarity theo pixel.
"""

import os
from PIL import Image, ImageChops
import numpy as np

from config import UPLOAD_FOLDER, WATERMARK_FOLDER

# Ngưỡng khác biệt cho phép (0-1). Watermark hợp lệ sẽ làm ảnh khác
# một chút so với gốc, nhưng không quá nhiều.
_DIFF_THRESHOLD = 0.35


def compare_images(filename: str) -> bool:
    original_path = os.path.join(UPLOAD_FOLDER, filename)
    watermarked_path = os.path.join(WATERMARK_FOLDER, filename)

    if not os.path.isfile(original_path) or not os.path.isfile(watermarked_path):
        return False

    original = Image.open(original_path).convert("RGB")
    watermarked = Image.open(watermarked_path).convert("RGB")

    if original.size != watermarked.size:
        return False

    diff = ImageChops.difference(original, watermarked)
    diff_array = np.array(diff, dtype=np.float32)

    # Tỷ lệ pixel thay đổi đáng kể (watermark hiện diện) so với tổng ảnh
    changed_ratio = np.mean(diff_array > 10)

    # Watermark hợp lệ: có thay đổi (>0) nhưng không thay đổi toàn ảnh
    # (>threshold nghĩa là ảnh đã bị chỉnh sửa quá mức / không khớp gốc).
    return 0 < changed_ratio <= _DIFF_THRESHOLD