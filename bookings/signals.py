from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from chats.models import ChatRoom

@receiver(post_save, sender=Booking)
def create_chat_for_booking(sender, instance, created, **kwargs):
    if created:
        # Создаём комнату чата, если она ещё не существует
        chat, chat_created = ChatRoom.objects.get_or_create(booking=instance)
        if chat_created:
            # Добавляем участников (owner и sitter)
            chat.participants.add(instance.owner, instance.sitter)