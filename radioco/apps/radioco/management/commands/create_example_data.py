from django.core.management.base import BaseCommand

from radioco.apps.radioco.utils import create_example_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_example_data()
