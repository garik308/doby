import datetime
import os
import uuid

from utils.file_type import IMAGE_EXTENSIONS


def pet_photo_upload_path(instance, filename):
    """Генерирует путь: pets/photos/YYYY/MM/DD/uuid.ext"""

    ext = filename.split('.')[-1].lower()
    if ext not in IMAGE_EXTENSIONS:
        ext = 'bin'

    uuid_name = f'{uuid.uuid4().hex}.{ext}'
    date_path = datetime.datetime.now(datetime.UTC).strftime('%Y/%m/%d')

    return os.path.join('pets/photos', date_path, uuid_name)
