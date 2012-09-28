#!/usr/bin/env python
from django.core.management import execute_manager
import imp
try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings

# The module pydevd is only present in development environments, and only needed there.
# In production environments, it is not needed, thus the failing import is ignored.
try: 
    import pydevd
    pydevd.patch_django_autoreload()
except Exception as exception:
    pass

if __name__ == "__main__":
    execute_manager(settings)
