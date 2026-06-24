# pets/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from pets.models import Pet, PetPhoto
from tests.factories import UserFactory

class PetFactory(DjangoModelFactory):
    class Meta:
        model = Pet

    owner = factory.SubFactory(UserFactory)
    name = factory.Faker('first_name')
    pet_type = 'dog'
    age = 2
    height = 50
    weight = 20
    breed_name = 'Labrador'

class PetPhotoFactory(DjangoModelFactory):
    class Meta:
        model = PetPhoto

    pet = factory.SubFactory(PetFactory)
    image = factory.django.ImageField(filename='test.jpg')
    order_number = 1
    is_main = False