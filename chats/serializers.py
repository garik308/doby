from rest_framework import serializers
from rest_framework.reverse import reverse

from .constants import MessageType
from .models import Message, ChatRoom
from users.serializers import UserBaseSerializer


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    sender_uuid = serializers.CharField(source='sender.uuid', read_only=True)
    text = serializers.CharField(label='Текст сообщения', allow_blank=True, max_length=4000)
    original_filename = serializers.CharField(label='Изначальное название файла', max_length=500, allow_blank=True)
    message_type = serializers.ChoiceField(label='Тип файла', choices=MessageType.choices)
    is_read = serializers.BooleanField(default=False)
    dt_created = serializers.DateTimeField(label='Дата создания', read_only=True)
    media_url = serializers.SerializerMethodField(help_text='Ссылка на скачивание медиафайла (требует аутентификации)')

    @staticmethod
    def get_media_url(obj):
        if obj.media_file:
            return reverse('chat_message_media_retrieve', args=[obj.id])
        return None


class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants = UserBaseSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'booking', 'participants', 'messages', 'dt_created']
