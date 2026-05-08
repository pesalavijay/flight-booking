from rest_framework import serializers
from .models import Flight, Seat


class SeatSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model  = Seat
        fields = [
            'id', 'seat_number', 'seat_class',
            'is_window', 'is_aisle', 'is_exit_row',
            'base_price', 'status'
        ]

    def get_status(self, obj):
        locked_seats = self.context.get('locked_seats', set())
        if obj.id in locked_seats:
            return 'locked'
        if obj.is_booked:
            return 'booked'
        return 'available'


class FlightSerializer(serializers.ModelSerializer):
    duration        = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model  = Flight
        fields = [
            'id', 'flight_number', 'airline',
            'source', 'destination',
            'departure_time', 'arrival_time',
            'duration', 'available_seats', 'is_active'
        ]

    def get_duration(self, obj):
        delta   = obj.arrival_time - obj.departure_time
        hours   = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    def get_available_seats(self, obj):
        return obj.seats.filter(is_booked=False).count()