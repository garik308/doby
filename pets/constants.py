from django.db import models


class PetType(models.TextChoices):
    """Типы домашнихних животных"""
    DOG = 'dog', 'Собака'
    CAT = 'cat', 'Кошка'
    PARROT = 'parrot', 'Попугай'
    HAMSTER = 'hamster', 'Хомяк'
    OTHER = 'other', 'Другое'
