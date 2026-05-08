from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from .models import Flight, Seat
from .serializers import FlightSerializer, SeatSerializer
import redis
import os

redis_client = redis.StrictRedis.from_url(
    os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    decode_responses=True
)

SEAT_LOCK_TTL = 600  # 10 minutes in seconds


class FlightSearchView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        source      = request.query_params.get('source', '').strip()
        destination = request.query_params.get('destination', '').strip()
        date        = request.query_params.get('date', '').strip()

        if not source or not destination or not date:
            return Response(
                {'error': 'source, destination and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cache key based on search params
        cache_key = f"search:{source}:{destination}:{date}"
        cached    = cache.get(cache_key)
        if cached:
            return Response({'flights': cached, 'source': 'cache'})

        # Query DB
        flights = Flight.objects.filter(
            source__iexact      = source,
            destination__iexact = destination,
            departure_time__date = date,
            is_active           = True
        ).prefetch_related('seats')

        if not flights.exists():
            return Response(
                {'message': 'No flights found', 'flights': []},
                status=status.HTTP_200_OK
            )

        serializer = FlightSerializer(flights, many=True)

        # Cache results for 5 minutes
        cache.set(cache_key, serializer.data, timeout=300)

        return Response({
            'flights': serializer.data,
            'source':  'db'
        }, status=status.HTTP_200_OK)


class SeatMapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, flight_id):
        try:
            flight = Flight.objects.get(id=flight_id, is_active=True)
        except Flight.DoesNotExist:
            return Response(
                {'error': 'Flight not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        seats = Seat.objects.filter(flight=flight).order_by('seat_number')

        # Get all locked seat IDs from Redis for this flight
        locked_keys = redis_client.keys(f"seat_lock:{flight_id}:*")
        locked_seats = set()
        for key in locked_keys:
            seat_id = redis_client.get(key)
            if seat_id:
                locked_seats.add(int(seat_id))

        serializer = SeatSerializer(
            seats,
            many=True,
            context={'request': request, 'locked_seats': locked_seats}
        )

        return Response({
            'flight':    FlightSerializer(flight).data,
            'seats':     serializer.data,
        }, status=status.HTTP_200_OK)


class SeatLockView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, flight_id, seat_id):
        try:
            seat = Seat.objects.get(id=seat_id, flight__id=flight_id)
        except Seat.DoesNotExist:
            return Response(
                {'error': 'Seat not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if seat.is_booked:
            return Response(
                {'error': 'Seat is already booked'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if seat is already locked by someone else
        lock_key = f"seat_lock:{flight_id}:{seat_id}"
        existing = redis_client.get(lock_key)

        if existing and existing != str(request.user.id):
            return Response(
                {'error': 'Seat is currently locked by another user'},
                status=status.HTTP_409_CONFLICT
            )

        # Lock the seat in Redis with TTL
        redis_client.setex(lock_key, SEAT_LOCK_TTL, str(request.user.id))

        return Response({
            'message':    'Seat locked successfully',
            'seat_id':    seat_id,
            'expires_in': f'{SEAT_LOCK_TTL // 60} minutes'
        }, status=status.HTTP_200_OK)


    def delete(self, request, flight_id, seat_id):
        lock_key = f"seat_lock:{flight_id}:{seat_id}"
        existing = redis_client.get(lock_key)

        if not existing:
            return Response(
                {'error': 'Seat is not locked'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if existing != str(request.user.id):
            return Response(
                {'error': 'You can only unlock seats you locked'},
                status=status.HTTP_403_FORBIDDEN
            )

        redis_client.delete(lock_key)
        return Response(
            {'message': 'Seat unlocked successfully'},
            status=status.HTTP_200_OK
        )