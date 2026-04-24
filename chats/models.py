from django.db import models

from chats.constants import MessageType
from chats.storages import chat_media_upload_path
from utils.storages import ProtectedStorage
from utils.mixins import AutoDateMixin


class ChatRoom(AutoDateMixin):
    """Комната чата. Связана с бронированием (один к одному)."""
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='chat',
        null=True,
        blank=True
    )
    participants = models.ManyToManyField(
        'users.User',
        related_name='chats'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f'Chat for booking {self.booking_id}'


class Message(AutoDateMixin):
    """Сообщение в чате"""
    chat = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        to='users.User',
        on_delete=models.SET_NULL,
        null=True,
    )
    text = models.CharField(verbose_name='Сообщение', max_length=4000, blank=True)
    original_filename = models.CharField(
        verbose_name='Изначальное название файла',
        max_length=500,
        blank=True,
        default='',
    )
    media_file = models.FileField(
        verbose_name='Прикрепленный файл',
        upload_to=chat_media_upload_path,
        storage=ProtectedStorage,
        blank=True,
        null=True,
    )
    message_type = models.CharField(
        verbose_name='Тип файла',
        max_length=100,
        choices=MessageType.choices,
        default=MessageType.TEXT,
    )
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f"Message #{self.id} {self.sender.username}: {self.text[:20]}"
