from settings import *

DEBUG = False
TEMPLATE_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/var/www/projecttools-example/projecttools/database.sqlite',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    '/var/www/projecttools-example/projecttools/templates'
)

STATIC_ROOT = "/var/www/projecttools-example/projecttools/sitestatic/"
LOGIN_URL = "/example/login/"
LOGIN_REDIRECT_URL = "/example/"
LOGOUT_URL = "/example/"
STATIC_URL = "/example/static/"
ADMIN_MEDIA_PREFIX = "/example/static/admin/"
SESSION_COOKIE_PATH = "/example/"
EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
