from django.urls import path
from .views import FlightSearchView, SeatMapView, SeatLockView, UserDashboardView

urlpatterns = [
    path('search/', FlightSearchView.as_view(), name='flight-search'),
    path('<int:flight_id>/seats/', SeatMapView.as_view(), name='seat-map'),
    path('<int:flight_id>/seats/<int:seat_id>/lock/', SeatLockView.as_view(), name='seat-lock'),
    path('api/dashboard/tickets/', UserDashboardView.as_view(), name='user-dashboard-tickets'),
    ]