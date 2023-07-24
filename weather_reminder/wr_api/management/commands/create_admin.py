from django.core.management.base import BaseCommand, CommandError
from django.db import connection, OperationalError

from wr_api.models import User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help="Admin's username")
        parser.add_argument('--password', type=str, help="Admin's password")
        parser.add_argument('--email', type=str, help="Admin's email")

    def handle(self, *args, **options):
        username = options.get('username')
        password = options.get('password')
        email = options.get('email')
        if not password:
            self.stdout.write(self.style.ERROR(f"Password is required!"))
            return

        exists = User.objects.filter(username=username)
        if exists:
            self.stdout.write(self.style.ERROR(f"{username} username already exists!"))
            return

        new_admin = User.objects.create_superuser(username=username, password=password, email=email)
        if not new_admin:
            self.stdout.write(self.style.ERROR(f"Something went wrong to create superuser!"))
            return

        self.stdout.write(self.style.SUCCESS(f"'{username}' admin was successfully created!"))
