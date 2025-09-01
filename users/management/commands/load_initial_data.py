from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Load initial data'

    def handle(self, *args, **options):
        # You'll paste your data here or load from a file
        call_command('loaddata', 'initial_data.json')
        self.stdout.write(self.style.SUCCESS('Initial data loaded successfully'))