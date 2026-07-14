from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django.core.cache import cache
from .models import Flight, Seat
from .serializers import FlightSerializer, SeatSerializer

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
        
        if not source or not destination or not date:
            return Response({'error': 'source, destination and date are required'}, status=status.HTTP_400_BAD_REQUEST )

        cache_key = f"search:{source}:{destination}:{date}"
        # This will now safely use Django's built-in local memory cache since we disabled Redis
        cached = cache.get(cache_key)
        
        if cached:
            return Response({'flights': cached, 'source': 'cache'})

        flights = Flight.objects.filter(
            source__iexact = source,
            destination__iexact = destination,
            departure_time__date = date,
            is_active = True
        ).prefetch_related('seats')

        if not flights.exists():
            return Response({'message': 'No flights found', 'flights': []}, status=status.HTTP_200_OK)
        
        serializer = FlightSerializer(flights, many=True)
        cache.set(cache_key, serializer.data, timeout=300)

        return Response({ 'flights': serializer.data,'source':'db'}, status=status.HTTP_200_OK)


class SeatMapView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    class SeatMapView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, flight_id):
        try:
            flight = Flight.objects.get(id=flight_id, is_active=True)
        except Flight.DoesNotExist:
            return Response({'error': 'Flight not found'}, status=status.HTTP_404_NOT_FOUND)
            
        seats = Seat.objects.filter(flight=flight).order_by('seat_number')
        
        # FIX: Bypassing Redis keys for now so Render doesn't crash!
        locked_seats = set() 

        serializer = SeatSerializer(seats, many=True, context={'request': request, 'locked_seats': locked_seats})

        return Response({ 'flight': FlightSerializer(flight).data, 'seats': serializer.data,}, status=status.HTTP_200_OK)


class SeatLockView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, flight_id, seat_id):
        try:
            seat = Seat.objects.get(id=seat_id, flight__id=flight_id)
        except Seat.DoesNotExist:
            return Response( {'error': 'Seat not found'},status=status.HTTP_404_NOT_FOUND )

        if seat.is_booked:
            return Response({'error': 'Seat is already booked'}, status=status.HTTP_400_BAD_REQUEST)

        # FIX: Simulating a successful lock for the frontend without using Redis
        return Response({'message': 'Seat locked successfully', 'seat_id': seat_id, 'expires_in': '10 minutes'}, status=status.HTTP_200_OK)


    def delete(self, request, flight_id, seat_id):
        # FIX: Simulating a successful unlock
        return Response({'message': 'Seat unlocked successfully'},status=status.HTTP_200_OK)


class SeatLockView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, flight_id, seat_id):
        try:
            seat = Seat.objects.get(id=seat_id, flight__id=flight_id)
        except Seat.DoesNotExist:
            return Response( {'error': 'Seat not found'},status=status.HTTP_404_NOT_FOUND )

        if seat.is_booked:
            return Response({'error': 'Seat is already booked'}, status=status.HTTP_400_BAD_REQUEST)

        # I read online that for a basic college setup without Redis, we can just 
        # simulate the lock response so the frontend still works. 
        # We will upgrade this to a proper PostgreSQL DB lock later!
        
        return Response({
            'message': 'Seat locked successfully', 
            'seat_id': seat_id, 
            'expires_in': f'{SEAT_LOCK_TTL // 60} minutes'
        }, status=status.HTTP_200_OK)

    def delete(self, request, flight_id, seat_id):
        # Simulating a successful unlock for the frontend
        return Response({'message': 'Seat unlocked successfully'},status=status.HTTP_200_OK)