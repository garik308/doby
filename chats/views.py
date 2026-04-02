from rest_framework import generics

from chats.models import ChatRoom
from chats.serializers import ChatRoomSerializer


class ChatRoomDetailView(generics.RetrieveAPIView):
    """Получение информации о комнате + всех сообщений"""

    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        # Пользователь может видеть только свои чаты
        user = self.request.user
        return ChatRoom.objects.filter(participants=user)