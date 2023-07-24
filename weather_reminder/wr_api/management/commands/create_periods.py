from django.core.management.base import BaseCommand, CommandError
from django.db import connection, OperationalError

from wr_api.models import Period


PERIODS = [(1, '1,3,5,7,9,11,13,15,17,19,21,23'),
           (2, '2,4,8,10,14,16,20,22'),
           (6, '6,18'),
           (12, '0,12')]


class Command(BaseCommand):

    def create_period_objects(self):
        for interval, hours in PERIODS:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            except OperationalError as e:
                raise CommandError("No access to the database: ", str(e))

            exists = Period.objects.filter(interval=interval).first()
            if exists:
                self.stdout.write(self.style.ERROR(f"{interval} hour interval Period already exists..."))
                continue
            created = Period.objects.create(interval=interval, hours=hours)
            if not created:
                self.stdout.write(self.style.ERROR(f"There was an error to create Period({interval}, {hours})"))
            self.stdout.write(self.style.SUCCESS(f"{interval} hour interval Period created!"))

    def handle(self, *args, **options):
        self.create_period_objects()
