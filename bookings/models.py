from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings

from bookings.constants import BookingStatus
from utils.mixins import AutoDateMixin


class Booking(AutoDateMixin):
    """Модель бронирования (заказа) на услуги ситтера."""

    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='owner_bookings',
        verbose_name='Собачник',
        null=True,
        blank=True,
    )
    sitter = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='sitter_bookings',
        verbose_name='Ситтер',
        null=True,
        blank=True,
    )
    pet = models.ForeignKey(
        'pets.Pet',
        on_delete=models.CASCADE,
        verbose_name='Питомец',
        null=True,
    )
    start_datetime = models.DateTimeField(verbose_name='Начало')
    end_datetime = models.DateTimeField(verbose_name='Конец')
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name='Статус'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий к заказу'
    )
    sitter_confirmed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Время подтверждения ситтером'
    )

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        # Уникальность не нужна, можно добавить индексы для частых фильтров
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['sitter', 'status']),
            models.Index(fields=['start_datetime']),
        ]

    def __str__(self):
        return f'Booking #{self.id}: {self.owner} -> {self.sitter} ({self.pet})'

    def clean(self):
        """Валидация на уровне модели"""
        if self.start_datetime and self.end_datetime:
            if self.start_datetime >= self.end_datetime:
                raise ValidationError('Дата окончания должна быть позже даты начала')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)