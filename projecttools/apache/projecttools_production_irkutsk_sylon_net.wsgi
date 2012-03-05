import site
site.addsitedir("/srv/python-environments/projecttools/lib/python2.7/site-packages")

import os
import sys

path = "/var/www/projecttools/projecttools"
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'projecttools.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
