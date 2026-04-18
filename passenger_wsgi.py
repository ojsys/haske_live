import os
import sys

# ── Paths ─────────────────────────────────────────────────────────────────────
# Project root (the folder that contains manage.py)
PROJECT_ROOT = '/home/lightofl/haske_live'
# Virtualenv site-packages — update python3.X to match your cPanel Python version
VENV_SITE = '/home/lightofl/haske_live/venv/lib/python3.11/site-packages'

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if VENV_SITE not in sys.path:
    sys.path.insert(1, VENV_SITE)

# ── Tell settings/__init__.py to use the production config ────────────────────
# All other secrets (SECRET_KEY, DB_*, DEBUG) are loaded from .env automatically
os.environ['PIPELINE'] = 'production'

# ── WSGI application ───────────────────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haske_pro.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
