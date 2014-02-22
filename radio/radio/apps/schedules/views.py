import datetime
import operator

from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone

from radio.apps.schedules.models import Schedule


def schedule_list(request):

    """
    emission_list = chain(Episode.objects.all() , Broadcast.objects.all() , BroadcastSyndication.objects.all())
    emission_list = sorted(emission_list, key=operator.attrgetter('start_date'))
    context = {'episode_list': Episode.objects.order_by('-start_date'),
               'broadcast_list' :Broadcast.objects.order_by('-start_date'),
               'broadcastsyndication_list': BroadcastSyndication.objects.order_by('-start_date')}
    
    
    string = list(schedule.recurrences.occurrences(dtstart=schedule.start_date))
    """
    # schedule = Schedule.objects.get(id=1)



    """
    now = datetime.utcnow().replace(tzinfo=timezone.utc)

    next_date = now + relativedelta(days=+7)
    next_date = datetime.combine(next_date, datetime.min.time())
    next_date = next_date.replace(tzinfo=timezone.utc)

    today = datetime.combine(date.today(), datetime.min.time())
    today = today.replace(tzinfo=timezone.utc)
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    
    
    # today = datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=utc)
    """
    tz = timezone.get_current_timezone()

    today = datetime.datetime.now(tz).date()
    midnight = tz.localize(datetime.datetime.combine(today, datetime.time(0, 0, 0)), is_dst=None)
    today = midnight.astimezone(timezone.utc)

    midnight = tz.localize(datetime.datetime.combine(today + relativedelta(days=+7), datetime.time(23, 59, 59)), is_dst=None)
    next_date = midnight.astimezone(timezone.utc)


    """
    dates = []
    schedules = Schedule.objects.order_by('id')
    programme_name = []
    for schedule in Schedule:
        programme_name.append(schedule.programme.name)
        dates.append(schedule.next_dates(after=today, before=next_date))
        # dates.append(schedule.recurrences.between(after=today, before=next_date))
    """
    next_schedules, next_dates = Schedule.between(after=today, before=next_date)

    schedules = []
    dates = []
    for x in range(len(next_schedules)):
        for y in range(len(next_dates[x])):
            # next_events.append([next_schedules[x], next_dates[x][y]])
            schedules.append(next_schedules[x])
            dates.append(next_dates[x][y])

    dates, schedules = (list(t) for t in zip(*sorted(zip(dates, schedules))))
    next_events = zip(schedules, dates)



    context = {'today':today, 'next_date':next_date, 'next_events':next_events}

    return render(request, 'schedules/schedules_list.html', context)
