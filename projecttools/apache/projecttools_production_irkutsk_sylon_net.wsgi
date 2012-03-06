import os
import sys

paths = ["/var/www/projecttools", "/var/www/projecttools/projecttools"]
for path in paths:
	if path not in sys.path:
		sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'projecttools.settings_production_irkutsk_sylon_net'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
