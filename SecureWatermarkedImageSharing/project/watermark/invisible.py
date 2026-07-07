"""
Watermark vô hình bằng kỹ thuật LSB (Least Significant Bit) steganography:
nhúng chuỗi owner vào bit thấp nhất của kênh màu Blue, không thay đổi
hình ảnh đến mức mắt người nhận ra được, nhưng có thể trích xuất lại
chính xác để xác minh quyền sở hữu (khác với visible watermark là chèn
chữ nhìn thấy được lên ảnh).
"""

import numpy as np
from PIL import Image

_DELIMITER = "###END###"


class InvisibleWatermark:

    @staticmethod
    def apply(input_path, output_path, owner):
        image = Image.open(input_path).convert("RGB")
        pixels = np.array(image)

        payload = owner + _DELIMITER
        bits = "".join(format(ord(c), "08b") for c in payload)

        flat = pixels.flatten()

        if len(bits) > len(flat):
            raise ValueError("Ảnh quá nhỏ để chứa watermark vô hình này")

        for i, bit in enumerate(bits):
            flat[i] = (flat[i] & 0xFE) | int(bit)

        watermarked_pixels = flat.reshape(pixels.shape).astype(np.uint8)
        result = Image.fromarray(watermarked_pixels, mode="RGB")
        result.save(output_path)

        return output_path

    @staticmethod
    def extract(image_path):
        image = Image.open(image_path).convert("RGB")
        pixels = np.array(image).flatten()

        bits = [str(pixels[i] & 1) for i in range(len(pixels))]

        chars = []
        delimiter_len = len(_DELIMITER)

        for i in range(0, len(bits) - 8, 8):
            byte = "".join(bits[i:i + 8])
            chars.append(chr(int(byte, 2)))

            # Bug hiệu năng cũ: join lại toàn bộ chars mỗi vòng lặp
            # (O(n^2) với ảnh lớn). Sửa: chỉ kiểm tra `delimiter_len`
            # ký tự cuối cùng vừa tích lũy.
            if len(chars) >= delimiter_len and "".join(chars[-delimiter_len:]) == _DELIMITER:
                return "".join(chars[:-delimiter_len])

        return None