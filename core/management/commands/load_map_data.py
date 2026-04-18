"""
Management command: load_map_data
-----------------------------------
Clears existing DemographicData then loads core/fixtures/map_data.json.
Uses bulk_create(ignore_conflicts=True) to skip any duplicate rows in the fixture.

Usage:
    python manage.py load_map_data --settings=haske_pro.settings.production
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Clear DemographicData and reload from core/fixtures/map_data.json, skipping duplicates."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default=None,
            help="Path to fixture file (default: core/fixtures/map_data.json)",
        )

    def handle(self, *args, **options):
        from core.models import DemographicData

        fixture_path = options["fixture"]
        if fixture_path is None:
            app_dir = Path(__file__).resolve().parent.parent.parent
            fixture_path = Path(app_dir) / "fixtures" / "map_data.json"
        else:
            fixture_path = Path(fixture_path)

        if not fixture_path.exists():
            self.stderr.write(self.style.ERROR(f"Fixture not found: {fixture_path}"))
            return

        # Truncate via raw SQL — clears any orphaned rows Django ORM can't see
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            cursor.execute("TRUNCATE TABLE core_demographicdata;")
            try:
                cursor.execute("TRUNCATE TABLE core_historicaldemographicdata;")
            except Exception:
                pass  # table may not exist
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
        self.stdout.write("Truncated core_demographicdata table.")

        # Parse fixture and build model instances
        raw = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.stdout.write(f"Parsed {len(raw)} records from fixture.")

        # Fields to skip — FK refs (user) and auto timestamps handled by Django
        SKIP_FIELDS = {"created_by", "last_modified_by", "created_at", "updated_at"}

        seen = set()
        instances = []
        skipped = 0

        for entry in raw:
            fields = entry["fields"]
            key = (
                fields.get("state", ""),
                fields.get("lga", ""),
                fields.get("ward", ""),
                fields.get("village", ""),
            )
            if key in seen:
                skipped += 1
                continue
            seen.add(key)

            obj_fields = {k: v for k, v in fields.items() if k not in SKIP_FIELDS}
            if entry.get("pk"):
                obj_fields["id"] = entry["pk"]
            instances.append(DemographicData(**obj_fields))

        if skipped:
            self.stdout.write(self.style.WARNING(f"Skipped {skipped} duplicate rows in fixture."))

        # Insert in batches, skipping any remaining conflicts
        BATCH = 200
        inserted = 0
        for i in range(0, len(instances), BATCH):
            batch = instances[i:i + BATCH]
            DemographicData.objects.bulk_create(batch, ignore_conflicts=True)
            inserted += len(batch)

        final_count = DemographicData.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"✓ Inserted {final_count} records ({skipped} duplicates in fixture were skipped)."
        ))
