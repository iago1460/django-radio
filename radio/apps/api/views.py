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


import serializers
import json
import re

from apps.programmes.models import Programme
from rest_framework import viewsets
from django.http import HttpResponse



class ProgrammeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Programme.objects.all()
    serializer_class = serializers.ProgrammeSerializer


def programmes_json(request):

    url = re.sub(request.get_full_path(), '', request.build_absolute_uri())

    programme_list = Programme.objects.order_by('end_date', 'name')
    json_list = []

    for programme in programme_list:

        json_entry = {
            'id': programme.id,
            'genre': programme.get_category_display(),
            'title': programme.name,
            'description': programme.synopsis,
            'logo_url': url + programme.photo.url,
            'rss_url': url + "/programmes/" + programme.slug + '/rss/'
        }
        json_list.append(json_entry)

    data = {'data': json_list}

    return HttpResponse(json.dumps(data), content_type='application/json')