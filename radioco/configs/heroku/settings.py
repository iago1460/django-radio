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


import dj_database_url

from radioco.configs.base.settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']  # FIXME: SECURITY ISSUE
SECRET_KEY = '(h_$1pj(&usx%kw^m6$7*x9pnar+t_136g!3)g#+eje5r^3(!!'  # FIXME: SECURITY ISSUE

DATABASES['default'] = dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

MIDDLEWARE_CLASSES += (
    'whitenoise.middleware.WhiteNoiseMiddleware',
)

# STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'  # FIXME: crash

# Import local settings
try:
    from local_settings import *
except ImportError:
    pass
