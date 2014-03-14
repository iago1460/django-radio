"""
Django settings for radio project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'llkjw3(_3i$708vzrvnjff+4cdeedg(w(eq@5rqc+z#ysxw1l3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'bootstrap_admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'radio',
    'radio.libs.home',
    'radio.apps.users',
    'radio.apps.programmes',
    'radio.apps.schedules',
    'radio.apps.dashboard',
    'debug_toolbar',
    'bootstrap3',
    'floppyforms',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'radio.global_vars.global_vars',
)
"""
TEMPLATE_CONTEXT_PROCESSORS = (
    # 'ism.context_processor.user_vars',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'pipeline.middleware.MinifyHTMLMiddleware',
)"""

ROOT_URLCONF = 'radio.urls'

WSGI_APPLICATION = 'radio.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME': 'radio',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_TZ = False
USE_L10N = False


LANGUAGES = (
    ('en', 'English'),
    ('es', 'Spanish'),
)



ABSOLUTE_PATHNAME = '/home/user/git/django-radio'

LOCALE_PATHS = (ABSOLUTE_PATHNAME + '/radio/locale',)

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    ABSOLUTE_PATHNAME + '/static',
)
MEDIA_ROOT = ABSOLUTE_PATHNAME + '/resources/'
MEDIA_URL = '/media/'


CRISPY_TEMPLATE_PACK = 'bootstrap3'

GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}

# Variables
LOGIN_URL = 'login'  # name of url pattern
SITE_NAME = 'Radio'
