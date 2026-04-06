"""Factory для тестов чата."""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from chats.models import ChatRoom, Message
from bookings.models import Booking
from pets.models import Pet
from pets.constants import PetType

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n:04d}')
    email = factory.Sequence(lambda n: f'user_{n:04d}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True


class PetFactory(DjangoModelFactory):
    """Фабрика питомцев."""

    class Meta:
        model = Pet

    pet_type = PetType.DOG
    name = factory.Faker('first_name')
    age = factory.Faker('random_int', min=1, max=15)
    owner = factory.SubFactory(UserFactory)


class BookingFactory(DjangoModelFactory):
    class Meta:
        model = Booking

    owner = factory.SubFactory(UserFactory)
    sitter = factory.SubFactory(UserFactory)
    pet = factory.SubFactory(PetFactory, owner=factory.SelfAttribute('..owner'))
    start_datetime = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))
    end_datetime = factory.LazyFunction(lambda: timezone.now() + timedelta(days=2))
    status = 'pending'


class ChatRoomFactory(DjangoModelFactory):
    """Фабрика чатов."""

    class Meta:
        model = ChatRoom

    # Создаём новый booking только если он не передан явно
    booking = None

    @factory.post_generation
    def participants(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for user in extracted:
                self.participants.add(user)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Если booking не передан, создаём новый через SubFactory
        if kwargs.get('booking') is None:
            kwargs['booking'] = BookingFactory()
        
        # Если для этого booking уже есть ChatRoom, возвращаем его
        booking = kwargs.get('booking')
        if booking and hasattr(booking, 'chat'):
            return booking.chat
        
        return super()._create(model_class, *args, **kwargs)


class MessageFactory(DjangoModelFactory):
    """Фабрика сообщений."""

    class Meta:
        model = Message

    chat = factory.SubFactory(ChatRoomFactory)
    sender = factory.SubFactory(UserFactory)
    text = factory.Faker('sentence', nb_words=5)
