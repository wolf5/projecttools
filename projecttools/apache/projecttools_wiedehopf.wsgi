# Taken from http://blog.dscpl.com.au/2010/03/improved-wsgi-script-for-use-with.html

import sys
sys.path.insert(0, "/var/www/projecttools-wiedehopf/projecttools")

import site
site.addsitedir("/usr/local/pythonenv/projecttools-wiedehopf/lib/python2.6/site-packages")

import settings_wiedehopf

import django.core.management
django.core.management.setup_environ(settings_wiedehopf)
utility = django.core.management.ManagementUtility()
command = utility.fetch_command('runserver')

command.validate()

import django.conf
import django.utils

django.utils.translation.activate(django.conf.settings.LANGUAGE_CODE)

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
