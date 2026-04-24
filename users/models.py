import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.mixins import AutoDateMixin


class City(models.Model):
    name = models.CharField(max_length=100)
    translit = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"


class User(AbstractUser):
    """Model: Пользователь"""

    uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True)
    first_name = models.CharField('Имя', blank=True, max_length=255)
    last_name = models.CharField('Фамилия', blank=True, max_length=255)
    patronymic = models.CharField('Отчество', blank=True, max_length=255)
    phone = models.CharField('номер телефона', max_length=15, null=True, blank=True)
    avatar = models.ImageField('аватарка', upload_to='avatars/', null=True, blank=True)
    city = models.ForeignKey(to='users.City', on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField('Информация', max_length=1500, blank=True)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self) -> str:
        return ' '.join([
            name_element for name_element in [self.first_name, self.last_name, self.patronymic] if name_element
        ])

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        constraints = [
            models.UniqueConstraint(
                'phone',
                condition=models.Q(phone__isnull=False),
                name='user_phone_unique_if_filled',
            ),
        ]


class DeletedUser(AutoDateMixin):
    """Model: удаленный пользователя"""

    user_id = models.BigIntegerField('Прошлый id пользователя')
    uuid = models.UUIDField('Прошлый UUID пользователя')
    username = models.CharField('Почта', max_length=150)
    first_name = models.CharField('Имя', blank=True, max_length=255)
    last_name = models.CharField('Фамилия', blank=True, max_length=255)
    patronymic = models.CharField('Отчество', blank=True, max_length=255)
    phone = models.CharField('Номер телефона', max_length=15, null=True, blank=True)
    city = models.ForeignKey(verbose_name='Город', to='users.City', on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField('Информация', max_length=1500, blank=True)
    bookings_as_sitter = models.JSONField('Бронирования как ситтер', null=True, blank=True)
    bookings_as_owner = models.JSONField('Бронирования как владелец', null=True, blank=True)
    pets = models.JSONField('Питомцы', null=True, blank=True)
    is_sitter = models.BooleanField('Был ли пользователь ситтером', default=False)

    @property
    def full_name(self) -> str:
        return ' '.join([
            name_element for name_element in [self.first_name, self.last_name, self.patronymic] if name_element
        ])

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Удаленный пользователь'
        verbose_name_plural = 'Удаленные пользователи'
        indexes = [
            models.Index(fields=['uuid'], name='deleted_user_uuid_idx'),
            models.Index(fields=['username'], name='deleted_username_uuid_idx'),
            models.Index(fields=['phone'], name='deleted_user_phone_idx', condition=models.Q(phone__isnull=False)),
        ]
