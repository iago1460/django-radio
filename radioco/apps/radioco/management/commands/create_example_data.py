from django.core.management.base import BaseCommand

from radioco.apps.programmes.models import Programme
from radioco.apps.radioco.utils import create_example_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        if Programme.objects.exists():
            print('There is already some data in the db, skipping creation...')
        else:
            create_example_data()
