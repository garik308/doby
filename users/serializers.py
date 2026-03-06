from rest_framework import serializers


class SitterProfileSerializer(serializers.Serializer):
    experience_years = serializers.IntegerField(allow_null=True, required=False)
    price_per_hour = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        allow_null=True,
        required=False
    )
    is_verified = serializers.BooleanField(read_only=True)


class CitySerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    translit = serializers.CharField(read_only=True)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    avatar = serializers.ImageField(allow_null=True)
    phone = serializers.CharField(max_length=15)
    city = CitySerializer(label='Город', )
    bio = serializers.CharField(max_length=500, allow_blank=True)
    sitter_profile = SitterProfileSerializer(read_only=True)
