from apscheduler.jobstores.base import ConflictingIdError
from django.core.management.base import BaseCommand

from WRapi.scheduler import create_jobs
from WRapi.weather_getter import update_weather_data


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('action', choices=['run', 'stop', 'weather'], help='Action to perform: run or stop')

    def handle(self, *args, **options):
        action = options['action']

        if action == 'run':
            create_jobs()
        elif action == 'weather':
            update_weather_data()
        else:
            self.stdout.write(self.style.ERROR(f"Invalid action: {action}. Must be either 'run' or 'stop'."))
