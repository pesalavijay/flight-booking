import os
import django
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from flights.models import Flight, Seat

def seed_seats():
    try:
        flight = Flight.objects.get(flight_number='6E-204')
    except Flight.DoesNotExist:
        print("Flight 6E-204 not found. Please add it in admin first.")
        return

    # Delete existing seats for clean run
    Seat.objects.filter(flight=flight).delete()

    seats = [
        # First Class
        {'seat_number': '1A', 'seat_class': 'firstclass', 'is_window': True,  'is_aisle': False, 'is_exit_row': False, 'base_price': 12500},
        {'seat_number': '1B', 'seat_class': 'firstclass', 'is_window': False, 'is_aisle': False, 'is_exit_row': False, 'base_price': 12200},

        # Business
        {'seat_number': '4A', 'seat_class': 'business',   'is_window': True,  'is_aisle': False, 'is_exit_row': False, 'base_price': 6500},
        {'seat_number': '4B', 'seat_class': 'business',   'is_window': False, 'is_aisle': True,  'is_exit_row': False, 'base_price': 6500},
        {'seat_number': '4C', 'seat_class': 'business',   'is_window': False, 'is_aisle': True,  'is_exit_row': False, 'base_price': 6500},
        {'seat_number': '4D', 'seat_class': 'business',   'is_window': True,  'is_aisle': False, 'is_exit_row': False, 'base_price': 6500},

        # Economy - Exit Row
        {'seat_number': '9A', 'seat_class': 'economy',    'is_window': True,  'is_aisle': False, 'is_exit_row': True,  'base_price': 2700},
        {'seat_number': '9B', 'seat_class': 'economy',    'is_window': False, 'is_aisle': False, 'is_exit_row': True,  'base_price': 2400},
        {'seat_number': '9C', 'seat_class': 'economy',    'is_window': False, 'is_aisle': True,  'is_exit_row': True,  'base_price': 2500},
        {'seat_number': '9D', 'seat_class': 'economy',    'is_window': False, 'is_aisle': True,  'is_exit_row': True,  'base_price': 2500},
        {'seat_number': '9E', 'seat_class': 'economy',    'is_window': False, 'is_aisle': False, 'is_exit_row': True,  'base_price': 2400},
        {'seat_number': '9F', 'seat_class': 'economy',    'is_window': True,  'is_aisle': False, 'is_exit_row': True,  'base_price': 2700},

        # Economy - Regular
        {'seat_number': '10A', 'seat_class': 'economy',   'is_window': True,  'is_aisle': False, 'is_exit_row': False, 'base_price': 2500},
        {'seat_number': '10B', 'seat_class': 'economy',   'is_window': False, 'is_aisle': False, 'is_exit_row': False, 'base_price': 2200},
        {'seat_number': '10C', 'seat_class': 'economy',   'is_window': False, 'is_aisle': True,  'is_exit_row': False, 'base_price': 2350},
        {'seat_number': '10D', 'seat_class': 'economy',   'is_window': False, 'is_aisle': True,  'is_exit_row': False, 'base_price': 2350},
        {'seat_number': '10E', 'seat_class': 'economy',   'is_window': False, 'is_aisle': False, 'is_exit_row': False, 'base_price': 2200},
        {'seat_number': '10F', 'seat_class': 'economy',   'is_window': True,  'is_aisle': False, 'is_exit_row': False, 'base_price': 2500},

        {'seat_number': '11A', 'seat_class': 'economy',   'is_window': True,  'is_aisle': False, 'is_exit_row': False, 'base_price': 2500},
        {'seat_number': '11B', 'seat_class': 'economy',   'is_window': False, 'is_aisle': False, 'is_exit_row': False, 'base_price': 2200},
        {'seat_number': '11C', 'seat_class': 'economy',   'is_window': False, 'is_aisle': True,  'is_exit_row': False, 'base_price': 2350},
        {'seat_number': '11D', 'seat_class': 'economy',   'is_window': False, 'is_aisle': True,  'is_exit_row': False, 'base_price': 2350},
        {'seat_number': '11E', 'seat_class': 'economy',   'is_window': False, 'is_aisle': False, 'is_exit_row': False, 'base_price': 2200},
        {'seat_number': '11F', 'seat_class': 'economy',   'is_window': True,  'is_aisle': False, 'is_exit_row': False, 'base_price': 2500},
    ]

    for s in seats:
        Seat.objects.create(flight=flight, **s)
        print(f"Added seat {s['seat_number']} - {s['seat_class']}")

    print(f"\n✅ Done! {len(seats)} seats added for flight 6E-204")

if __name__ == '__main__':
    seed_seats()