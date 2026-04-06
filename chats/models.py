from django.db import models

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
    """
    Сообщение в чате.
    """
    chat = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )
    text = models.CharField(verbose_name='Сообщение', max_length=100)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f"Message #{self.id} {self.sender.username}: {self.text[:20]}"