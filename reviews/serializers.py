from drf_spectacular.utils import extend_schema
from rest_framework import serializers

from reviews.models import Review


class ReviewInputSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(allow_blank=True)


class ReviewOutputSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()
    booking_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(allow_blank=True)

    @staticmethod
    def get_reviewer_name(obj) -> str:
        return obj.reviewer.full_name
