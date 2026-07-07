import os
import uuid

from werkzeug.utils import secure_filename

from config import UPLOAD_FOLDER
from utils.file_utils import allowed_image
from database.database import log_audit


class UploadService:

    @staticmethod
    def allowed(filename):
        return allowed_image(filename)

    @staticmethod
    def save(file):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        safe_name = secure_filename(file.filename)

        if not safe_name:
            raise ValueError("Invalid filename")

        unique_name = f"{uuid.uuid4().hex}_{safe_name}"

        filepath = os.path.join(UPLOAD_FOLDER, unique_name)

        file.save(filepath)

        log_audit("CREATE", filename=unique_name)

        return unique_name