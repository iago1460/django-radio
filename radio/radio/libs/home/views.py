import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login, logout, authenticate
)
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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
