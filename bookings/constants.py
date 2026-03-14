from django.db import models


class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидает подтверждения'
    CONFIRMED = 'confirmed', 'Подтверждено'
    REJECTED = 'rejected', 'Отклонено ситтером'
    CANCELLED_BY_OWNER = 'cancelled_by_owner', 'Отменено собачником'
    CANCELLED_BY_SITTER = 'cancelled_by_sitter', 'Отменено ситтером'
    COMPLETED = 'completed', 'Завершено'