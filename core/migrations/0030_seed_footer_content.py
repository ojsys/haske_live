from django.db import migrations


QUICK_LINKS = [
    ('Home', '/'),
    ('About Us', '/about/'),
    ('Projects', '/projects/'),
    ('Volunteer', '/volunteer/'),
    ('Media', '/media/'),
    ('Blog', '/blog/'),
]

INVOLVED_LINKS = [
    ('Give / Donate', '/give/'),
    ('Go-Teams', '/volunteer/'),
    ('Prayer Partners', '/volunteer/'),
    ('Partner With Us', '/contact/'),
    ('Impact Map', '/map/'),
]

SOCIALS = [
    ('Facebook', 'fab fa-facebook-f', 'https://www.facebook.com/profile.php?id=100065205799702'),
    ('TikTok', 'fab fa-tiktok', 'https://www.tiktok.com/@haskenrayuwaafrika'),
    ('Instagram', 'fab fa-instagram', 'https://www.instagram.com/haske_project'),
    ('YouTube', 'fab fa-youtube', 'https://www.youtube.com/@HaskeProject'),
    ('Telegram', 'fab fa-telegram-plane', 'https://t.me/+4jsirMTmyn43ODBk'),
]


def seed(apps, schema_editor):
    """Populate the footer tables with the values previously hardcoded in base.html."""
    FooterSettings = apps.get_model('core', 'FooterSettings')
    FooterLink = apps.get_model('core', 'FooterLink')
    FooterSocial = apps.get_model('core', 'FooterSocial')

    if not FooterSettings.objects.exists():
        FooterSettings.objects.create()

    if not FooterLink.objects.exists():
        for i, (label, url) in enumerate(QUICK_LINKS):
            FooterLink.objects.create(column='quick', label=label, url=url, order=i)
        for i, (label, url) in enumerate(INVOLVED_LINKS):
            FooterLink.objects.create(column='involved', label=label, url=url, order=i)

    if not FooterSocial.objects.exists():
        for i, (name, icon, url) in enumerate(SOCIALS):
            FooterSocial.objects.create(name=name, icon=icon, url=url, order=i)


def unseed(apps, schema_editor):
    """No-op — the tables are dropped by the schema migration on reverse."""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_footerlink_footersocial_footersettings_and_more'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
