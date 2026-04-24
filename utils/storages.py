from django.conf import settings
from django.core.files.storage import FileSystemStorage


class ProtectedStorage(FileSystemStorage):

    def __init__(self):
        super().__init__(location=settings.PROTECTED_MEDIA_ROOT, base_url=settings.PROTECTED_MEDIA_URL)
