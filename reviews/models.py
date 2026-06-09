from django.conf import settings
from django.db import models

from bookings.models import Booking
from sitters.models import SitterProfile
from utils.mixins import AutoDateMixin


class Review(AutoDateMixin):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    sitter = models.ForeignKey(SitterProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 5+1)], help_text="1-5")
    comment = models.CharField(max_length=1500, blank=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
