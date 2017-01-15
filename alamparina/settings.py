"""
Django settings for alamparina project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY','aa%1e*xipej7@2ir6d7d)$ra*-e67l)q-@c7-376g)(t$0tb20gz')
#'aa%1e*xipej7@2ir6d7d)$ra*-e67l)q-@c7-376g)(t$0tb20gz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('ALAMPARINA_DEBUG', True)

ALLOWED_HOSTS = ['*']

ADMINS = (
    ("Roberto", "80.pereira@gmail.com") #envia email caso ocorra erro 500 e debug=false
)

TEMPLATE_DEBUG = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'alamparina',
    'administrativo',
    'operacional',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'alamparina.urls'

WSGI_APPLICATION = 'alamparina.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

PRODUCAO = os.environ.get('ALAMPARINA_PRODUCAO', False)

if not PRODUCAO:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'alamparina',                      # Or path to database file if using sqlite3.
            'USER': 'root',                      # Not used with sqlite3.
            'PASSWORD': 'toor',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '3306',
        }
    }
else:
    # producao
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': os.environ.get('ALAMPARINA_DB_NAME'),                      # Or path to database file if using sqlite3.
            'USER': os.environ.get('ALAMPARINA_DB_USER'),                      # Not used with sqlite3.
            'PASSWORD': os.environ.get('ALAMPARINA_DB_PASSWORD'),                  # Not used with sqlite3.
            'HOST': os.environ.get('ALAMPARINA_DB_URL'),                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '3306',
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

if PRODUCAO:
    AWS_HEADERS = {  # see http://developer.yahoo.com/performance/rules.html#expires
            'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
            'Cache-Control': 'max-age=94608000',
        }


    ALAMPARINA_S3_ACCESS_KEY_DEV = os.environ.get('ALAMPARINA_AWS_ID')
    ALAMPARINA_S3_SECRET_ACCESS_KEY = os.environ.get('ALAMPARINA_AWS_ID_ID')

    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_ALAMPARINA_STORAGE', 'loja01')
    AWS_ACCESS_KEY_ID = os.environ.get('ALAMPARINA_AWS_ACCESS_KEY', ALAMPARINA_S3_ACCESS_KEY_DEV)
    AWS_SECRET_ACCESS_KEY = os.environ.get('ALAMPARINA_AWS_SECRET_ACCESS_KEY', ALAMPARINA_S3_SECRET_ACCESS_KEY)

    # Tell django-storages that when coming up with the URL for an item in S3 storage, keep
    # it simple - just use this domain plus the path. (If this isn't set, things get complicated).
    # This controls how the `static` template tag from `staticfiles` gets expanded, if you're using it.
    # We also use it in the next setting.
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

    # This is used by the `static` template tag from `static`, if you're using that. Or if anything else
    # refers directly to STATIC_URL. So it's safest to always set it.
    STATIC_URL = "https://%s/static/" % AWS_S3_CUSTOM_DOMAIN
    MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

    # Tell the staticfiles app to use S3Boto storage when writing the collected static files (when
    # you run `collectstatic`).
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

    AWS_LOCATION = ''

    DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'
    #
    # MESSAGE_TAGS = {
    #     messages.SUCCESS: 'alert-success success',
    #     messages.WARNING: 'alert-warning warning',
    #     messages.ERROR: 'alert-danger error'
    # }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                "django.core.context_processors.request",
            ],
        },
    },
]

try:
  from settings_local import *
except ImportError:
  pass

