import factory
from factory.django import DjangoModelFactory
from sitters.models import SitterService
from bookings.constants import ServiceTypeChoices
import random

class SitterServiceFactory(DjangoModelFactory):
    class Meta:
        model = SitterService

    sitter = factory.SubFactory('tests.factories.SitterProfileFactory')
    service_type = factory.Iterator([choice[0] for choice in ServiceTypeChoices.choices])
    price = factory.LazyAttribute(lambda _: random.randint(300, 2000))
    is_active = True