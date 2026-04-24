import datetime
import os
import uuid


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