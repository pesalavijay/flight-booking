from django.urls import path
from .views import ( CreateBookingView, VerifyPaymentView, RefundPreviewView,CancelBookingView, BookingHistoryView)

urlpatterns = [
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('my-bookings/', BookingHistoryView.as_view(), name='booking-history'),
    path('bookings/<int:booking_id>/refund-preview/', RefundPreviewView.as_view(), name='refund-preview'),
    path('bookings/<int:booking_id>/cancel/', CancelBookingView.as_view(), name='cancel-booking'),
]