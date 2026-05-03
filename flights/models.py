from django.db import models


# Create your models here.
class Flight(models.Model):
    Airline_CHOICES = [
        ('airIndia','AirIndia'),
        ('vistara' , 'Vistara'),
        ('indigo' , 'IndiGo'),
        ('starair', 'StartAir'),
        ('spicejet', 'SpiceJet'),
    ]
    airline = models.CharField(max_length=50, choices=Airline_CHOICES)
    flight_number = models.CharField(max_length=100, unique=True)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [('departure_time')]

    def __str__(self):
        return f"{self.flight_number} | {self.source} | {self.destination}"
    
class Seat(models.Model):
    CLASS_CHOICES = [
        ('firstclass', 'First Class'),
        ('business', 'Business'),
        ('economy', 'Economy'),
    ]
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='Seats')
    seat_number = models.CharField(max_length=4)
    seat_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    is_window = models.BooleanField(default=False)
    is_aisle = models.BooleanField(default=False)
    is_exit_row = models.BooleanField(default=False)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_bookend = models.BooleanField(default=False)

    class Meta:
        unique_together = ('flight' , 'seat_number')

    def __str__(self):
        return f"{self.flight.flight_number} - Seat {self.seat_number} ({self.seat_class})"

