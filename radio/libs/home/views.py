import datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone

from radio.apps.schedules.models import Schedule


def index(request):
    now = datetime.datetime.now(timezone.get_current_timezone())
    schedule_now, start_time = Schedule.schedule(now)
    if schedule_now:
        end_time = start_time + schedule_now.runtime()
        percentage = str(round((now - start_time).total_seconds() / schedule_now.runtime().total_seconds() * 100))
    else:
        end_time = now
        percentage = None

    next_schedules, next_dates = Schedule.between(end_time, end_time + relativedelta(hours=+6))
    next_events = []
    for x in range(len(next_schedules)):
        for y in range(len(next_dates[x])):
            next_events.append([next_schedules[x], next_dates[x][y]])

    context = {'active_home': True, 'schedule_now':schedule_now, 'start_time':start_time, 'percentage':percentage,
               'end_time':end_time, 'now': now, 'next_events':next_events}
    return render(request, 'home/index.html', context)
