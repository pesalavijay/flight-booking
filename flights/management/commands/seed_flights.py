import random
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from flights.models import Flight, Seat

class Command(BaseCommand):
    help = 'Seeds the database with flights and seats up to May 31, 2027'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting database seed... this might take a minute.'))

        # 1. Setup our dummy data pools
        airlines = ['Platter Airways', 'IndiGo', 'Air India', 'Vistara', 'SpiceJet']
        cities = ['Hyderabad', 'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Pune']
        
        # 2. Setup the Date Range (Today until May 31, 2027)
        start_date = timezone.now()
        end_date = timezone.make_aware(datetime(2027, 5, 31, 23, 59, 59))
        
        days_to_generate = (end_date - start_date).days

        flights_created = 0
        seats_created = 0

        # Seat layout (Rows 1-11, Seats A-F based on your React UI)
        rows = range(1, 12)
        cols = ['A', 'B', 'C', 'D', 'E', 'F']

        # Add a counter to guarantee totally unique flight numbers!
        flight_counter = 1000

        # 3. Loop through every single day
        for i in range(days_to_generate + 1):
            current_day = start_date + timedelta(days=i)
            
            # Generate 3 to 6 random flights per day
            num_flights_today = random.randint(3, 6)
            
            for _ in range(num_flights_today):
                # Pick random, different cities
                source, dest = random.sample(cities, 2)
                
                # Randomize time of day
                hour = random.randint(5, 22) # Flights between 5 AM and 10 PM
                minute = random.choice([0, 15, 30, 45])
                departure_time = current_day.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Generate exact duration for math
                dur_hours = random.randint(1, 3)
                dur_mins = random.choice([0, 15, 30, 45])
                
                # Calculate arrival time exactly based on departure + duration
                arrival_time = departure_time + timedelta(hours=dur_hours, minutes=dur_mins)
                
                # Generate a guaranteed unique flight number
                prefix = random.choice(['6E', 'AI', 'UK', 'SG', 'PA'])
                unique_flight_number = f"{prefix}-{flight_counter}"
                flight_counter += 1  # Increase counter for the next flight
                
                # Create the Flight
                flight = Flight.objects.create(
                    airline=random.choice(airlines),
                    flight_number=unique_flight_number,
                    source=source,
                    destination=dest,
                    departure_time=departure_time,
                    arrival_time=arrival_time,                 
                    duration=f"{dur_hours}h {dur_mins:02d}m",  
                    is_active=True
                )
                flights_created += 1

                # Generate Seats for this flight in bulk (much faster than saving one by one)
                seats_to_insert = []
                base_price = random.choice([2500.00, 3500.00, 4500.00, 5500.00])
                
                for row in rows:
                    for col in cols:
                        # Make front rows slightly more expensive
                        seat_price = base_price + 500 if row <= 3 else base_price
                        
                        seats_to_insert.append(
                            Seat(
                                flight=flight,
                                seat_number=f"{row}{col}",
                                is_booked=random.choice([True, False, False, False]), # 25% chance a seat is already booked
                                base_price=seat_price
                            )
                        )
                
                # Bulk insert all seats for this flight
                Seat.objects.bulk_create(seats_to_insert)
                seats_created += len(seats_to_insert)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded! Created {flights_created} flights and {seats_created} seats up to May 2027.'
        ))