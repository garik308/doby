from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.constants import BookingStatus
from bookings.models import Booking
from reviews.models import Review
from reviews.serializers import ReviewInputSerializer, ReviewOutputSerializer
from sitters.models import SitterProfile


class ReviewCreateView(APIView):

    @extend_schema(
        request=ReviewInputSerializer,
        responses={status.HTTP_201_CREATED: None, status.HTTP_4: "Ошибка"}
    )
    def post(self, request):
        input_serializer = ReviewInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        booking = get_object_or_404(Booking, id=data['booking_id'], owner=request.user)
        if booking.status != BookingStatus.COMPLETED:
            return Response({'error': 'Заказ не завершен'}, status=400)
        if hasattr(booking, 'review'):
            return Response({'error': 'Отзыв уже существует'}, status=400)

        with transaction.atomic():
            review = Review.objects.create(
                booking=booking,
                reviewer=request.user,
                target=booking.sitter,
                rating=data['rating'],
                comment=data['comment'],
            )
            avg_rating = Review.objects.filter(target=booking.sitter).aggregate(avg=Avg('rating'))['avg']
            sitter_profile = booking.sitter
            sitter_profile.rating = avg_rating
            sitter_profile.save()

        return Response(status=status.HTTP_201_CREATED)


class MyReviewsView(APIView):

    @extend_schema(responses={status.HTTP_200_OK: ReviewOutputSerializer(many=True)})
    def get(self, request):
        reviews = Review.objects.filter(reviewer=request.user).order_by('-created_at')
        serializer = ReviewOutputSerializer(reviews, many=True)
        return Response(serializer.data)


class SitterReviewsView(APIView):

    @extend_schema(responses={status.HTTP_200_OK: ReviewOutputSerializer(many=True)})
    def get(self, request, sitter_uuid):
        reviews = Review.objects.filter(sitter_id=sitter_uuid).order_by('-created_at')
        serializer = ReviewOutputSerializer(reviews, many=True)
        return Response(serializer.data)
