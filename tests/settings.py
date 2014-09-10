SECRET_KEY = 'asdf'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

import logging
logging.disable(logging.CRITICAL)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    # External apps
    'oscar_sagepay',
]
from oscar import get_core_apps
INSTALLED_APPS = INSTALLED_APPS + get_core_apps()

from oscar.defaults import *  # noqa

OSCAR_SAGEPAY_VENDOR = 'tangentlabs'
OSCAR_SAGEPAY_VPS_PROTOCOL = '2.23'
