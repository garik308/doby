import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """Консьюмер для чатов <UNK> <UNK>"""

    async def connect(self):
        """Вызывается при попытке клиента подключиться к WebSocket."""
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        elif await self.is_participant(user.id, self.chat_id):
            # Добавляем пользователя в группу (channel layer)
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """При отключении удаляем пользователя из группы."""
        await self.channel_layer.group_discard(
            self.room_group_name,
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
        
        message_text = data.get('message')
        if not message_text:
            await self.send(text_data=json.dumps({
                'error': 'Missing "message" field in request'
            }))
            return

        user = self.scope['user']

        # Сохраняем сообщение в базу данных
        saved_message = await self.save_message(user, self.chat_id, message_text)

        # Отправляем сообщение всем в группе (включая отправителя)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # это имя метода, который будет вызван
                'message': message_text,
                'sender_uuid': str(user.uuid),
                'sender_username': user.username,
                'dt_created': saved_message.dt_created.isoformat(),
                'message_id': saved_message.id,
            }
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
