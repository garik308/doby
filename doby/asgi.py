"""
ASGI config for doby project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from doby.env_interface import Env

settings_module = 'doby.settings_prod' if Env.get_bool('DEBUG') else "doby.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
django.setup()

from chats.middleware import JWTAuthMiddleware
from chats.routing import websocket_urlpatterns

asgi = get_asgi_application()

application = ProtocolTypeRouter({
    'http': asgi,
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns),
        ),
    ),
})