import os
import razorpay
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from razorpay.errors import SignatureVerificationError
from flights.models import Flight, Seat  
from .models import Booking, Payment, Cancellation
from .serializers import BookingSerializer
from datetime import timedelta
from django.utils import timezone
from rest_framework import generics
from flights.serializers import FlightSerializer

razorpay_client = razorpay.Client(
    auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET'))
)

def calculate_refund_percentage(departure_time):
    now = timezone.now()
    hours_left = (departure_time - now).total_seconds() / 3600
    if hours_left > 168: return 90
    elif hours_left > 72: return 75
    elif hours_left > 24: return 50
    elif hours_left > 6:  return 25
    else: return 0

class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        flight_id = request.data.get('flight_id')
        passengers_data = request.data.get('passengers', [])
        if not flight_id or not passengers_data:
            return Response({'error': 'Flight ID and passengers are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            flight = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            return Response({'error': 'Flight not found'}, status=status.HTTP_404_NOT_FOUND)

        if flight.departure_time < timezone.now():
            return Response({'error': 'Cannot book a flight that has already departed.'}, status=status.HTTP_400_BAD_REQUEST)
        total_amount = Decimal('0.00')
        seats_to_book = []

        for p_data in passengers_data:
            try:
                seat = Seat.objects.get(id=p_data['seat_id'], flight=flight)
            except Seat.DoesNotExist:
                return Response({'error': f"Seat {p_data.get('seat_number')} not found"}, status=status.HTTP_404_NOT_FOUND)

            if seat.is_booked:
                return Response({'error': f"Seat {seat.seat_number} is already booked"}, status=status.HTTP_400_BAD_REQUEST)

            total_amount += Decimal(str(seat.base_price))
            seats_to_book.append((seat, p_data))

        try:
            razorpay_order = razorpay_client.order.create({
                'amount':   int(total_amount * 100),
                'currency': 'INR',
                'receipt':  f"grp_flight_{flight.id}_user_{request.user.id}",
            })
        except Exception as e:
            return Response({'error': f'Payment gateway error: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY )

        created_bookings = []

        with transaction.atomic():
            for seat, p_data in seats_to_book:
                booking = Booking.objects.create(
                    user = request.user,
                    flight = flight,
                    seat = seat,
                    passenger_name = p_data['passenger_name'],
                    passenger_age = p_data['passenger_age'],
                    total_amount = seat.base_price,
                    status = 'pending' )
                Payment.objects.create(
                    booking = booking,
                    amount = seat.base_price,
                    status = 'pending',
                    razorpay_order_id = razorpay_order['id'],
                )
                created_bookings.append(booking)

        return Response({
            'message': 'Group booking created, proceed to payment',
            'bookings': BookingSerializer(created_bookings, many=True).data,
            'payment': {
                'razorpay_order_id': razorpay_order['id'],
                'amount': float(total_amount),
                'currency': 'INR',
            }
        }, status=status.HTTP_201_CREATED)

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        razorpay_order_id  = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response({'error': 'razorpay_order_id, payment_id and signature are required'}, status=status.HTTP_400_BAD_REQUEST)
        payments = Payment.objects.filter(razorpay_order_id=razorpay_order_id, booking__user=request.user)

        if not payments.exists():
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id':   razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature':  razorpay_signature,
            })
        except SignatureVerificationError:
            payments.update(status='failed')
            return Response({'error': 'Payment verification failed. Contact support.'}, status=status.HTTP_400_BAD_REQUEST )

        with transaction.atomic():
            for payment in payments:
                payment.razorpay_payment_id = razorpay_payment_id
                payment.status  = 'success'
                payment.paid_at = timezone.now()
                payment.save()
                booking = payment.booking
                booking.status = 'confirmed'
                booking.save()
                seat = booking.seat
                seat.is_booked = True
                seat.save()
        return Response({ 'message': 'Group payment verified and all bookings confirmed!'}, status=status.HTTP_200_OK)

class BookingHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        bookings = Booking.objects.filter(user=request.user, status='confirmed').order_by('-booked_at')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RefundPreviewView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user, status='confirmed')
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found or not confirmed'}, status=status.HTTP_404_NOT_FOUND )
        refund_percentage = calculate_refund_percentage(booking.flight.departure_time)
        refund_amount = Decimal(booking.total_amount) * Decimal(refund_percentage) / Decimal(100)

        return Response({
            'refund_percentage': refund_percentage,
            'refund_amount': str(refund_amount),
            'original_amount': str(booking.total_amount),
            'message': f'You will get ₹{refund_amount:.2f} back ({refund_percentage}% refund)',
        }, status=status.HTTP_200_OK)

class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user, status='confirmed')
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found or already cancelled'}, status=status.HTTP_404_NOT_FOUND )
            
        if booking.flight.departure_time < timezone.now():
            return Response({'error': 'Cannot cancel a completed flight.'}, status=status.HTTP_400_BAD_REQUEST)
            
        refund_percentage = calculate_refund_percentage(booking.flight.departure_time)
        refund_amount = Decimal(booking.total_amount) * Decimal(refund_percentage) / Decimal(100)

        payment = Payment.objects.filter(booking=booking, status='success').first()

        if refund_amount > 0 and payment and payment.razorpay_payment_id:
            try:
                razorpay_client.payment.refund(payment.razorpay_payment_id, {
                    "amount": int(refund_amount * 100)
                })
            except Exception as e:
                return Response({'error': f'Gateway failed to process refund: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)

        with transaction.atomic():
            cancellation = Cancellation.objects.create(
                booking = booking,
                reason = request.data.get('reason', ''),
                refund_percentage = refund_percentage,
                refund_amount = refund_amount,
                refund_status = 'completed' if refund_amount > 0 else 'not_applicable',
            )

            booking.status = 'cancelled'
            booking.save()

            seat = booking.seat
            seat.is_booked = False
            seat.save()

        return Response({
            'message': 'Booking cancelled and refund initiated successfully',
            'cancellation_id': cancellation.id,
            'refund_amount': str(refund_amount),
            'refund_status': cancellation.refund_status,
        }, status=status.HTTP_200_OK)


class UpcomingFlightsView(generics.ListAPIView):
    serializer_class = FlightSerializer

    def get_queryset(self):
        today = timezone.now().date()

        three_months_limit = today + timedelta(days=90)

        return Flight.objects.filter( departure_date__range=[today, three_months_limit]).order_by('departure_date')