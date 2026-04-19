from rest_framework.reverse import reverse

from chats.models import Message


def create_ws_text_message_data(message: Message) -> dict:
    return {
        'type': 'chat_message',  # это имя метода, который будет вызван
        'message_type': message.message_type,
        'message_id': message.id,
        'message': message.text,
        'sender_uuid': str(message.sender.uuid),
        'dt_created': message.dt_created.isoformat(),
        'is_read': message.is_read,
        'media': {
            'original_filename': message.original_filename,
            'media_url': reverse('chat_message_media_retrieve', args=[message.id]),
        } if message.media_file else None,
    }
