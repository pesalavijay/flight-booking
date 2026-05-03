from django.db import models
from django.conf import settings
from flights.models import Flight, Seat
import uuid

# Create your models here.
def generate_pnr():
    return uuid.uuid4().hex[:8].upper()

class Booking(models.Model):
    Status_Choices = [('pending','Pending'), ('confirmed','Confirmed'), ('cancelled', 'Cancelled')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name = 'bookings')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='bookings')
    pnr = models.CharField(max_length=10, unique=True, default=generate_pnr)
    status = models.CharField(max_length=30, choices=Status_Choices)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    passanger_name = models.CharField(max_length=150)
    passanger_age = models.PositiveIntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PNR: {self.pnr} | {self.user.email} | {self.flight.flight_number}"
    


class Payment(models.Model):
    Status_Choices = [('success', 'Success'), ('failed','Failed'), ('pending','Pending'), ('refunded','Refunded')]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payemnts')
    razorpay_order_id   = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    status              = models.CharField(max_length=20, choices=Status_Choices, default='pending')
    amount              = models.DecimalField(max_digits=10, decimal_places=2)
    refund_amount       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_at             = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for PNR {self.booking.pnr} | {self.status}"

class Cancellation(models.Model):
    booking            = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='cancellation')
    reason             = models.TextField(blank=True)
    refund_percentage  = models.DecimalField(max_digits=5, decimal_places=2)
    refund_amount      = models.DecimalField(max_digits=10, decimal_places=2)
    refund_status      = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('processed', 'Processed')], default='pending')
    cancelled_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancellation for PNR {self.booking.pnr}"



