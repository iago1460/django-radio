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


import datetime
import json
import django_filters
import pytz

from django import utils
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.timezone import override
from rest_framework import filters, viewsets
from rest_framework import serializers
from rest_framework.decorators import list_route
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from radioco.apps.api.serializers import DateTimeFieldTz
from radioco.apps.api.views import TransmissionForm
from radioco.apps.global_settings.models import RadiocomConfiguration
from radioco.apps.global_settings.models import SiteConfiguration
from radioco.apps.programmes.models import Programme
from radioco.apps.schedules.models import Schedule
from radioco.apps.schedules.models import Transmission_Radiocom


# Json programmes
def programmes_json(request):
    # url = re.sub(request.get_full_path(), '', request.build_absolute_uri())

    programme_list = Programme.objects.order_by('end_date', 'name')
    json_list = []

    for programme in programme_list:
        json_entry = {
            'id': programme.id,
            'genre': programme.get_category_display(),
            'name': programme.name,
            'slug': programme.slug,
            'description': programme.synopsis,
            'logo_url': programme.photo.url,
            'rss_url': reverse('programmes:detail', args=[programme.slug]) + 'rss/'
        }
        json_list.append(json_entry)

    data = {'data': json_list}

    return HttpResponse(json.dumps(data), content_type='application/json')


# Json station
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


# Filter by calendar
class ScheduleFilter(filters.FilterSet):
    class Meta:
        model = Schedule
        fields = ('programme', 'calendar', 'type')

    programme = django_filters.CharFilter(name="programme__slug")


# Json Transmission
class Transmission_RadiocomSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='schedule.id')
    slug = serializers.SlugField(max_length=100)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    start = DateTimeFieldTz()
    end = DateTimeFieldTz()
    schedule = serializers.IntegerField(source='schedule.id')
    programme_url = serializers.URLField()
    episode_url = serializers.URLField()
    logo_url = serializers.ImageField()
    rss_url = serializers.URLField()
    type = serializers.CharField(max_length=1, source='schedule.type')
    source = serializers.IntegerField(source='schedule.source.id')


# Search Transmissions
class TransmissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all()
    # Transmissions are always order by date
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ScheduleFilter
    serializer_class = Transmission_RadiocomSerializer

    def list(self, request, *args, **kwargs):
        data = TransmissionForm(request.query_params)
        if not data.is_valid():
            raise DRFValidationError(data.errors)
        requested_timezone = data.cleaned_data.get('timezone')

        after = data.cleaned_data['after']
        before = data.cleaned_data['before']

        tz = requested_timezone or pytz.utc
        after_date = tz.localize(datetime.datetime.combine(after, datetime.time()))
        before_date = tz.localize(datetime.datetime.combine(before, datetime.time(23, 59, 59)))

        # Apply filters to the queryset
        schedules = self.filter_queryset(self.get_queryset())
        # Filter by active calendar if that filter was not provided
        if not data.cleaned_data.get('calendar'):
            schedules = schedules.filter(calendar__is_active=True)

        # It indicates the class of the model to be serialized
        transmissions = Transmission_Radiocom.between(
            after_date,
            before_date,
            schedules=schedules
        )

        serializer = self.serializer_class(transmissions, many=True)

        with override(timezone=tz):
            return Response(serializer.data)

    @list_route()
    def now(self, request):
        tz = None or pytz.utc  # TODO check for a tz?
        now = utils.timezone.now()
        transmissions = Transmission_Radiocom.at(now)
        serializer = self.serializer_class(
            transmissions, many=True)
        with override(timezone=tz):
            return Response(serializer.data)
