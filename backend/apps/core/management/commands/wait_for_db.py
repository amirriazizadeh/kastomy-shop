import time
from django.db.utils import OperationalError
from django.db import connections
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for postgres...")
        db_conn = None
        while not db_conn:
            try:
                connections["default"].ensure_connection()
                db_conn = True
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("PostgreSQL started"))
