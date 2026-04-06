import pytest
from asgiref.sync import sync_to_async
import json
import os
from django.db import connection

from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from rest_framework_simplejwt.tokens import AccessToken

from chats.middleware import JWTAuthMiddleware
from chats.models import ChatRoom, Message
from chats.factories import ChatRoomFactory, UserFactory, BookingFactory
from chats.routing import websocket_urlpatterns
from django.contrib.auth import get_user_model
from bookings.models import Booking
from pets.models import Pet


User = get_user_model()


pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def app():
    """ASGI приложение доступно для всех тестов."""
    return AllowedHostsOriginValidator(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    )


@pytest.fixture
async def chat_room_async():
    """Асинхронная фикстура для создания данных."""
    # Используем sync_to_async, чтобы создание в БД прошло корректно внутри цикла событий
    def create_data():
        owner = UserFactory()
        sitter = UserFactory()
        booking = BookingFactory(owner=owner, sitter=sitter)
        chat = ChatRoomFactory(booking=booking)
        chat.participants.add(owner, sitter)
        return chat, owner

    return await sync_to_async(create_data)()


@pytest.mark.asyncio
async def test_websocket_connect_and_send_message(app, chat_room_async):
    chat_room, user = chat_room_async
    token = AccessToken.for_user(user)

    communicator = WebsocketCommunicator(
        app,
        f"/ws/chat/{chat_room.id}/?token={str(token)}"
    )
    connected, _ = await communicator.connect()
    assert connected
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_websocket_reject_anonymous(app, transactional_db):
    chat = await sync_to_async(ChatRoomFactory)()
    communicator = WebsocketCommunicator(app, f"/ws/chat/{chat.id}/?token=random_invalid_token")
    connected, _ = await communicator.connect()
    assert not connected

