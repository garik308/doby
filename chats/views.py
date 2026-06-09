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

from bookings.models import Booking
from chats.constants import MessageType
from chats.models import ChatRoom, Message
from chats.serializers import ChatRoomSerializer, MessageSerializer, ChatRoomCreateSerializer
from users.models import User


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


class ChatRoomCreateView(APIView):
    output_serializer = ChatRoomSerializer

    @extend_schema(
        summary='Создать чат',
        description=(
            'Создаёт новый чат. Текущий пользователь добавляется автоматически. '
            'Если передан `booking_id`, чат привязывается к бронированию (только один чат на бронирование). '
            'Если `booking_id` не передан и количество уникальных участников равно 2, '
            'возвращается существующий личный чат (без бронирования) между этими пользователями.'
        ),
        request=ChatRoomCreateSerializer,
        responses={
            200: output_serializer,
            201: output_serializer,
            400: OpenApiResponse(description='Ошибка валидации'),
        }
    )
    def post(self, request):
        serializer = ChatRoomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        participants_ids = set(data['participants'])
        booking_id = data.get('booking_id')

        participants_ids.add(request.user.uuid)
        participants_list = list(participants_ids)

        existing_users_ids = User.objects.filter(uuid__in=participants_list).values_list('id', flat=True)
        if len(existing_users_ids) != len(participants_list):
            return Response(
                {'participants': f'Пользователи с UUID не найдены.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking_id is not None:
            booking = get_object_or_404(Booking, id=booking_id)
            if hasattr(booking, 'chat') and booking.chat is not None:
                return Response(
                    {'booking_id': 'К этому бронированию уже привязан чат.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not booking_id and len(participants_list) == 2:
            existing_chat = ChatRoom.objects.filter(
                participants__uuid=participants_list[0]
            ).filter(
                participants__uuid=participants_list[1]
            ).filter(
                booking__isnull=True
            ).distinct().first()

            if existing_chat:
                return Response(
                    self.output_serializer(existing_chat).data,
                    status=status.HTTP_200_OK
                )

        chat = ChatRoom.objects.create()
        if booking_id:
            chat.booking = booking
            chat.save()
        chat.participants.add(*existing_users_ids)

        return Response(
            self.output_serializer(chat).data,
            status=status.HTTP_201_CREATED
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