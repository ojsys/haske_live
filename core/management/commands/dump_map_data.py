"""
Management command: dump_map_data
-----------------------------------
Dumps DemographicData to core/fixtures/map_data.json.
Kept separate from dump_seed because this dataset can be large.

Usage (local dev):
    python manage.py dump_map_data

Then transfer to server and load:
    scp -P 2222 core/fixtures/map_data.json lightofl@lightoflifeafrica.org.ng:/home/lightofl/haske_live/core/fixtures/
    python manage.py loaddata core/fixtures/map_data.json --settings=haske_pro.settings.production
"""

import json
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Dump DemographicData (map data) to core/fixtures/map_data.json."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=None,
            help="Output file path (default: core/fixtures/map_data.json)",
        )

    def handle(self, *args, **options):
        output_path = options["output"]
        if output_path is None:
            app_dir = Path(__file__).resolve().parent.parent.parent
            output_path = app_dir / "fixtures" / "map_data.json"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.stdout.write("Dumping DemographicData…")

        buf = StringIO()
        call_command(
            "dumpdata",
            "core.DemographicData",
            indent=2,
            stdout=buf,
            natural_foreign=True,
            natural_primary=True,
        )

        raw = buf.getvalue()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            self.stderr.write(self.style.ERROR(f"dumpdata produced invalid JSON: {exc}"))
            return

        output_path.write_text(raw, encoding="utf-8")

        self.stdout.write(
            self.style.SUCCESS(f"✓ Dumped {len(data)} records → {output_path}")
        )
        self.stdout.write("")
        self.stdout.write("To load on production:")
        self.stdout.write(
            "  scp -P 2222 core/fixtures/map_data.json "
            "lightofl@lightoflifeafrica.org.ng:/home/lightofl/haske_live/core/fixtures/"
        )
        self.stdout.write(
            "  python manage.py loaddata core/fixtures/map_data.json "
            "--settings=haske_pro.settings.production"
        )
