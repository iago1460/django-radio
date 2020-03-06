# Radioco - Broadcasting Radio Recording Scheduling system.
# Copyright (C) 2014  Iago Veloso Abalo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os


def str_to_bool(text):
    return str(text).lower() not in ('none', 'false', 'no', '0')


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

##################################################################################
# To override this settings create a "local_settings.py" file in same location.  #
# RadioCo Settings                                                               #
# http://django-radio.readthedocs.org/en/latest/reference/configuration.html     #
##################################################################################


SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = str_to_bool(os.environ.get('DEBUG'))
TESTING_MODE = False
ALLOWED_HOSTS = '*'

# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'grappelli',
    'filebrowser',

    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.humanize',

    'ckeditor',
    'ckeditor_uploader',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'disqus',
    'recurrence',

    # Local Project Apps
    'radioco.apps.api',
    'radioco.apps.users',
    'radioco.apps.programmes',
    'radioco.apps.schedules',
    'radioco.apps.global_settings',
    'radioco.apps.radioco',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (
            os.path.join(SITE_ROOT, 'templates'),
        ),
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'radioco.apps.radioco.context_processors.settings',
            ),
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ),
        },
    },
]

ROOT_URLCONF = 'radioco.configs.base.urls'
TEST_RUNNER = 'radioco.configs.base.test_runner.MyTestSuiteRunner'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
        'PORT': 5432,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = os.environ['TIME_ZONE']

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


LOCALE_PATHS = (
    os.path.join(SITE_ROOT, 'locale'),
)

LOGIN_URL = 'admin:index'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

SITE_ID = 1

# Filebrowser
FILEBROWSER_URL_FILEBROWSER_MEDIA = STATIC_URL + "filebrowser/"
FILEBROWSER_PATH_FILEBROWSER_MEDIA = os.path.join(STATIC_URL, 'filebrowser/')
FILEBROWSER_VERSIONS = {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    'thumbnail': {'verbose_name': 'Thumbnail (1 col)', 'width': 60, 'height': 60, 'opts': 'crop'},
    'small': {'verbose_name': 'Small (2 col)', 'width': 140, 'height': '', 'opts': ''},
    'medium': {'verbose_name': 'Medium (4col )', 'width': 300, 'height': '', 'opts': ''},
    'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': ''},
    'large': {'verbose_name': 'Large (8 col)', 'width': 680, 'height': '', 'opts': ''},

    'item_overlap': {'verbose_name': 'Big (6 col)', 'width': 600, 'height': 450, 'opts': 'crop upscale'},
    'programme_preview': {'verbose_name': 'Big (6 col)', 'width': 800, 'height': 600, 'opts': 'crop upscale'},
    'person_preview': {'verbose_name': 'Big (6 col)', 'width': 600, 'height': 600, 'opts': 'crop upscale'},
    'rss_image': {'verbose_name': 'Big (6 col)', 'width': 144, 'height': 144, 'opts': 'crop'},
    'itunes_image': {'verbose_name': 'Big (6 col)', 'width': 1400, 'height': 1400, 'opts': 'crop upscale'},
}
FILEBROWSER_ADMIN_VERSIONS = [
    'thumb', 'small', 'medium', 'large',
]

# RadioCo Settings
# http://django-radio.readthedocs.org/en/latest/reference/configuration.html

USERNAME_RADIOCO_RECORDER = 'RadioCo_Recorder'

# CKEditor
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'

# Available Languages
gettext_noop = lambda s: s
PROGRAMME_LANGUAGES = (
    ('es', gettext_noop('Spanish')),
    ('en', gettext_noop('English')),
    ('gl', gettext_noop('Galician')),
)

# Disqus
DISQUS_ENABLE = bool(os.environ['DISQUS_API_KEY'])
DISQUS_API_KEY = os.environ['DISQUS_API_KEY']
DISQUS_WEBSITE_SHORTNAME = os.environ['DISQUS_WEBSITE_SHORTNAME']

# Admin
GRAPPELLI_ADMIN_HEADLINE = 'RadioCo'
GRAPPELLI_ADMIN_TITLE = 'RadioCo'

# Import local settings
try:
    from local_settings import *
except ImportError:
    pass


if DEBUG:
    # Django Debug Toolbar
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }
else:
    # Enabling cache
    TEMPLATES[0]['OPTIONS']['loaders'] = [('django.template.loaders.cached.Loader', TEMPLATES[0]['OPTIONS']['loaders'])]
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': 'memcached:11211',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'