from rest_framework import serializers

from pets.models import Pet


class PetSerializer(serializers.ModelSerializer):
    """Сериализатор питомца"""

    pet_type_display = serializers.CharField(source='get_pet_type_display', read_only=True)
    owner_uuid = serializers.UUIDField(source='owner.uuid', read_only=True)

    class Meta:
        model = Pet
        fields = ('id', 'pet_type', 'pet_type_display', 'name', 'age', 'owner_uuid', 'height', 'weight', 'breed_name', 'dt_created', 'dt_updated')
        read_only_fields = ('dt_created', 'dt_updated')


class PetCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания/обновления питомца"""

    class Meta:
        model = Pet
        fields = ('pet_type', 'name', 'age', 'height', 'weight', 'breed_name')
