import os

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg"}


def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


def allowed_image(filename: str) -> bool:
    return get_extension(filename) in ALLOWED_IMAGE_EXTENSIONS


def safe_join(folder: str, filename: str) -> str:
    """
    Ghép đường dẫn an toàn, chặn path traversal (vd filename =
    "../../config.py"). Ném ValueError nếu phát hiện cố vượt ra ngoài
    thư mục gốc `folder`.
    """
    folder_abs = os.path.abspath(folder)
    target_abs = os.path.abspath(os.path.join(folder_abs, filename))

    if not target_abs.startswith(folder_abs + os.sep) and target_abs != folder_abs:
        raise ValueError(f"Đường dẫn không hợp lệ: {filename}")

    return target_abs


def file_size_bytes(path: str) -> int:
    return os.path.getsize(path)