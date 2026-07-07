from utils.logger import get_logger

_logger = get_logger("app")


def log_event(action: str, filename: str, detail: str = ""):
    _logger.info(f"action={action} filename={filename} {detail}".strip())


def log_error(action: str, filename: str, error: str):
    _logger.error(f"action={action} filename={filename} error={error}")