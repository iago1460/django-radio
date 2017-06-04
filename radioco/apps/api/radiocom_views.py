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


import json

from radioco.apps.global_settings.models import RadiocomConfiguration
from radioco.apps.global_settings.models import SiteConfiguration
from django.http import HttpResponse


def station_json(request):
    radiocomConfiguration = RadiocomConfiguration.objects.get()
    siteConfiguration = SiteConfiguration.objects.get()

    # tokenizer station_photos by ',' to generate a list
    list_photos = []
    for word in radiocomConfiguration.station_photos.split(','):
        list_photos.append(word.strip())

    json_list = []
    json_entry = {
        'id': radiocomConfiguration.id,
        'station_name': radiocomConfiguration.station_name,
        'icon_url': radiocomConfiguration.big_icon_url,
        'big_icon_url': radiocomConfiguration.big_icon_url,
        'history': radiocomConfiguration.history,
        'latitude': radiocomConfiguration.latitude,
        'longitude': radiocomConfiguration.longitude,
        'news_rss': radiocomConfiguration.news_rss,
        'station_photos': list_photos,
        'stream_url': radiocomConfiguration.stream_url,
        'facebook_url': siteConfiguration.facebook_address,
        'twitter_url': siteConfiguration.twitter_address
    }
    json_list.append(json_entry)

    data = {'data': json_list}

    return HttpResponse(json.dumps(data), content_type='application/json')
