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


from radioco.configs.base.settings import *

DEBUG = False

USE_X_FORWARDED_HOST = True
ALLOWED_HOSTS = '*'  # FIXME: SECURITY ISSUE
SECRET_KEY = '(h_$1pj(&usx%kw^m6$7*x9pnar+t_136g!3)g#+eje5r^3(!!'  # FIXME: SECURITY ISSUE

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['OPENSHIFT_APP_NAME'],
        'USER': os.environ['OPENSHIFT_POSTGRESQL_DB_USERNAME'],
        'PASSWORD': os.environ['OPENSHIFT_POSTGRESQL_DB_PASSWORD'],
        'HOST': os.environ['OPENSHIFT_POSTGRESQL_DB_HOST'],
        'PORT': os.environ['OPENSHIFT_POSTGRESQL_DB_PORT']
    }
}
STATIC_URL = '/static/static/'
STATIC_ROOT = os.path.join(os.path.dirname(SITE_ROOT), 'wsgi/static/static')
MEDIA_URL = '/static/media/'
MEDIA_ROOT = os.path.join(os.environ.get('OPENSHIFT_DATA_DIR'), 'media')

# Import local settings
try:
    from local_settings import *
except ImportError:
    pass
