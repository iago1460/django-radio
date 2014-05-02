import datetime
import json

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login, logout, authenticate
)
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render

from radio.apps.schedules.models import Schedule
from radio.apps.schedules.views import __get_events
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
            # start = date.strftime("%Y-%m-%dT%H:%M:%S"+utc_str)
            json_entry = {'id':schedule.id, 'start':str(date), 'duration':str(schedule.runtime().seconds),
                          'title': schedule.programme.slug}
            json_list.append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')



