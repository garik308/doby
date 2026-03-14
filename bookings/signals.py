from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from chats.models import ChatRoom

@receiver(post_save, sender=Booking)
def create_chat_for_booking(sender, instance, created, **kwargs):
    if created:
        # Создаём комнату чата
        chat = ChatRoom.objects.create(booking=instance)
        # Добавляем участников (owner и sitter)
        chat.participants.add(instance.owner, instance.sitter)