import logging
import os
from config import LOG_FOLDER

_LOG_FILE = os.path.join(LOG_FOLDER, "app.log")


def get_logger(name: str) -> logging.Logger:
    """
    Trả về logger ghi đồng thời ra console và file logs/app.log.
    Dùng logging chuẩn thay vì print() rải rác để dễ trace lỗi production.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Tránh add handler trùng lặp nếu get_logger được gọi nhiều lần
        # với cùng tên (vd reload module trong debug mode).
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    os.makedirs(LOG_FOLDER, exist_ok=True)

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger