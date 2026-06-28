from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiParameter
from bookings.models import Booking
from bookings.serializers import BookingInputSerializer, BookingOutputSerializer, BookingActionSerializer
from pets.models import Pet
from sitters.models import SitterProfile
from users.models import User
from bookings.constants import BookingStatus


class BookingCreateView(APIView):

    @extend_schema(
        summary="Создать новое бронирование",
        request=BookingInputSerializer,
        responses={
            status.HTTP_201_CREATED: BookingOutputSerializer,
            status.HTTP_400_BAD_REQUEST: "Ошибка валидации",
        }
    )
    def post(self, request):
        serializer = BookingInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        sitter = get_object_or_404(SitterProfile.objects.select_related('user'), uuid=data['sitter_uuid'], user__is_active=True)
        overlapping = Booking.objects.filter(
            sitter=sitter,
            start_datetime__lt=data['end_datetime'],
            end_datetime__gt=data['start_datetime'],
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        ).exists()
        if overlapping:
            return Response({'error': 'Ситтер занят в это время, попробуйте другое'}, status=400)

        pet = get_object_or_404(Pet, id=data['pet_id'], owner=request.user)
        booking = Booking.objects.create(
            owner=request.user,
            sitter=sitter,
            pet=pet,
            service=data['service'],
            start_datetime=data['start_datetime'],
            end_datetime=data['end_datetime'],
            comment=data.get('comment', ''),
            status=BookingStatus.PENDING
        )

        send_mail(
            subject='Новый запрос на бронирование',
            message=f'Пользователь {request.user.full_name} хочет забронировать услугу {booking.service} с {booking.start_datetime} по {booking.end_datetime}. Перейдите в приложение для подтверждения.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[sitter.user.username],
            fail_silently=True,
        )

        output = BookingOutputSerializer(booking)
        return Response(output.data, status=status.HTTP_201_CREATED)


class UserBookingsListView(APIView):

    @extend_schema(
        summary="Список бронирований на роль пользователя",
        responses={status.HTTP_200_OK: BookingOutputSerializer(many=True)},
    )
    def get(self, request):
        bookings = Booking.objects.filter(owner=request.user).order_by('-start_datetime')
        serializer = BookingOutputSerializer(bookings, many=True)
        return Response(serializer.data)


class SitterBookingsListView(APIView):

    @extend_schema(
        summary="Список бронирований на роль ситтера",
        responses={status.HTTP_200_OK: BookingOutputSerializer(many=True)},
    )
    def get(self, request):
        bookings = Booking.objects.filter(sitter=request.user.sitter_profile).order_by('-start_datetime')
        serializer = BookingOutputSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingDetailView(APIView):

    @extend_schema(responses={status.HTTP_200_OK: BookingOutputSerializer, status.HTTP_403_FORBIDDEN: "Нет доступа"})
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, pk=booking_id)
        if request.user != booking.owner and request.user.sitter_profile != booking.sitter:
            return Response({'error': 'Access denied'}, status=403)
        serializer = BookingOutputSerializer(booking)
        return Response(serializer.data)


class SitterBookingActionView(APIView):

    @extend_schema(
        summary="Действие ситтера над бронированием",
        request=BookingActionSerializer,
        responses={200: BookingOutputSerializer, 400: "Недопустимое действие или статус"}
    )
    def post(self, request, booking_id):
        action_serializer = BookingActionSerializer(data=request.data)
        action_serializer.is_valid(raise_exception=True)
        action = action_serializer.validated_data['action']
        booking = get_object_or_404(Booking, pk=booking_id, sitter=request.user)

        if action == 'accept':
            if booking.status != BookingStatus.PENDING:
                return Response({'error': 'Already processed'}, status=400)
            booking.status = BookingStatus.CONFIRMED
            booking.sitter_confirmed_at = timezone.now()
            booking.save()
            send_mail(
                subject='Бронирование подтверждено',
                message=f'Ваше бронирование #{booking.id} подтверждено ситтером.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.owner.username],
                fail_silently=True,
            )
        elif action == 'reject':
            if booking.status != BookingStatus.PENDING:
                return Response({'error': 'Already processed'}, status=400)
            booking.status = BookingStatus.REJECTED
            booking.save()
            send_mail(
                subject='Бронирование отклонено',
                message=f'Ситтер отклонил ваше бронирование #{booking.id}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.owner.username],
                fail_silently=True,
            )
        elif action == 'complete':
            if booking.status != BookingStatus.CONFIRMED:
                return Response({'error': 'Booking not confirmed'}, status=400)
            booking.status = BookingStatus.COMPLETED
            booking.completed_at = timezone.now()
            booking.save()
            send_mail(
                subject=f'Бронирование #{booking.id} завершено',
                message=f'Услуга выполнена. Пожалуйста, оставьте отзыв о ситтере.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.owner.username],
                fail_silently=True,
            )
        else:
            return Response({'error': 'Invalid action'}, status=400)

        serializer = BookingOutputSerializer(booking)
        return Response(serializer.data)


class BookingCancelView(APIView):

    @extend_schema(responses={200: BookingOutputSerializer, 400: "Нельзя отменить"})
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, owner=request.user)
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            return Response({'error': 'Нельзя отменить, если ситтер принял заказ или выполнил его'}, status=400)
        booking.status = BookingStatus.CANCELLED_BY_OWNER
        booking.cancelled_at = timezone.now()
        booking.save()
        send_mail(
            subject=f'Бронирование #{booking.id} отменено',
            message=f'Заказчик отменил бронирование #{booking.id}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.sitter.user.username],
            fail_silently=True,
        )
        serializer = BookingOutputSerializer(booking)
        return Response(serializer.data)