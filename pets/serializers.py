from rest_framework import serializers

from pets.models import Pet, PetPhoto


class PetPhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PetPhoto
        fields = ('id', 'image', 'image_url', 'order_number', 'is_main')
        extra_kwargs = {
            'image': {'write_only': True},
        }

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class PetSerializer(serializers.ModelSerializer):
    """Сериализатор питомца"""

    pet_type_display = serializers.CharField(source='get_pet_type_display', read_only=True)
    owner_uuid = serializers.UUIDField(source='owner.uuid', read_only=True)
    photos = PetPhotoSerializer(many=True, read_only=True)
    warning_tags = serializers.ListField()
    specific_features = serializers.ListField()
    uploaded_photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Pet
        fields = ('id', 'pet_type', 'pet_type_display', 'owner_uuid', 'name', 'age', 'height', 'uploaded_photos',
            'weight', 'breed_name', 'diet_type', 'diet_pattern', 'warning_tags', 'specific_features',
            'diet_additional_info', 'photos', 'dt_created', 'dt_updated')
        read_only_fields = ('id', 'dt_created', 'dt_updated')


class PetUpdateSerializer(PetSerializer):
    """Сериализатор питомца для обновления"""
    photo_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Pet
        fields = ('id', 'pet_type', 'pet_type_display', 'owner_uuid', 'name', 'age', 'height', 'uploaded_photos',
            'weight', 'breed_name', 'diet_type', 'diet_pattern', 'warning_tags', 'specific_features', 'photo_ids',
            'diet_additional_info', 'photos', 'dt_created', 'dt_updated')
        read_only_fields = ('id', 'dt_created', 'dt_updated')
