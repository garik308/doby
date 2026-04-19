import magic
from typing import Tuple


IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'tiff', 'ico'}
VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'mpeg', 'ogv'}
AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac'}
DOCUMENT_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'html',
    'css', 'js', 'json', 'xml', 'zip', 'rar', '7z', 'tar', 'gz',
}
SYSTEM_EXTENSIONS = {'bin', 'exe', 'so', 'o', 'dll', 'msi'}

MIME_IMAGE_MAP = {
    # Изображения
    'image/jpeg': 'jpg',
    'image/jpg': 'jpg',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/webp': 'webp',
    'image/bmp': 'bmp',
    'image/svg+xml': 'svg',
    'image/tiff': 'tiff',
    'image/x-icon': 'ico',
}
MIME_VIDEO_MAP = {
    'video/mp4': 'mp4',
    'video/quicktime': 'mov',
    'video/x-msvideo': 'avi',
    'video/x-matroska': 'mkv',
    'video/webm': 'webm',
    'video/mpeg': 'mpeg',
    'video/ogg': 'ogv',
}
MIME_AUDIO_MAP = {
    'audio/mpeg': 'mp3',
    'audio/wav': 'wav',
    'audio/ogg': 'ogg',
    'audio/mp4': 'm4a',
    'audio/x-m4a': 'm4a',
    'audio/flac': 'flac',
    'audio/aac': 'aac',
}
MIME_DOCUMENT_MAP = {
    'application/pdf': 'pdf',
    'application/msword': 'doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-powerpoint': 'ppt',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'text/plain': 'txt',
    'text/html': 'html',
    'text/css': 'css',
    'text/javascript': 'js',
    'application/json': 'json',
    'application/xml': 'xml',
    'application/zip': 'zip',
    'application/x-rar-compressed': 'rar',
    'application/x-7z-compressed': '7z',
    'application/x-tar': 'tar',
    'application/gzip': 'gz',
}
MIME_SYSTEMFILES_MAP = {
    'application/x-executable': 'bin',
    'application/x-msdownload': 'exe',
    'application/x-sharedlib': 'so',
    'application/x-object': 'o',
    'application/octet-stream': 'bin',
}
MIME_FULL_MAP = (
        MIME_IMAGE_MAP | MIME_VIDEO_MAP | MIME_AUDIO_MAP | MIME_DOCUMENT_MAP | MIME_SYSTEMFILES_MAP
)


class MimeToExtension:
    """
    Инструмент для преобразования MIME-типа в расширение файла.
    Использует базу соответствий MIME -> расширение.
    """

    @classmethod
    def get_extension(cls, mime_type: str, default: str = '.bin') -> str:
        """
        Возвращает расширение для заданного MIME-типа.

        Args:
            mime_type: MIME-тип (например, 'video/mp4')
            default: расширение по умолчанию, если тип не найден

        Returns:
            Расширение с точкой (например, 'mp4')
        """
        # Приводим к нижнему регистру и удаляем параметры (например, 'text/plain; charset=utf-8')
        base_mime = mime_type.split(';')[0].strip().lower()
        return MIME_FULL_MAP.get(base_mime, default)

    @classmethod
    def get_extension_from_file(cls, file_path: str, default: str = 'bin') -> Tuple[str, str]:
        """
        Определяет MIME-тип файла через magic и возвращает подходящее расширение.

        Args:
            file_path: путь к файлу
            default: расширение по умолчанию

        Returns:
            Кортеж (mime_type, extension)
        """
        mime = magic.from_file(file_path, mime=True)
        ext = cls.get_extension(mime, default)
        return mime, ext

    @classmethod
    def validate_extension(cls, file_path: str, expected_extension: str) -> bool:
        """
        Проверяет, соответствует ли реальный MIME-тип файла ожидаемому расширению.

        Args:
            file_path: путь к файлу
            expected_extension: ожидаемое расширение (с точкой или без, например 'mp4' или 'mp4')

        Returns:
            True, если MIME-тип соответствует расширению, иначе False
        """
        # Нормализуем ожидаемое расширение
        if not expected_extension.startswith('.'):
            expected_extension = '.' + expected_extension

        mime, ext = cls.get_extension_from_file(file_path)
        return ext == expected_extension


def get_mime(file_path: str) -> str:
    """Вернуть MIME-тип файла."""
    return magic.from_file(file_path, mime=True)
