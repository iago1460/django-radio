import datetime
import json

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login, logout, authenticate
)
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from radio.apps.programmes.models import Podcast, Programme, Episode
from radio.apps.schedules.models import Schedule
from radio.apps.schedules.views import __get_events
from radio.libs.global_settings.models import PodcastConfiguration
from radio.libs.home.forms import LoginForm


def index(request):
    now = datetime.datetime.now()
    schedule_now, start_time = Schedule.schedule(now)
    if schedule_now:
        end_time = start_time + schedule_now.runtime()
        percentage = str(round((now - start_time).total_seconds() / schedule_now.runtime().total_seconds() * 100))
    else:
        end_time = now
        percentage = None

    next_events = __get_events(end_time, end_time + relativedelta(hours=+16))

    context = {'schedule_now':schedule_now, 'start_time':start_time, 'percentage':percentage,
               'end_time':end_time, 'now': now, 'next_events':next_events}
    return render(request, 'home/index.html', context)


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
                        return HttpResponseRedirect(reverse('dashboard:index'))
                return render(request, "home/login.html", {'form': form, 'error':True})
            else:
                return render(request, "home/login.html", {'form': form})
        else:
            form = LoginForm()
            return render(request, "home/login.html", {'form': form})
    return HttpResponseRedirect(reverse('dashboard:index'))

# User Logout View
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')





def check_recorder_program(user):
    return user.username == settings.USERNAME_RADIOCO_RECORDER


@api_view(['GET'])
# @authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@authentication_classes((BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
@user_passes_test(check_recorder_program)
def recording_schedules(request):
    if not settings.DEBUG and not request.is_ajax() and not request.GET.get('start'):
        return HttpResponseBadRequest()
    start = datetime.datetime.strptime(request.GET.get('start'), '%Y-%m-%d')
    json_list = []
    schedules, dates = Schedule.between(start, start + relativedelta(hours=+24), live=True)
    for x in range(len(schedules)):
        schedule = schedules[x]
        for y in range(len(dates[x])):
            date = dates[x][y]
            date = date + datetime.timedelta(seconds=PodcastConfiguration.objects.get().start_delay)
            duration = schedule.runtime().seconds - PodcastConfiguration.objects.get().start_delay - PodcastConfiguration.objects.get().end_delay
            # start = date.strftime("%Y-%m-%dT%H:%M:%S"+utc_str)
            json_entry = {'id':schedule.id, 'start':str(date), 'duration':str(duration),
                          'title': schedule.programme.slug}
            json_list.append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')


@api_view(['GET'])
@authentication_classes((BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
@user_passes_test(check_recorder_program)
def submit_recorder(request):
    if not settings.DEBUG and not request.is_ajax():
        return HttpResponseBadRequest()

    schedule_id = int(request.GET.get('schedule_id'))
    date = datetime.datetime.strptime(request.GET.get('date'), '%Y-%m-%d %H-%M-%S')
    file_name = request.GET.get('file_name')
    mime_type = request.GET.get('mime_type')
    length = int(request.GET.get('length'))
    url = PodcastConfiguration.objects.get().url_source + file_name

    try:
        episode = Episode.objects.select_related('programme').get(issue_date=date)
    except Episode.DoesNotExist:
        episode = Episode.create_episode(date, schedule_id)

    duration = episode.programme._runtime

    try:
        # can exist but it must have the same values
        # ignore if exist
        Podcast.objects.get(episode=episode)
    except Podcast.DoesNotExist:
        Podcast.objects.create(episode=episode, url=url, mime_type=mime_type, length=length, duration=duration)
    return HttpResponse()


'''
@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def example_view(request, format=None):
    content = {
        'user': unicode(request.user),  # `django.contrib.auth.User` instance.
        'auth': unicode(request.auth),  # None
    }
    return Response(content)
'''
