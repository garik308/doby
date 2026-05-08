from settings import *

DEBUG = False
ALLOWED_HOSTS = Env.get_list('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = Env.get_list('CSRF_TRUSTED_ORIGINS')