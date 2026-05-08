from rest_framework import serializers
from .models import Booking, Payment, Cancellation
from flights.models import Seat, Flight

class BookingSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source='flights.flight_number', read_only=True)
    seat_number = serializers.CharField(source='seat.seat_number', read_only=True)
    class Meta:
        model = Booking
        fields = [
            'id', 'pnr', 'flight_number','seat_number','passenger_name', 'passenger_age','status','total_amount', 'bookend_at'
        ]
        read_only_fields = ['id', 'pnr', 'booked_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'razorpay_order_id', 'razorpay_payment_id', 'status', 'amount','refund_amount','paid_at'
        ]
        read_only_fields = ['id', 'razorpay_order_id', 'razorpay_payment_id', 'paid_at']


class CreateBookingSerializer(serializers.ModelSerializer):
    flight_id = serializers.IntegerField()
    sear_id = serializers.IntegerField()
    passenger_name = serializers.CharField(max_length = 150)
    passenger_age = serializers.IntegerField()

    def validate(self, data):
        try:
            flight=  Flight.objects.get(id=data['flight_id'], is_active=True)
            seat = Seat.objects.get(id=data['seat_id'], flight=flight)
        except Flight.DoesNotExist:
            raise serializers.ValidationError("Flight not found")
        except Seat.DoesNotExist:
            raise serializers.ValidateError("Seat not found for this flight")
        
        if seat.is_booked:
            raise serializers.ValidationError("Seat is already Booked")
        
        data['flight'] = flight
        data['seat'] = seat
        return data
    
class RefundPreviewSearializer(serializers.Serializer):
    refund_percentage = serializers.FloatField(read_only=True)
    refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    reason = serializers.CharField(required=False, allow_blank=True)


class CancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancellation
        fields = [
            'id', 'reason', 'refund_percentage','refund_amount','refund_status','cancelled_at'
        ]
        read_only_fields = [
            'id','refund_percentage','refund_amount','refund_status','cancelled_at'
        ]
