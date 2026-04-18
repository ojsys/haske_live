"""
Management command: dump_seed
------------------------------
Dumps all site-content models to core/fixtures/seed.json.
Excludes user submissions, demographic data, audit history, and auth tables.

Usage (local dev):
    python manage.py dump_seed

Then commit / transfer seed.json to the server and run:
    python manage.py loaddata core/fixtures/seed.json --settings=haske_pro.settings.production
"""

import json
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand


# ── Content models to seed ────────────────────────────────────────────────────
# Order matters: parent models before child models (FK constraints).
SEED_MODELS = [
    # Site-wide
    "core.SiteLogo",

    # Home page
    "core.HeroSlide",
    "core.Statistics",
    "core.Achievement",
    "core.MinistrySection",
    "core.Ministry",
    "core.Activity",
    "core.Gallery",

    # About page
    "core.AboutPage",
    "core.AboutMinistry",
    "core.MissionVision",
    "core.Challenge",
    "core.BoardMember",

    # Projects page
    "core.ProjectPage",
    "core.Project",

    # Volunteer page
    "core.VolunteerPage",
    "core.GoTeam",
    "core.PrayerPartner",
    "core.GiveSection",

    # Media / blog
    "core.MediaPage",
    "core.BlogPost",
    "core.BlogImage",
    "core.YouTubeVideo",
    "core.SpotifyPodcast",

    # Give / donate
    "core.DonationPage",
    "core.BankAccount",

    # Custom pages (page builder)
    "core.Page",
    "core.PageSection",
    "core.PageSectionCard",

    # ── Excluded ──────────────────────────────────────────────────────────────
    # core.DemographicData  — large dataset; migrate separately
    # core.Subscriber       — user submissions
    # core.VolunteerApplication — user submissions
    # core.ContactSubmission    — user submissions
    # core.Historical*          — django-simple-history; auto-rebuilt on prod
    # auth.*  / admin.LogEntry  — security; create superuser manually on prod
]


class Command(BaseCommand):
    help = "Dump site content to core/fixtures/seed.json for production seeding."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default=None,
            help="Output file path (default: core/fixtures/seed.json)",
        )
        parser.add_argument(
            "--indent",
            type=int,
            default=2,
            help="JSON indentation level (default: 2)",
        )

    def handle(self, *args, **options):
        output_path = options["output"]
        if output_path is None:
            # Place next to this app
            app_dir = Path(__file__).resolve().parent.parent.parent
            output_path = app_dir / "fixtures" / "seed.json"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.stdout.write("Dumping content models…")

        buf = StringIO()
        call_command(
            "dumpdata",
            *SEED_MODELS,
            indent=options["indent"],
            stdout=buf,
        )

        raw = buf.getvalue()

        # Sanity-check: valid JSON
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            self.stderr.write(self.style.ERROR(f"dumpdata produced invalid JSON: {exc}"))
            return

        # Null out user FK fields — production won't have the same users
        for entry in data:
            for field in ("created_by", "last_modified_by"):
                if field in entry.get("fields", {}):
                    entry["fields"][field] = None

        output_path.write_text(json.dumps(data, indent=options["indent"]), encoding="utf-8")

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Dumped {len(data)} objects → {output_path}"
            )
        )
        self.stdout.write("")
        self.stdout.write("Next steps:")
        self.stdout.write("  1. Transfer media files to production:")
        self.stdout.write("       rsync -avz -e 'ssh -p 2222' media/ lightofl@lightoflifeafrica.org.ng:/home/lightofl/haske_live/media/")
        self.stdout.write("  2. Upload seed.json to the server:")
        self.stdout.write("       scp -P 2222 core/fixtures/seed.json lightofl@lightoflifeafrica.org.ng:/home/lightofl/haske_live/core/fixtures/")
        self.stdout.write("  3. On the server, load the fixture:")
        self.stdout.write("       python manage.py loaddata core/fixtures/seed.json --settings=haske_pro.settings.production")
