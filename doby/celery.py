"""
Celery configuration for doby project.
"""
import os
from celery import Celery
from celery.schedules import crontab

from doby.env_interface import Env

# Устанавливаем переменную окружения Django
settings_module = 'doby.settings_prod' if Env.get_bool('DEBUG') else "doby.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

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
