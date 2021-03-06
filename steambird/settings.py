import os
from importlib.util import find_spec

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g+9hmm0y!48$_vaj=0&=mr%=pdd*c7&i&@8a)t=qow-!fh6vs!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") in ["True", "1", "true"]

INTERNAL_IPS = ('127.0.0.1',)
ALLOWED_HOSTS = ([
    '127.0.0.1',
    'localhost'
] if DEBUG else ['*'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'polymorphic',
    'modeltranslation',

    'steambird',
    'steambird.boecie',
    'steambird.teacher',
    'steambird.material_management',

    'pysidian_core',
    'django_select2',
    'django_addanother',
] + ([
    'django_uwsgi',
] if find_spec('django_uwsgi') else [
]) + ([
    'rosetta',
    'debug_toolbar',
] if DEBUG else [
])

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
] + ([
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] if DEBUG else [
])

ROOT_URLCONF = 'steambird.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'steambird.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': os.getenv('DB_NAME', 'stoomvogel'),
        'USER': os.getenv('DB_USERNAME', 'stoomvogel'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'stoomvogel'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGES = [
    ('nl', _('Dutch')),
    ('en', _('English')),
]

LANGUAGE_CODE = 'en'


TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# How to generate locale files:
# https://docs.djangoproject.com/en/2.1/topics/i18n/translation/#localization-how-to-create-language-files
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Login URL
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

# Configures email backends
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = '130.89.148.239'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

try:
    # pylint: disable=wildcard-import, unused-wildcard-import
    from .local import *
except ImportError:
    print("Failed to import local.py. It is recommended to add them.")
