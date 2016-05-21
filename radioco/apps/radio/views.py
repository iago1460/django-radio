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

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import (
    login, logout, authenticate
)
from django import utils
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from radioco.apps.global_settings.models import PodcastConfiguration
from radioco.apps.programmes.models import Podcast, Programme, Episode
from radioco.apps.radio.forms import LoginForm
from radioco.apps.schedules.models import Schedule, Transmission


def index(request):
    now = utils.timezone.now()
    transmissions = Transmission.at(now)
    try:
        transmission = transmissions.next()
        end_time = transmission.end
        percentage = round(
            (now - transmission.start).total_seconds() /
            (transmission.end - transmission.start).total_seconds() * 100)

    except StopIteration:
        transmission = None
        end_time = now
        percentage = None

    next_transmissions = Transmission.between(
        end_time, end_time + datetime.timedelta(hours=+16))

    other_programmes = Programme.objects.order_by('?').all()[:10]
    latest_episodes = Episode.objects.filter(podcast__isnull=False).order_by('-issue_date')[:5]

    context = {
        'now': now, 'percentage': percentage,
        'transmission': transmission, 'next_transmissions': next_transmissions,
        'other_programmes': other_programmes, 'latest_episodes': latest_episodes
    }
    return render(request, 'radio/index.html', context)


# WARNING: function not in use
def user_login(request):
    if request.user.is_anonymous():
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                # This authenticates the user
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        # This logs him in
                        login(request, user)
                        return HttpResponseRedirect(reverse('admin:index'))
                return render(request, "radio/login.html", {'form': form, 'error': True})
            else:
                return render(request, "radio/login.html", {'form': form})
        else:
            form = LoginForm()
            return render(request, "radio/login.html", {'form': form})
    return HttpResponseRedirect(reverse('admin:index'))


# User Logout View
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def check_recorder_program(user):
    return user.username == settings.USERNAME_RADIOCO_RECORDER


@api_view(['GET'])
@authentication_classes((BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
@user_passes_test(check_recorder_program)
def recording_schedules(request):
    start = datetime.datetime.strptime(request.GET.get('start'), '%Y-%m-%d %H:%M:%S')
    next_hours = request.GET.get("next_hours", None)
    if not next_hours:
        next_hours = PodcastConfiguration.objects.get().next_events
    else:
        next_hours = int(next_hours)
    json_list = []

    next_schedules, next_dates = Schedule.between(start, start + relativedelta(hours=next_hours), live=True)
    schedules = []
    dates = []
    for x in range(len(next_schedules)):
        for y in range(len(next_dates[x])):
            schedules.append(next_schedules[x])
            dates.append(next_dates[x][y])

    # sort
    if schedules:
        dates, schedules = (list(t) for t in zip(*sorted(zip(dates, schedules))))

    for x in range(len(schedules)):
        schedule = schedules[x]
        date = dates[x]

        # Create the episode to retrieve season and episode number
        try:
            episode = Episode.objects.select_related('programme').get(issue_date=date, programme=schedule.programme)
        except Episode.DoesNotExist:
            episode = Episode.create_episode(date, schedule.programme)

        start_date = date + datetime.timedelta(seconds=PodcastConfiguration.objects.get().start_delay)
        duration = schedule.runtime().seconds - PodcastConfiguration.objects.get().start_delay - PodcastConfiguration.objects.get().end_delay
        # start = date.strftime("%Y-%m-%dT%H:%M:%S"+utc_str)
        json_entry = {
            'id': schedule.programme.id, 'issue_date': date.strftime('%Y-%m-%d %H-%M-%S'),
            'start': start_date.strftime('%Y-%m-%d %H-%M-%S'), 'duration': str(duration),
            'genre': schedule.programme.get_category_display(), 'programme_name': schedule.programme.slug,
            'title': episode.title, 'author': schedule.programme.name, 'album': _('Season') + ' ' + str(episode.season),
            'track': episode.number_in_season
        }
        json_list.append(json_entry)

    return HttpResponse(json.dumps(json_list), content_type='application/json')


@api_view(['GET'])
@authentication_classes((BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
@user_passes_test(check_recorder_program)
def submit_recorder(request):
    programme_id = int(request.GET.get('programme_id'))
    programme = get_object_or_404(Programme, id=programme_id)
    date = datetime.datetime.strptime(request.GET.get('date'), '%Y-%m-%d %H-%M-%S')
    file_name = request.GET.get('file_name')
    mime_type = request.GET.get('mime_type')
    length = int(request.GET.get('length'))
    url = PodcastConfiguration.objects.get().url_source + file_name

    try:
        episode = Episode.objects.select_related('programme').get(issue_date=date, programme=programme)
    except Episode.DoesNotExist:
        episode = Episode.create_episode(date, programme)

    duration = episode.programme._runtime
    try:
        # can exist but it should have same values
        # overwrite if episode exists
        podcast = Podcast.objects.get(episode=episode)
        podcast.url = url
        podcast.mime_type = mime_type
        podcast.length = length
        podcast.duration = duration
        podcast.save()
    except Podcast.DoesNotExist:
        Podcast.objects.create(episode=episode, url=url, mime_type=mime_type, length=length, duration=duration)
    return HttpResponse()
