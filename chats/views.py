import mimetypes
from os import path

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.utils.encoding import escape_uri_path
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from chats.constants import MessageType
from chats.models import ChatRoom, Message
from chats.serializers import ChatRoomSerializer, MessageSerializer


class ChatRoomDetailView(generics.RetrieveAPIView):
    """Получение информации о комнате"""

    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        return ChatRoom.objects.filter(
            id__in=(
                ChatRoom.participants.through.objects.filter(user=self.request.user)
                .values_list('chatroom_id', flat=True)
            ),
        )


class MessageMediaRetrieveView(APIView):

    @extend_schema(
        summary=__doc__,
        description=(
            'Возвращает защищённый медиафайл, используя внутренний редирект на Nginx. '
            'Доступ возможен только для участников чата.'
        ),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description='Файл успешно получен. Будет возвращён бинарный поток данных.',
                response={'application/octet-stream': {}},
            ),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(description='Доступ запрещён.'),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(description='Сообщение или файл не найдены.'),
        },
    )
    def get(self, request, message_id):
        message = get_object_or_404(Message, sender=request.user, id=message_id)

        if not (
            ChatRoom.participants.through
            .objects.filter(user=self.request.user, chatroom_id=message.chat_id)
            .exists()
        ):
            raise PermissionDenied("Это сообщение не из вашего чата")

        if not message.media_file:
            raise Http404("У сообщения отсутствует прикрепленное медиа")

        relative_path = message.media_file.name
        internal_uri = path.join(settings.PROTECTED_MEDIA_URL, relative_path)
        content_type, _ = mimetypes.guess_type(relative_path)
        if not content_type:
            content_type = 'application/octet-stream'

        # Используем HttpResponse, а не DRF Response, чтобы избежать лишних рендереров.
        response = HttpResponse()
        response['X-Accel-Redirect'] = internal_uri
        response['Content-Type'] = content_type
        response['Content-Disposition'] = f"inline; filename*=UTF-8''{escape_uri_path(message.original_filename)}"
        return response


class CreateMessageSerializer(serializers.ModelSerializer):
    chat = serializers.PrimaryKeyRelatedField(
        queryset=ChatRoom.objects.all(),
        write_only=True,
    )
    text = serializers.CharField(allow_blank=True, max_length=5000)
    media_file = serializers.FileField()

    class Meta:
        model = Message
        fields = ('chat', 'text', 'media_file')

    def validate_media_file(self, value):
        """Валидация размера и типа файла"""
        if value:
            if value.size > 50 * 1024 * 1024:
                raise serializers.ValidationError("File too large (max 50MB)")
        return value


class MessageCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Создать сообщение в чате",
        description=(
                "Отправляет текстовое сообщение и/или файл в указанную комнату.\n"
                "Файл будет сохранён с уникальным именем (UUID) в защищённом хранилище.\n"
                "Доступ только для участников чата."
        ),
        request=CreateMessageSerializer,
        responses={
            201: MessageSerializer,
            400: OpenApiResponse(description="Ошибка валидации (неверные поля, слишком большой файл)"),
            403: OpenApiResponse(description="Вы не участник этого чата"),
            404: OpenApiResponse(description="Чат не найден"),
        },
    )
    def post(self, request):
        serializer = CreateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chat = serializer.validated_data['chat']
        text = serializer.validated_data['text']
        media_file = serializer.validated_data.get('media_file')

        if not chat.participants.filter(id=request.user.id).exists():
            return Response({'error': 'Not a participant'}, status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            text=text,
            message_type=MessageType.from_extension(media_file.name.split('.')[-1]),
            original_filename=media_file.name,
            media_file=media_file,
        )

        message_data = MessageSerializer(message).data
        async_to_sync(get_channel_layer().group_send)(
            f'chat_{chat.id}',
            {
                'type': 'chat_message',
                **message_data,
            },
        )
        return Response(message_data, status=status.HTTP_201_CREATED)