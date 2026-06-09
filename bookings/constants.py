from django.db import models


class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Ожидает подтверждения'
    CONFIRMED = 'confirmed', 'Подтверждено'
    REJECTED = 'rejected', 'Отклонено ситтером'
    CANCELLED_BY_OWNER = 'cancelled_by_owner', 'Отменено собачником'
    CANCELLED_BY_SITTER = 'cancelled_by_sitter', 'Отменено ситтером'
    COMPLETED = 'completed', 'Завершено'


class ServiceTypeChoices(models.TextChoices):
    BOARDING = 'boarding', 'Передержка'
    WALKING = 'walking', 'Выгул'
    GROOMING = 'grooming', 'Груминг'
    TRAINING = 'training', 'Дрессировка'

# Базовая стоимость (можно вынести в отдельный словарь)
SERVICE_BASE_PRICE = {
    ServiceTypeChoices.BOARDING: 1000,
    ServiceTypeChoices.WALKING: 500,
    ServiceTypeChoices.GROOMING: 1500,
    ServiceTypeChoices.TRAINING: 2000,
}
SERVICE_UNIT = {
    ServiceTypeChoices.BOARDING: 'day',
    ServiceTypeChoices.WALKING: 'hour',
    ServiceTypeChoices.GROOMING: 'hour',
    ServiceTypeChoices.TRAINING: 'hour',
}