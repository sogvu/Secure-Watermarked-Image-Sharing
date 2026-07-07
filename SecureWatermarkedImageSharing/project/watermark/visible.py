from PIL import Image, ImageDraw, ImageFont


class VisibleWatermark:

    @staticmethod
    def apply(input_path, output_path, owner):
        image = Image.open(input_path).convert("RGB")

        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 40)
        except Exception:
            font = ImageFont.load_default()

        text = f"\u00a9 {owner}"

        width, height = image.size

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = max(width - text_width - 20, 0)
        y = max(height - text_height - 20, 0)

        # Bug cũ: chữ trắng (255,255,255) trên nền sáng sẽ gần như
        # vô hình. Thêm viền đen (outline) để luôn đọc được bất kể
        # màu nền của ảnh.
        outline_range = 2
        for dx in range(-outline_range, outline_range + 1):
            for dy in range(-outline_range, outline_range + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, fill=(0, 0, 0), font=font)

        draw.text((x, y), text, fill=(255, 255, 255), font=font)

        image.save(output_path)

        return output_path