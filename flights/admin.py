from django.contrib import admin
from .models import Flight, Seat


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'airline', 'source', 'destination', 'departure_time', 'arrival_time', 'is_active']
    list_filter = ['airline', 'is_active']
    search_fields = ['flight_number', 'source', 'destination']


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ['flight', 'seat_number', 'seat_class', 'base_price']
    list_filter = ['seat_class']
    search_fields = ['seat_number']