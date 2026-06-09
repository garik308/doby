from django.urls import path

from reviews.views import ReviewCreateView, MyReviewsView, SitterReviewsView

urlpatterns=[
    path('', ReviewCreateView.as_view(), name='review-create'),
    path('me/', MyReviewsView.as_view(), name='my-reviews'),
    path('sitter/<int:sitter_uuid>/', SitterReviewsView.as_view(), name='sitter-reviews'),
]