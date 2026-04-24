import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """Консьюмер для чатов"""

    async def connect(self):
        """Вызывается при попытке клиента подключиться к WebSocket."""
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        user = self.scope['user']
        if user.is_anonymous:
            await self.close()

        if not await self.is_participant(user.id, self.chat_id):
            await self.close()

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """При отключении удаляем пользователя из группы."""
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """Получение сообщения от клиента."""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format. Expected: {"message": "text"}'
            }))
            return
        
        message_text = data.get('message', '')
        user = self.scope['user']
        saved_message = await self.save_message(user, self.chat_id, message_text)
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                **MessageSerializer(saved_message).data,
            },
        )

    async def chat_message(self, event):
        """
        Отправка сообщения обратно в WebSocket клиенту.
        """
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def is_participant(self, user_id, chat_id):
        """
        Проверяет, является ли пользователь участником комнаты.
        """
        return ChatRoom.participants.through.objects.filter(chatroom_id=chat_id, user_id=user_id).exists()

    @database_sync_to_async
    def save_message(self, user, chat_id, text):
        """
        Сохраняет сообщение в БД.
        """
        return Message.objects.create(chat_id=chat_id, sender=user, text=text)
