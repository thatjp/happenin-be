from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.events.models import Event
from decimal import Decimal
from datetime import date, time, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create 15 diverse events around New York City and Brooklyn'

    def handle(self, *args, **options):
        # Get or create a user for the events
        user, created = User.objects.get_or_create(
            username='nyc_events',
            defaults={
                'email': 'nyc@example.com',
                'first_name': 'NYC',
                'last_name': 'Events'
            }
        )
        
        if created:
            user.set_password('nycpass123')
            user.save()
            self.stdout.write(f'Created user: {user.username}')
        else:
            self.stdout.write(f'Using existing user: {user.username}')

        # NYC Event data
        events_data = [
            {
                'title': 'Central Park Summer Concert Series',
                'description': 'Enjoy live music under the stars in Central Park. Bring a blanket and picnic basket for an unforgettable evening of jazz, classical, and contemporary music.',
                'event_type': 'Music',
                'icon': 'music-note',
                'price': Decimal('0.00'),
                'address': 'Central Park Great Lawn',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '10024',
                'latitude': Decimal('40.7829'),
                'longitude': Decimal('-73.9654'),
                'start_date': date.today() + timedelta(days=3),
                'end_date': date.today() + timedelta(days=3),
                'open_time': time(19, 0),
                'close_time': time(22, 0),
            },
            {
                'title': 'Brooklyn Bridge Sunset Walk',
                'description': 'Join us for a guided walking tour across the iconic Brooklyn Bridge during golden hour. Learn about the bridge\'s history while capturing stunning photos.',
                'event_type': 'Education',
                'icon': 'book-open',
                'price': Decimal('25.00'),
                'address': 'Brooklyn Bridge Walkway',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '10038',
                'latitude': Decimal('40.7061'),
                'longitude': Decimal('-73.9969'),
                'start_date': date.today() + timedelta(days=5),
                'end_date': date.today() + timedelta(days=5),
                'open_time': time(17, 30),
                'close_time': time(19, 30),
            },
            {
                'title': 'Williamsburg Food Festival',
                'description': 'Taste the best of Brooklyn\'s culinary scene at this annual food festival. From artisanal pizza to craft beer, discover why Williamsburg is a foodie paradise.',
                'event_type': 'Food',
                'icon': 'utensils',
                'price': Decimal('45.00'),
                'address': 'McCarren Park',
                'city': 'Brooklyn',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '11206',
                'latitude': Decimal('40.7182'),
                'longitude': Decimal('-73.9582'),
                'start_date': date.today() + timedelta(days=7),
                'end_date': date.today() + timedelta(days=8),
                'open_time': time(11, 0),
                'close_time': time(20, 0),
            },
            {
                'title': 'Times Square Comedy Night',
                'description': 'Laugh the night away at this intimate comedy club in the heart of Times Square. Featuring up-and-coming comedians and surprise celebrity guests.',
                'event_type': 'Entertainment',
                'icon': 'laugh',
                'price': Decimal('35.00'),
                'address': 'Broadway & 42nd Street',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '10036',
                'latitude': Decimal('40.7580'),
                'longitude': Decimal('-73.9855'),
                'start_date': date.today() + timedelta(days=2),
                'end_date': date.today() + timedelta(days=2),
                'open_time': time(20, 0),
                'close_time': time(23, 0),
            },
            {
                'title': 'Prospect Park Yoga & Wellness',
                'description': 'Start your day with a rejuvenating yoga session in the beautiful surroundings of Prospect Park. All levels welcome, mats provided.',
                'event_type': 'Health',
                'icon': 'heart',
                'price': Decimal('15.00'),
                'address': 'Prospect Park Long Meadow',
                'city': 'Brooklyn',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '11215',
                'latitude': Decimal('40.6602'),
                'longitude': Decimal('-73.9690'),
                'start_date': date.today() + timedelta(days=1),
                'end_date': date.today() + timedelta(days=1),
                'open_time': time(7, 0),
                'close_time': time(8, 30),
            },
            {
                'title': 'Chelsea Art Gallery Crawl',
                'description': 'Explore the vibrant contemporary art scene in Chelsea\'s renowned galleries. Guided tour with expert commentary on the latest exhibitions.',
                'event_type': 'Art',
                'icon': 'palette',
                'price': Decimal('30.00'),
                'address': 'Chelsea Art District',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '10011',
                'latitude': Decimal('40.7505'),
                'longitude': Decimal('-74.0060'),
                'start_date': date.today() + timedelta(days=4),
                'end_date': date.today() + timedelta(days=4),
                'open_time': time(14, 0),
                'close_time': time(17, 0),
            },
            {
                'title': 'DUMBO Street Art Workshop',
                'description': 'Learn the basics of street art and graffiti in this hands-on workshop. Create your own piece under the guidance of local artists.',
                'event_type': 'Art',
                'icon': 'spray-can',
                'price': Decimal('55.00'),
                'address': 'DUMBO Arts Center',
                'city': 'Brooklyn',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '11201',
                'latitude': Decimal('40.7033'),
                'longitude': Decimal('-73.9881'),
                'start_date': date.today() + timedelta(days=6),
                'end_date': date.today() + timedelta(days=6),
                'open_time': time(13, 0),
                'close_time': time(16, 0),
            },
            {
                'title': 'Greenwich Village Jazz Session',
                'description': 'Experience authentic jazz in the historic Greenwich Village. Intimate venue with world-class musicians performing classic and contemporary jazz.',
                'event_type': 'Music',
                'icon': 'music-note',
                'price': Decimal('40.00'),
                'address': 'Village Vanguard',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '10014',
                'latitude': Decimal('40.7355'),
                'longitude': Decimal('-74.0027'),
                'start_date': date.today() + timedelta(days=9),
                'end_date': date.today() + timedelta(days=9),
                'open_time': time(21, 0),
                'close_time': time(23, 30),
            },
            {
                'title': 'Brooklyn Heights Historical Tour',
                'description': 'Discover the rich history of Brooklyn Heights, one of NYC\'s most beautiful neighborhoods. Learn about its role in the American Revolution and architectural significance.',
                'event_type': 'Education',
                'icon': 'landmark',
                'price': Decimal('20.00'),
                'address': 'Brooklyn Heights Promenade',
                'city': 'Brooklyn',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '11201',
                'latitude': Decimal('40.6995'),
                'longitude': Decimal('-73.9934'),
                'start_date': date.today() + timedelta(days=10),
                'end_date': date.today() + timedelta(days=10),
                'open_time': time(10, 0),
                'close_time': time(12, 0),
            },
            {
                'title': 'Hudson Yards Tech Meetup',
                'description': 'Connect with fellow tech professionals in the modern Hudson Yards district. Networking, presentations, and discussions on the latest in technology and innovation.',
                'event_type': 'Business',
                'icon': 'laptop',
                'price': Decimal('25.00'),
                'address': 'Hudson Yards',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '10001',
                'latitude': Decimal('40.7505'),
                'longitude': Decimal('-74.0060'),
                'start_date': date.today() + timedelta(days=12),
                'end_date': date.today() + timedelta(days=12),
                'open_time': time(18, 0),
                'close_time': time(21, 0),
            },
            {
                'title': 'Bushwick Street Dance Battle',
                'description': 'Witness incredible breakdancing and street dance performances in Bushwick\'s vibrant arts community. Live DJ, food trucks, and audience participation.',
                'event_type': 'Entertainment',
                'icon': 'dancing',
                'price': Decimal('0.00'),
                'address': 'Bushwick Collective',
                'city': 'Brooklyn',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '11237',
                'latitude': Decimal('40.6943'),
                'longitude': Decimal('-73.9207'),
                'start_date': date.today() + timedelta(days=14),
                'end_date': date.today() + timedelta(days=14),
                'open_time': time(16, 0),
                'close_time': time(22, 0),
            },
            {
                'title': 'Upper West Side Literary Salon',
                'description': 'Join fellow book lovers for an evening of literary discussion and readings. Featured author Q&A and wine reception included.',
                'event_type': 'Education',
                'icon': 'book',
                'price': Decimal('35.00'),
                'address': 'Upper West Side',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '10024',
                'latitude': Decimal('40.7870'),
                'longitude': Decimal('-73.9754'),
                'start_date': date.today() + timedelta(days=15),
                'end_date': date.today() + timedelta(days=15),
                'open_time': time(19, 0),
                'close_time': time(21, 30),
            },
            {
                'title': 'Red Hook Seafood Festival',
                'description': 'Celebrate Brooklyn\'s maritime heritage with fresh seafood, live music, and waterfront activities. Family-friendly event with boat tours and fishing demonstrations.',
                'event_type': 'Food',
                'icon': 'fish',
                'price': Decimal('30.00'),
                'address': 'Red Hook Waterfront',
                'city': 'Brooklyn',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '11231',
                'latitude': Decimal('40.6754'),
                'longitude': Decimal('-74.0157'),
                'start_date': date.today() + timedelta(days=18),
                'end_date': date.today() + timedelta(days=19),
                'open_time': time(11, 0),
                'close_time': time(19, 0),
            },
            {
                'title': 'Astoria Greek Cultural Festival',
                'description': 'Immerse yourself in Greek culture with traditional music, dance performances, authentic cuisine, and cultural exhibits in Queens\' vibrant Astoria neighborhood.',
                'event_type': 'Cultural',
                'icon': 'flag',
                'price': Decimal('15.00'),
                'address': 'Astoria Park',
                'city': 'Queens',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '11102',
                'latitude': Decimal('40.7829'),
                'longitude': Decimal('-73.9207'),
                'start_date': date.today() + timedelta(days=20),
                'end_date': date.today() + timedelta(days=21),
                'open_time': time(12, 0),
                'close_time': time(21, 0),
            },
            {
                'title': 'Manhattan Skyline Photography Workshop',
                'description': 'Capture stunning views of the Manhattan skyline from various vantage points. Professional photographer guidance, equipment tips, and post-processing techniques.',
                'event_type': 'Education',
                'icon': 'camera',
                'price': Decimal('75.00'),
                'address': 'Various Manhattan Locations',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '10001',
                'latitude': Decimal('40.7589'),
                'longitude': Decimal('-73.9851'),
                'start_date': date.today() + timedelta(days=25),
                'end_date': date.today() + timedelta(days=25),
                'open_time': time(16, 0),
                'close_time': time(20, 0),
            }
        ]

        created_count = 0
        for event_data in events_data:
            # Check if event already exists
            if not Event.objects.filter(title=event_data['title']).exists():
                event = Event.objects.create(
                    created_by=user,
                    **event_data
                )
                # Add the creator as admin
                event.admins.add(user)
                created_count += 1
                self.stdout.write(f'Created event: {event.title} in {event.city}')
            else:
                self.stdout.write(f'Event already exists: {event_data["title"]}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new events!')
        )
        
        # Display summary
        total_events = Event.objects.count()
        nyc_events = Event.objects.filter(city='New York').count()
        brooklyn_events = Event.objects.filter(city='Brooklyn').count()
        queens_events = Event.objects.filter(city='Queens').count()
        
        self.stdout.write(f'\nEvent Summary:')
        self.stdout.write(f'Total events: {total_events}')
        self.stdout.write(f'New York City: {nyc_events}')
        self.stdout.write(f'Brooklyn: {brooklyn_events}')
        self.stdout.write(f'Queens: {queens_events}')
