from django.urls import path
from .views import FlightSearchView, SeatMapView, SeatLockView, UpcomingFlightsView

urlpatterns = [
    path('search/', FlightSearchView.as_view(), name='flight-search'),
    path('upcoming/', UpcomingFlightsView.as_view(), name='upcoming-flights'), # <-- Add this line
    path('<int:flight_id>/seats/', SeatMapView.as_view(), name='seat-map'),
    path('<int:flight_id>/seats/<int:seat_id>/lock/', SeatLockView.as_view(), name='seat-lock'),
]