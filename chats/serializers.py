from rest_framework import serializers
from .models import Message, ChatRoom
from users.serializers import UserBaseSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserBaseSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'dt_created', 'is_read']


class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants = UserBaseSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'booking', 'participants', 'messages', 'dt_created']