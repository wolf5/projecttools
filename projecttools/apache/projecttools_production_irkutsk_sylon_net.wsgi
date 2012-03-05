ALLDIRS = ['/srv/python-environments/projecttools/lib/python2.7/site-packages']

import sys 
import site 

# Remember original sys.path.
prev_sys_path = list(sys.path) 

# Add each new site-packages directory.
for directory in ALLDIRS:
  site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = [] 
for item in list(sys.path): 
    if item not in prev_sys_path: 
        new_sys_path.append(item) 
        sys.path.remove(item) 
sys.path[:0] = new_sys_path 

import os

path = "/var/www/projecttools/projecttools"
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'projecttools.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
