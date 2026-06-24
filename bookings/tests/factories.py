import factory
from factory.django import DjangoModelFactory
from bookings.models import Booking
from reviews.models import Review
from tests.factories import UserFactory, PetFactory
import random
from django.utils import timezone
from datetime import timedelta

class BookingFactory(DjangoModelFactory):
    class Meta:
        model = Booking

    owner = factory.SubFactory(UserFactory)
    sitter = factory.SubFactory(UserFactory)
    pet = factory.SubFactory(PetFactory)
    service = 'walking'
    start_datetime = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))
    end_datetime = factory.LazyAttribute(lambda obj: obj.start_datetime + timedelta(hours=1))
    status = 'pending'
    comment = factory.Faker('text', max_nb_chars=50)

class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    booking = factory.SubFactory(BookingFactory)
    reviewer = factory.SelfAttribute('booking.owner')
    target = factory.SelfAttribute('booking.sitter')
    rating = factory.LazyFunction(lambda: random.randint(1, 5))
    comment = factory.Faker('text', max_nb_chars=100)