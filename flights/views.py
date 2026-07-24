from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from .models import Flight, Seat
from .serializers import FlightSerializer, SeatSerializer
from rest_framework import generics

# Commenting out Redis since we are on Render's free tier and it will crash the server
# import redis
# import os
# from dotenv import load_dotenv, find_dotenv
# load_dotenv(find_dotenv())
# redis_client = redis.StrictRedis.from_url(...)

SEAT_LOCK_TTL = 600

class FlightSearchView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def get(self, request):
        source = request.query_params.get('source', '').strip()
        destination = request.query_params.get('destination', '').strip()
        date = request.query_params.get('date', '').strip()
        
        # FIX 1: Date is now optional! We only require source and destination.
        if not source or not destination:
            return Response({'error': 'Source and destination are required'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"search:{source}:{destination}:{date}"
        # This will safely use Django's built-in local memory cache
        # cached = cache.get(cache_key)
        
        # if cached:
        #     return Response({'flights': cached, 'source': 'cache'})

        # FIX 2: Set the 90-day rolling window
        today = timezone.now().date()
        three_months_out = today + timedelta(days=90)

        # Base query: Match cities, ensure it's active, and lock to 90 days
        queryset = Flight.objects.filter(
            source__iexact=source,
            destination__iexact=destination,
            departure_time__date__range=[today, three_months_out],
            is_active=True
        ).prefetch_related('seats')

        # If the user actually provided a date, filter down to that specific date
        if date:
            queryset = queryset.filter(departure_time__date=date)

        # Order chronologically
        flights = queryset.order_by('departure_time')

        if not flights.exists():
            return Response({'message': 'No flights found', 'flights': []}, status=status.HTTP_200_OK)
        
        serializer = FlightSerializer(flights, many=True)
        cache.set(cache_key, serializer.data, timeout=300)

        return Response({'flights': serializer.data, 'source': 'db'}, status=status.HTTP_200_OK)


class SeatMapView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, flight_id):
        try:
            flight = Flight.objects.get(id=flight_id, is_active=True)
        except Flight.DoesNotExist:
            return Response({'error': 'Flight not found'}, status=status.HTTP_404_NOT_FOUND)
            
        seats = Seat.objects.filter(flight=flight).order_by('seat_number')
        
        # Bypassing Redis keys for now so Render doesn't crash
        locked_seats = set() 

        serializer = SeatSerializer(seats, many=True, context={'request': request, 'locked_seats': locked_seats})

        return Response({'flight': FlightSerializer(flight).data, 'seats': serializer.data}, status=status.HTTP_200_OK)


class SeatLockView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, flight_id, seat_id):
        try:
            seat = Seat.objects.get(id=seat_id, flight__id=flight_id)
        except Seat.DoesNotExist:
            return Response({'error': 'Seat not found'}, status=status.HTTP_404_NOT_FOUND)

        if seat.is_booked:
            return Response({'error': 'Seat is already booked'}, status=status.HTTP_400_BAD_REQUEST)

        # Simulating a successful lock response so the frontend still works without Redis
        return Response({
            'message': 'Seat locked successfully', 
            'seat_id': seat_id, 
            'expires_in': f'{SEAT_LOCK_TTL // 60} minutes'
        }, status=status.HTTP_200_OK)

    def delete(self, request, flight_id, seat_id):
        # Simulating a successful unlock for the frontend
        return Response({'message': 'Seat unlocked successfully'}, status=status.HTTP_200_OK)


class UpcomingFlightsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = FlightSerializer

    def get_queryset(self):
        today = timezone.now().date()
        three_months_out = today + timedelta(days=90)
        
        # Fetch upcoming active flights within the 3-month window
        return Flight.objects.filter(
            departure_time__date__range=[today, three_months_out],
            is_active=True
        ).order_by('departure_time')[:9] # Limits to 9 flights so the UI grid looks clean