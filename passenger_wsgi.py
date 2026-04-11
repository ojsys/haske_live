import os
import sys

from django.core.wsgi import get_wsgi_application

# Add your project directory to the sys.path
path = '/home/lightofl/haske/haske_pro'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'haske_pro.settings'

application = get_wsgi_application()