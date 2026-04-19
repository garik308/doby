import datetime
import os
import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage



class ProtectedStorage(FileSystemStorage):

    def __init__(self):
        super().__init__(location=settings.PROTECTED_MEDIA_ROOT, base_url=settings.PROTECTED_MEDIA_URL)


def chat_media_upload_path(instance, filename):
    """
    Генерирует путь: chats/YYYY/MM/DD/uuid.ext
    Также сохраняет оригинальное имя и сгенерированное UUID-имя в поля модели.
    """

    ext = filename.split('.')[-1].lower()
    if ext not in ['mp4', 'mov', 'mp3', 'jpg', 'png', 'pdf']:
        ext = 'bin'

    uuid_name = f"{uuid.uuid4().hex}.{ext}"
    instance.original_filename = filename

    date_path = datetime.datetime.now(datetime.UTC).strftime('%Y/%m/%d')

    return os.path.join('chats', date_path, uuid_name)