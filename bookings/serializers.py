from rest_framework import serializers

from bookings.constants import ServiceTypeChoices
from bookings.models import Booking

class BookingInputSerializer(serializers.Serializer):
    pet_id = serializers.IntegerField()
    sitter_uuid = serializers.UUIDField(help_text='UUID ситтера')
    service = serializers.ChoiceField(choices=ServiceTypeChoices.choices)
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    comment = serializers.CharField(required=False, allow_blank=True)


class BookingActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['accept', 'reject', 'complete'])


class BookingOutputSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.fullname', read_only=True)
    sitter_name = serializers.CharField(source='sitter.user.fullname', read_only=True)
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    class Meta:
        model = Booking
        fields = '__all__'