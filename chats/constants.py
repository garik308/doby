from django.db.models import TextChoices

from utils.file_type import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, AUDIO_EXTENSIONS


class MessageType(TextChoices):

    AUDIO = 'audio', 'Аудиосообщение'
    VIDEO = 'video', 'Видеосообщение'
    IMAGE = 'image', 'Фотография'
    FILE = 'file', 'Файл'
    TEXT = 'text', 'Текст'

    @classmethod
    def from_extension(cls, extension: str) -> 'MessageType':
        if extension.lower() in IMAGE_EXTENSIONS:
            return MessageType.IMAGE
        if extension.lower() in VIDEO_EXTENSIONS:
            return MessageType.VIDEO
        if extension.lower() in AUDIO_EXTENSIONS:
            return MessageType.AUDIO
        return MessageType.FILE
