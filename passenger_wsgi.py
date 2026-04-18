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

# ── Environment variables ──────────────────────────────────────────────────────
os.environ['PIPELINE']   = 'production'
os.environ['SECRET_KEY'] = 'REPLACE-WITH-A-LONG-RANDOM-SECRET-KEY'
os.environ['DEBUG']      = 'False'

# MySQL database (cPanel)
os.environ['DB_NAME']    = 'lightofl_haske_db'
os.environ['DB_USER_NM'] = 'lightofl_haskedb_user'
os.environ['DB_USER_PW'] = 'REPLACE-WITH-DB-PASSWORD'
os.environ['DB_IP']      = 'localhost'
os.environ['DB_PORT']    = '3306'

# ── WSGI application ───────────────────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haske_pro.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
