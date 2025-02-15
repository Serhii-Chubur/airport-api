import time

from django.core.management.base import BaseCommand
from django.db import connection, OperationalError
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Waiting for database connection"
    load_dotenv()

    def handle(self, *args, **options):
        """Handle the command"""
        self.stdout.write("Waiting for database...")
        db_conn = None
        while not db_conn:
            try:
                connection.ensure_connection()
                db_conn = True
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
