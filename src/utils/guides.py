import os
from datetime import datetime
from pathlib import Path

from core.constants import MEDIA_ROOT


def create_upload_path(directory: str, filename: str):
    if not os.path.exists(directory):
        Path(directory).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(directory + filename):
        filename_parts = filename.split(".")
        timestamp = str(int(datetime.now().timestamp()))
        filename = "".join(filename_parts[:-1]) + "_" + timestamp + "." + filename_parts[-1]
    open(f'{directory}{filename}', 'wb').close()
    return directory + filename


def get_featured_image_upload_path(guide_id: str, filename: str):
    directory = f"{MEDIA_ROOT}/guides/{guide_id}/cover_image/"
    path = create_upload_path(directory, filename)
    path_to_save = 'media' + path.split('media')[1]
    return path_to_save
