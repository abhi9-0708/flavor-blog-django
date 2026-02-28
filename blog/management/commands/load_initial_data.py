from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Load initial data from fixtures'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force load even if data exists')

    def handle(self, *args, **options):
        from blog.models import Post

        if Post.objects.exists() and not options['force']:
            self.stdout.write(self.style.SUCCESS('Posts already exist. Skipping. Use --force to reload.'))
            return

        base_dir = settings.BASE_DIR
        fixture = os.path.join(base_dir, 'all_data.json')

        if os.path.exists(fixture):
            self.stdout.write(f'Loading data from {fixture}...')
            try:
                call_command('loaddata', fixture, verbosity=2)
                self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error loading data: {e}'))
        else:
            self.stdout.write(self.style.WARNING(f'Fixture file not found: {fixture}'))
