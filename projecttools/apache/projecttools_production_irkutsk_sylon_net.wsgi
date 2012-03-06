import os
import sys

path = "/var/www/projecttools"
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'projecttools.settings_production_irkutsk_sylon_net'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
