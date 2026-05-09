from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Booking, Payment, Cancellation
from .serializers import (
    BookingSerializer, PaymentSerializer, CreateBookingSerializer,
    RefundPreviewSerializer, CancellationSerializer
)
from flights.models import Seat
import razorpay
from razorpay.errors import SignatureVerificationError
import os
from decimal import Decimal

razorpay_client = razorpay.Client(
    auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET'))
)


def calculate_refund_percentage(departure_time):
    now = timezone.now()
    hours_left = (departure_time - now).total_seconds() / 3600

    if hours_left > 168: 
        return 90
    elif hours_left > 72: 
        return 75
    elif hours_left > 24: 
        return 50
    elif hours_left > 6:  
        return 25
    else:              
        return 0


class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateBookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        flight = serializer.validated_data['flight']
        seat = serializer.validated_data['seat']
        booking = Booking.objects.create(
            user             = request.user,
            flight           = flight,
            seat             = seat,
            passenger_name   = serializer.validated_data['passenger_name'],
            passenger_age    = serializer.validated_data['passenger_age'],
            total_amount     = seat.base_price,
            status           = 'pending'
        )
        payment = Payment.objects.create(
            booking = booking,
            amount  = seat.base_price,
            status  = 'pending'
        )
        payment.razorpay_order_id = f"order_{booking.pnr}"
        payment.save()
        return Response({
            'message':  'Booking created, proceed to payment',
            'booking':  BookingSerializer(booking).data,
            'payment':  {
                'razorpay_order_id': payment.razorpay_order_id,
                'amount': float(payment.amount),
                'currency':'INR'
            }
        }, status=status.HTTP_201_CREATED)

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        booking_id        = request.data.get('booking_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature  = request.data.get('razorpay_signature')

        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
            payment = booking.payment
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'},status=status.HTTP_404_NOT_FOUND)
        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id':    payment.razorpay_order_id,
                'razorpay_payment_id':  razorpay_payment_id,
                'razorpay_signature':   razorpay_signature
            })
        except SignatureVerificationError:
            payment.status = 'failed'
            payment.save()
            return Response({'error': 'Payment verification failed'},status=status.HTTP_400_BAD_REQUEST)
        payment.razorpay_payment_id = razorpay_payment_id
        payment.status = 'success'
        payment.paid_at = timezone.now()
        payment.save()
        booking.status = 'confirmed'
        booking.save()
        seat = booking.seat
        seat.is_booked = True
        seat.save()
        return Response({'message': 'Payment verified and booking confirmed','booking': BookingSerializer(booking).data,'pnr':booking.pnr}, status=status.HTTP_200_OK)


class RefundPreviewView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user, status='confirmed')
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found or not confirmed'},status=status.HTTP_404_NOT_FOUND)

        refund_percentage = calculate_refund_percentage(booking.flight.departure_time)
        refund_amount = Decimal(booking.total_amount) * Decimal(refund_percentage) / Decimal(100)
        return Response({
            'refund_percentage': refund_percentage,
            'refund_amount': refund_amount,
            'original_amount':booking.total_amount,
            'message':f'You will get ₹{refund_amount} back ({refund_percentage}% refund)'}, status=status.HTTP_200_OK)


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user, status='confirmed')
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found or already cancelled'},status=status.HTTP_404_NOT_FOUND)

        refund_percentage = calculate_refund_percentage(booking.flight.departure_time)
        refund_amount = Decimal(booking.total_amount) * Decimal(refund_percentage) / Decimal(100)
        cancellation = Cancellation.objects.create(
            booking            = booking,
            reason             = request.data.get('reason', ''),
            refund_percentage  = refund_percentage,
            refund_amount      = refund_amount,
            refund_status      = 'pending'
        )
        booking.status = 'cancelled'
        booking.save()
        seat = booking.seat
        seat.is_booked = False
        seat.save()
        return Response({'message':'Booking cancelled successfully','cancellation_id':cancellation.id,'refund_amount':refund_amount,'refund_status':'pending'}, status=status.HTTP_200_OK)

class BookingHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response({'bookings': serializer.data}, status=status.HTTP_200_OK)