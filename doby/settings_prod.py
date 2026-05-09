from settings import *

SECRET_KEY = Env.get_str('DJANGO_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = Env.get_list('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = Env.get_list('CSRF_TRUSTED_ORIGINS')