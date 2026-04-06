"""
Celery configuration for doby project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doby.settings')

# Создаем приложение Celery
app = Celery('doby')

# Загружаем конфигурацию из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автообнаружение задач во всех установленных приложениях
app.autodiscover_tasks()


# Настройка периодических задач (Celery Beat)

app.conf.timezone = 'Europe/Moscow'


@app.task(bind=True)
def debug_task(self):
    """Тестовая задача для проверки работы Celery"""
    print(f'Request: {self.request!r}')
