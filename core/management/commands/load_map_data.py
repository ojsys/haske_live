"""
Management command: load_map_data
-----------------------------------
Clears existing DemographicData then loads core/fixtures/map_data.json.
Safer than running loaddata directly when data may already exist.

Usage:
    python manage.py load_map_data --settings=haske_pro.settings.production
"""

from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clear DemographicData and reload from core/fixtures/map_data.json."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default=None,
            help="Path to fixture file (default: core/fixtures/map_data.json)",
        )

    def handle(self, *args, **options):
        fixture_path = options["fixture"]
        if fixture_path is None:
            app_dir = Path(__file__).resolve().parent.parent.parent
            fixture_path = str(app_dir / "fixtures" / "map_data.json")

        # Clear existing data
        from core.models import DemographicData
        count = DemographicData.objects.count()
        DemographicData.objects.all().delete()
        self.stdout.write(f"Cleared {count} existing records.")

        # Load fresh
        self.stdout.write("Loading map_data.json…")
        call_command("loaddata", fixture_path)

        new_count = DemographicData.objects.count()
        self.stdout.write(self.style.SUCCESS(f"✓ Loaded {new_count} records."))
