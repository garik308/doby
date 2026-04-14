from rest_framework import serializers

from users.models import User
from users.serializers import UserBaseSerializer


class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.EmailField(label='Почта')

    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'min_length': 8}}


class OutputUserRegisterSerializer(serializers.Serializer):
    user = UserBaseSerializer(label='Данные о пользователе')
    access_token = serializers.CharField(label='Токен доступа')
    refresh_token = serializers.CharField(label='Токен для обновления access_token')



class UserLoginSerializer(serializers.Serializer):
    username = serializers.EmailField(label='Почта')
    password = serializers.CharField(label='Пароль', min_length=8)


class OutputUserLoginSerializer(serializers.Serializer):
    user = UserBaseSerializer(label='Данные о пользователе')
    access_token = serializers.CharField(label='Токен доступа')
    refresh_token = serializers.CharField(label='Токен для обновления access_token')


# class SitterRegisterSerialzer(serializers.Serializer):
#     id = serializers.IntegerField(label='Идентификатор ситтера')
#     experience_years = serializers.IntegerField(label='Количество лет опыта')
#     price_per_hour = serializers.DecimalField(
#         label='Стоимость в час',
#         max_digits=6,
#         decimal_places=2,
#         allow_null=True,
#     )
#     bio = serializers.CharField(label='Описание ситтера', max_length=1500)
#
#
# class ComplexSitterRegisterSerializer(serializers.Serializer):
#     user_data = UserRegisterSerializer(label='Данные для регистрации юзера')
#     sitter_data = SitterRegisterSerialzer(label='Данные ситтера')
#
#
# class OutputSitterRegisterSerializer(serializers.Serializer):
#     user = UserSerializer(label='Данные о пользователе')
#     sitter = SitterSerialzer(label='Данные о ситтере')
#     access_token = serializers.CharField(label='Токен доступа')
#     refresh_token = serializers.CharField(label='Токен для обновления access_token')