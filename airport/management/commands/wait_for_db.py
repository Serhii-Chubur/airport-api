# import os
import time
from django.db import connection, OperationalError

# import psycopg
from django.core.management.base import BaseCommand
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Waiting for database connection"
    load_dotenv()

    # def handle(self, *args, **options):
    #     count = 0
    #     max_count = 4
    #     while count < max_count:
    #         count += 1
    #         try:
    #             conn = psycopg.connect(
    #                 f"dbname={os.getenv('POSTGRES_DB')} "
    #                 f"user={os.getenv('POSTGRES_USER')} "
    #                 f"host={os.getenv('POSTGRES_HOST')} "
    #                 f"password={os.getenv('POSTGRES_PASSWORD')}"
    #                 f"port={os.getenv('POSTGRES_PORT')}"
    #             )
    #             conn.close()
    #             self.stdout.write(
    #                 self.style.SUCCESS("Database connection successful!")
    #             )
    #             break
    #         except psycopg.OperationalError:
    #             self.stdout.write(
    #                 self.style.ERROR("Database unavailable, retrying...")
    #             )
    #             sleep(3)
    #             if count == max_count:
    #                 raise CommandError(
    #                     "Max attempts exceeded. "
    #                     "Wasn't able to connect. Exiting..."
    #                 )
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
