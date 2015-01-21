# -*- coding: utf-8 -*-
import os
import sys

abspath = lambda *p: os.path.abspath(os.path.join(*p))

PROJECT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = abspath(os.path.dirname(__file__))

SITE_ID = 1
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': abspath(PROJECT_ROOT, '.hidden.db'),
        'TEST_NAME': ':memory:',
    },
}

SECRET_KEY = 'CHANGE_THIS_TO_SOMETHING_UNIQUE_AND_SECURE'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEST_RUNNER = 'django.test.simple.DjangoTestSuiteRunner'

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

BASIC_EMAIL_DIRECTORY = os.path.join(PROJECT_DIR, 'templates/emails')

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'basic_email',
    'tests',
)


STATIC_URL = '/static/'

COVERAGE_EXCLUDE_MODULES = (
    "basic_email.migrations.*",
    "basic_email.tests*",
    "basic_email.urls",
    "basic_email.__init__",
)

COVERAGE_HTML_REPORT = True
COVERAGE_BRANCH_COVERAGE = False
TESTING = ('test' in sys.argv) or ('jenkins' in sys.argv) or ('tox' in sys.argv)
if not TESTING:
    try:
        from local_settings import *
    except ImportError:
        print ("no local_settings.py file?")
