# Celery app для Django проекта
# Это гарантирует, что Celery app загружается при импорте doby
from .celery import app as celery_app

__all__ = ('celery_app',)
