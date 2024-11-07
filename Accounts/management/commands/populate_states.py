# app1/management/commands/populate_states.py

from django.core.management.base import BaseCommand
from app1.models import State
import pycountry

class Command(BaseCommand):
    help = 'Populates the State model with state names within India'

    def handle(self, *args, **kwargs):
        country_code = 'IN'  # ISO 3166-1 alpha-2 code for India
        
        for subdivision in pycountry.subdivisions.get(country_code=country_code):
            # Get state name
            state_name = subdivision.name

            # Check for existing records before creating
            existing_record = State.objects.filter(name=state_name).first()
            if existing_record:
                self.stdout.write(self.style.WARNING(f"Duplicate state name found: {state_name}. Skipping..."))
                continue

            # Create a new state record
            State.objects.create(name=state_name)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated State model with Indian states'))
