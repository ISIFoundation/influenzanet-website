# Django settings for epiweb project.
# -*- coding: utf-8 -*-

DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = (
    ('Antwan Wiersma', 'webdev@grotegriepmeting.nl'),
    ('Klaas van Schelven', 'klaasvanschelven@gmail.com'), # please leave this setting for a minimal amount of spam-checking
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'influenzanet.db',             # Or path to database file if using sqlite3.
        'USER': '',             # Not used with sqlite3.
        'PASSWORD': '',         # Not used with sqlite3.
        'HOST': '',             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',             # Set to empty string for default. Not used with sqlite3.
    }
}


SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# For checking postcodes etc.
# Use ISO3166 two-letter country code
# See http://www.iso.org/iso/country_codes/iso_3166_code_lists/english_country_names_and_code_elements.htm
# Avaliable: be, it, nl, uk, pt, se
COUNTRY = 'en'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

LANGUAGES = (
   ('en', u'English'),
   ('de', u'Deutsch'),
   ('fr', u'Français'),
   ('nl', u'Nederlands'),
   ('it', u'Italiano'),
   ('sv', u'Svenska'),
   ('pt', u'Portugues'),
   ('es', u'Español'),
   ('da', u'Dansk'),
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
import os
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, 'locale'),
)
POLLSTER_CACHE_PATH = PROJECT_PATH

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
STATIC_URL = MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

CMS_FILE_ICON_PATH = os.path.join(MEDIA_ROOT, 'file_icons/')
CMS_FILE_ICON_URL = os.path.join(MEDIA_URL, 'file_icons/')

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'swgm*3%po62mg76m4iq!k8h3j+_)x=8b--7skjc_0wiak^wksr'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#    'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.sw_auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.media.PlaceholderMediaMiddleware',
#   'pybb.middleware.PybbMiddleware',
    'cms.middleware.multilingual.MultilingualURLMiddleware',
    'apps.pollster.middleware.ForceResponseMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "cms.context_processors.media",
    "sekizai.context_processors.sekizai",
    "django.contrib.messages.context_processors.messages",
    "apps.partnersites.context_processors.customizations",
#   "pybb.context_processors.processor",
#    "apps.pollster.context_processors.last_survey",
#    "apps.pollster.context_processors.surveyuser_count",
    "apps.survey.context_processors.household",
)

CMS_TEMPLATES = (
    ('base/threecol.html', "3 Columns"),
    ('base/twocol.html', "2 Columns"),
    ('base/influhome.html', "European Map"),
)

GEOMETRY_TABLES = (
 ('pollster_zip_codes','zip level'),
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
#   os.path.join(PROJECT_PATH, 'custom_templates'),
    os.path.join(PROJECT_PATH, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'nani',
    'south',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'sekizai',
    'apps.common',
#    'registration',
    'loginurl',
#   'apps.accounts',
    'apps.survey',
    'apps.reminder',
#    'apps.banner',
    'apps.search',
    'apps.journal',
#    'apps.sander',
#    'contact_form',
#   'apps.ew_contact_form',
    'apps.partnersites',
    'apps.count',
    'cms',
    'cms.plugins.text',
    'cms.plugins.picture',
    'cms.plugins.link',
    'cms.plugins.file',
    'cms.plugins.snippet',
#    'cms.plugins.googlemap',
    'menus',
    'mptt',
    'appmedia',
    'publisher',
    'haystack',
    'apps.pollster',
    'apps.municipal',
    'apps.sw_feedback',
    'apps.sw_auth',
    'apps.sw_cohort',
    'apps.sw_invitation',
#    'apps.contest',
#    'captcha',
    #'apps.tellafriend',
#   'pybb',
#   'pytils',
#   'sorl.thumbnail',
#   'pure_pagination',
    'apps.dashboard',
    'apps.grippenet',
    'apps.top5',
    'apps.ascor',
)

HAYSTACK_SITECONF = 'search_sites'

try:
    import xapian
    HAYSTACK_SEARCH_ENGINE = 'xapian'
    HAYSTACK_XAPIAN_PATH = '/tmp/xapian'
except:
    HAYSTACK_SEARCH_ENGINE = 'simple'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'apps.sw_auth.backend.EpiworkAuthBackend',
    'apps.sw_auth.backend.EpiworkTokenBackend',
    'loginurl.backends.LoginUrlBackend',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

CMSPLUGIN_NEWS_RSS_TITLE = "News"
CMSPLUGIN_NEWS_RSS_DESCRIPTION = "News List"

ACCOUNT_ACTIVATION_DAYS = 7

EMAIL_HOST = '127.0.0.1'

# Default e-mail address to use for various automated correspondence from
# the site managers.
DEFAULT_FROM_EMAIL = 'Influenzanet <webmaster@influenzanet.eu>'

if DEBUG:
	EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Subject-line prefix for email messages send with django.core.mail.mail_admins
# or ...mail_managers.  Make sure to include the trailing space.
EMAIL_SUBJECT_PREFIX = '[Influenzanet] '

EPIDB_API_KEY = '0000000000000000000000000000000000000000'
EPIDB_SERVER = 'http://127.0.0.1:8080/'

SURVEY_ID = 'gold-standard-weekly-1.6'
SURVEY_PROFILE_ID = 'gold-standard-intake-1.5'

MOBILE_INTERFACE_ACTIVE = False

STORE_RESPONSES_LOCALLY = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    }
}

# SEO Settings

GOOGLE_ANALYTICS_ACCOUNT = None
CMS_SEO_FIELDS = True

SESSION_COOKIE_AGE = 60 * 60 * 2

LOGIN_REDIRECT_URL = '/survey/main/'

# PyBB settings
#AUTH_PROFILE_MODULE = 'pybb.Profile'
#PYBB_TEMPLATE = 'base/forum.html'
#PYBB_ENABLE_ANONYMOUS_POST = True
#PYBB_ANONYMOUS_USERNAME = 'Gast'

LOCAL_APPS = ()
LOCAL_MIDDLEWARE = ()

try:
    from local_settings import *
except ImportError:
    pass

INSTALLED_APPS += LOCAL_APPS
MIDDLEWARE_CLASSES += LOCAL_MIDDLEWARE
