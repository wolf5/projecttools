import os
import sys

# Even though this might look like an ugly hack, this seems to be the way to go
# (see the sys.path.append part in 
# http://code.google.com/p/modwsgi/wiki/IntegrationWithDjango#Integration_With_Django)
paths = ["/var/www/projecttools", "/var/www/projecttools/projecttools"]
for path in paths:
	if path not in sys.path:
		sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'projecttools.settings_production_irkutsk_sylon_net'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
