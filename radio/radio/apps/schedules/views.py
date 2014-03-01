import datetime

from dateutil import rrule
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone

from radio.apps.schedules.models import Schedule


def schedule_day(request, year, month, day):
    tz = timezone.get_current_timezone()
    after = datetime.datetime(int(year), int(month), int(day), 0, 0, 0, tzinfo=timezone.utc)
    
    midnight = tz.localize(datetime.datetime.combine(after, datetime.time(23, 59, 59)), is_dst=None)
    before = midnight.astimezone(timezone.utc)
    
    next_events = __get_events(after, before)

    context = {'today':after, 'next_events':next_events, 'day_list':__get_nextDays(), 'now':datetime.datetime.now(tz)}

    return render(request, 'schedules/schedules_list.html', context)
    
def schedule_list(request):
    today = datetime.datetime.now().date()
    return schedule_day(request, today.year, today.month, today.day)


def __get_events(after, before):
    next_schedules, next_dates = Schedule.between(after=after, before=before)

    schedules = []
    dates = []
    for x in range(len(next_schedules)):
        for y in range(len(next_dates[x])):
            # next_events.append([next_schedules[x], next_dates[x][y]])
            schedules.append(next_schedules[x])
            dates.append(next_dates[x][y])
    if (schedules):
        dates, schedules = (list(t) for t in zip(*sorted(zip(dates, schedules))))
        return zip(schedules, dates)
    return None
    
def __get_nextDays():
    tz = timezone.get_current_timezone()

    today = datetime.datetime.now(tz).date()
    midnight = tz.localize(datetime.datetime.combine(today, datetime.time(0, 0, 0)), is_dst=None)
    today = midnight.astimezone(timezone.utc)

    midnight = tz.localize(datetime.datetime.combine(today + relativedelta(days=+7), datetime.time(23, 59, 59)), is_dst=None)
    end_date = midnight.astimezone(timezone.utc)
    
    today = timezone.get_current_timezone().normalize(today)
    end_date = timezone.get_current_timezone().normalize(end_date)
    return rrule.rrule(rrule.WEEKLY, byweekday=[], dtstart=today, until=end_date)
    
    