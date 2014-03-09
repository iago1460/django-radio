import datetime
import json

from dateutil import rrule
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from radio.apps.programmes.models import Programme
from radio.apps.schedules.models import Schedule


def ajax_view(f):
    """Return a valid ajax response"""
    def vista(request, *args, **kwargs):

        if not settings.DEBUG and not request.is_ajax():
            return HttpResponseBadRequest()
        try:
            res = f(request, *args, **kwargs)
            error = None
        except ValidationError, e:
            res = None
            error = str(e)
        except Exception, e:
            res = None
            if settings.DEBUG:
                error = str(e)
            else:
                error = str("Internal error")

        return HttpResponse(
            json.dumps({
                'error': error,
                'response': res
            }),
            content_type='application/json; charset=utf8'
        )
    return vista


def full_calendar(request):
    # event_url = 'all_events/'
    return render(request, 'schedules/schedules_fullcalendar.html', {})


@ajax_view
def change_event(request):

    start = int(request.POST.get('start'))
    start = datetime.datetime.fromtimestamp(start / 1000.0)
    id = int(request.POST.get('id'))
    schedule = get_object_or_404(Schedule, id=id)

    now = datetime.datetime.now().date()
    if (schedule.programme.end_date is not None and start.date() >= schedule.programme.end_date) or start.date() < schedule.programme.start_date or start.date() < now:
        raise ValidationError(_('Out of programme date range'))

    schedule.start_hour = start.time()
    schedule.day = start.weekday()
    schedule.clean()
    schedule.save()


background_colours = { "L": "#F9AD81", "B": "#C4DF9B", "S": "#8493CA" }
text_colours = { "L": "black", "B": "black", "S": "black" }


@ajax_view
def create_schedule(request):
    start = int(request.POST.get('start'))
    start = datetime.datetime.fromtimestamp(start / 1000.0)
    id = int(request.POST.get('programmeId'))
    type = request.POST.get('type')
    programme = get_object_or_404(Programme, id=id)

    now = datetime.datetime.now().date()
    if (programme.end_date is not None and start.date() >= programme.end_date) or start.date() < programme.start_date or start.date() < now:
        raise ValidationError(_('Out of programme date range'))

    schedule = Schedule(programme=programme, day=start.weekday(), start_hour=start.time(), type=type)
    schedule.clean()
    schedule.save()
    return {'scheduleId': schedule.id, 'backgroundColor':background_colours[schedule.type], 'textColor':text_colours[schedule.type]}

@ajax_view
def delete_schedule(request):
    id = int(request.POST.get('scheduleId'))
    schedule = get_object_or_404(Schedule, id=id)
    schedule.delete()


@ajax_view
def programmes(request):
    programmes = Programme.actives(datetime.datetime.now().date())
    response_data = []
    for programme in programmes:
        response_data.append({'title' : programme.name, 'runtime' : programme._runtime, 'programmeId' : programme.id})
    return response_data


def all_events(request):
    if not settings.DEBUG and not request.is_ajax():
        return HttpResponseBadRequest()

    start = datetime.datetime.strptime(request.GET.get('start'), '%Y-%m-%d')
    end = datetime.datetime.strptime(request.GET.get('end'), '%Y-%m-%d')

    # Don't show past schedules
    now = datetime.datetime.now().date()
    if start.date() < now:
        start = datetime.datetime.combine(now, datetime.time(0, 0, 0))
    else:
        start = datetime.datetime.combine(start.date(), datetime.time(0, 0, 0))

    end = datetime.datetime.combine(end.date(), datetime.time(23, 59, 59))

    json_list = []
    if end >= start:
        schedules, dates = Schedule.between(start, end)
        for x in range(len(schedules)):
            schedule = schedules[x]
            for y in range(len(dates[x])):
                date = dates[x][y]
                # start = date.strftime("%Y-%m-%dT%H:%M:%S"+utc_str)
                json_entry = {'id':schedule.id, 'start':str(date), 'end':str(date + schedule.runtime()),
                              'allDay':False, 'title': schedule.programme.name, 'textColor':text_colours[schedule.type] , 'backgroundColor':background_colours[schedule.type]}
                json_list.append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')


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
    today = datetime.datetime.now().date()
    today = datetime.datetime.combine(today, datetime.time(0, 0, 0))
    end_date = today + relativedelta(days=+7)
    return rrule.rrule(rrule.WEEKLY, byweekday=[], dtstart=today, until=end_date)


