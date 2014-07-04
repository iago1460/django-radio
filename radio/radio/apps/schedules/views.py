import datetime
import json

from dateutil import rrule
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from radio.apps.programmes.models import Programme, Episode
from radio.apps.schedules.models import Schedule




def schedule_day(request, year, month, day):
    after = datetime.datetime(int(year), int(month), int(day), 0, 0, 0)
    before = datetime.datetime.combine(after, datetime.time(23, 59, 59))
    context = {'today':after, 'next_events':__get_events(after, before), 'day_list':__get_nextDays(), 'now':datetime.datetime.now()}
    return render(request, 'schedules/schedules_list.html', context)

def schedule_list(request):
    today = datetime.datetime.now().date()
    return schedule_day(request, today.year, today.month, today.day)


def __get_events(after, before):
    next_schedules, next_dates = Schedule.between(after=after, before=before)
    schedules = []
    dates = []
    episodes = []
    for x in range(len(next_schedules)):
        for y in range(len(next_dates[x])):
            # next_events.append([next_schedules[x], next_dates[x][y]])

            schedule = next_schedules[x]
            schedules.append(schedule)
            date = next_dates[x][y]
            dates.append(date)

            episode = None
            # if schedule == live
            if next_schedules[x].type == 'L':
                try:
                    episode = Episode.objects.get(issue_date=date)
                except Episode.DoesNotExist:
                    pass
            # TODO: schedule == broadcast
            episodes.append(episode)



    if (schedules):
        dates, schedules, episodes = (list(t) for t in zip(*sorted(zip(dates, schedules, episodes))))
        return zip(schedules, dates, episodes)
    return None

def __get_nextDays():
    today = datetime.datetime.now().date()
    today = datetime.datetime.combine(today, datetime.time(0, 0, 0))
    end_date = today + relativedelta(days=+7)
    return rrule.rrule(rrule.WEEKLY, byweekday=[], dtstart=today, until=end_date)


