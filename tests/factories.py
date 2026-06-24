import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from faker import Faker


fake = Faker()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True


class SitterProfileFactory(DjangoModelFactory):
    class Meta:
        model = 'sitters.SitterProfile'

    user = factory.SubFactory(UserFactory)
    location_lat = factory.LazyAttribute(lambda _: fake.latitude())
    location_lng = factory.LazyAttribute(lambda _: fake.longitude())
    rating = 0.0
    bio = factory.Faker('text', max_nb_chars=100)


class PetFactory(DjangoModelFactory):
    class Meta:
        model = 'pets.Pet'

    owner = factory.SubFactory(UserFactory)
    name = factory.Faker('first_name')
    pet_type = 'dog'
    age = 2
    height = 50
    weight = 10
    breed_name = 'Labrador'