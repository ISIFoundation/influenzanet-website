# Django settings for epiweb project.
# -*- coding: iso-8859-15 -*-

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'ggm.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nl'
# LANGUAGE_CODE = 'en'

# For checking postcodes etc.
# Use ISO3166 two-letter country code
# See http://www.iso.org/iso/country_codes/iso_3166_code_lists/english_country_names_and_code_elements.htm
# Avaliable: be, it, nl, uk, pt, se
COUNTRY = 'nl'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

LANGUAGES = (
   ('nl', 'Nederlands'),
   ('fr', 'Français'),
)

#CMS_LANGUAGES = (
#  ('nl', gettext('Nederlands')),
#  ('fr', gettext('Francais')),
#)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
import os
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/+media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'swgm*3%po62mg76m4iq!k8h3j+_)x=8b--7skjc_0wiak^wksr'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#    'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#	'cms.middleware.multilingual.MultilingualURLMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "cms.context_processors.media",
)

CMS_TEMPLATES = (
    ('base/threecol.html', "3 Columns"),
    ('base/twocol.html', "2 Columns"),
)

ROOT_URLCONF = 'epiweb.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates/base'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'epiweb',
    'registration',
    'loginurl',
    'epiweb.apps.accounts',
    'epiweb.apps.survey',
    'epiweb.apps.reminder',
    'epiweb.apps.banner',
    'cms',
#    'menu',
    'cms.plugins.text',
    'cms.plugins.picture',
#    'cms.plugins.link',
#    'cms.plugins.file',
    'cms.plugins.snippet',
#    'cms.plugins.googlemap',
    'journal',
    'mptt',
    'publisher',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'loginurl.backends.LoginUrlBackend',
)

CMSPLUGIN_NEWS_RSS_TITLE = "News"
CMSPLUGIN_NEWS_RSS_DESCRIPTION = "News List"

ACCOUNT_ACTIVATION_DAYS = 7

EMAIL_HOST='127.0.0.1'

# Default e-mail address to use for various automated correspondence from
# the site managers.
DEFAULT_FROM_EMAIL = 'webmaster@influenzanet.com'

# Subject-line prefix for email messages send with django.core.mail.mail_admins
# or ...mail_managers.  Make sure to include the trailing space.
EMAIL_SUBJECT_PREFIX = '[Influenzanet] '

REMINDER_FROM = 'reminder-no-reply@epiwork.example'
REMINDER_USE_LOGINURL = True
REMINDER_LOGINURL_EXPIRES = 7
REMINDER_HTML = False

EPIDB_API_KEY = '0000000000000000000000000000000000000000'
EPIDB_SERVER = 'http://127.0.0.1:8080/'

SURVEY_ID = 'gold-standard-weekly-1.6'
SURVEY_PROFILE_ID = 'gold-standard-intake-1.5'
EXTRA_SURVEY = False

MOBILE_INTERFACE_ACTIVE = False

STORE_RESPONSES_LOCALLY = False

import socket
_hostname = socket.gethostname()
if _hostname in ['rawon.local']:
    EPIDB_SERVER = 'http://192.168.100.100:8080/'
    EMAIL_PORT = 2525
elif _hostname in ['rekenwolk.nl']:
    EPIDB_SERVER = 'http://178.18.82.138:8080/'
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 25
    MOBILE_INTERFACE_ACTIVE = True
    STORE_RESPONSES_LOCALLY = True
    EXTRA_SURVEY = 'contact-survey-1.0'
elif _hostname in ['via']:
    MOBILE_INTERFACE_ACTIVE = True
    STORE_RESPONSES_LOCALLY = True
    EXTRA_SURVEY = 'contact-survey-1.0'

