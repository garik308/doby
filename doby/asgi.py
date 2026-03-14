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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doby.settings')
django.setup()

from chats.middleware import JWTAuthMiddleware
from chats.routing import websocket_urlpatterns

asgi = get_asgi_application()

application = ProtocolTypeRouter({
    'http': asgi,
    'websocket': (
        # AllowedHostsOriginValidator(
        # JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns),
        # ),
        # ),
    )
})