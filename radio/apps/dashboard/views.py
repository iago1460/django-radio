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

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from radio.apps.dashboard.forms import ScheduleForm
from radio.apps.programmes.models import Programme, Episode
from radio.apps.schedules.models import Schedule, ScheduleBoard
from radio.libs.global_settings.models import CalendarConfiguration



# FullCalendar
def ajax_view(f):
    """Return a valid ajax response"""
    def vista(request, *args, **kwargs):
        if not settings.DEBUG and not request.is_ajax():
            return HttpResponseBadRequest()
        try:
            res = f(request, *args, **kwargs)
            if not res:
                res = None
            error = None
        except ValidationError, e:
            res = None
            error = json.dumps('; '.join(e.messages))
        except Exception, e:
            res = None
            if settings.DEBUG:
                error = (str(e))
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

def schedule_permissions(user):
    return user.has_perm('schedules.add_schedule') and user.has_perm('schedules.change_schedule') and user.has_perm('schedules.delete_schedule')


@login_required
@user_passes_test(schedule_permissions)
def change_broadcast(request, pk):
    schedule = get_object_or_404(Schedule.objects.select_related('schedule_board', 'programme'), pk=pk)
    queryset = Schedule.objects.filter(schedule_board=schedule.schedule_board, programme=schedule.programme, type='L').order_by('day', 'start_hour')
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ScheduleForm(queryset, request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            source = form.cleaned_data['source']
            schedule.source = source
            schedule.save()
            return HttpResponse(render_to_string('dashboard/item_edit_form_success.html', {'schedule': schedule}))
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ScheduleForm(queryset=queryset)
        if schedule.source:
            form = ScheduleForm(queryset=queryset, initial={'source': schedule.source.pk })

    return render(request, 'dashboard/item_edit_form.html', {'form': form, 'schedule':schedule})



@login_required
def full_calendar(request):
    try:
        if schedule_permissions(request.user):
            schedule_boards = ScheduleBoard.objects.all().order_by('start_date')
            if not schedule_boards:
                ScheduleBoard.objects.create(name="Unnamed")
                schedule_boards = ScheduleBoard.objects.all()
            calendar_configuration = CalendarConfiguration.objects.get()
            context = {'scheduleBoards' : schedule_boards,
                       'scroll_time': calendar_configuration.scroll_time.strftime('%H:%M:%S'),
                       'first_day': calendar_configuration.first_day + 1,
                       'language' : request.LANGUAGE_CODE,
                       'current_scheduleBoard':ScheduleBoard.get_current(datetime.datetime.now())}
            return render(request, 'dashboard/fullcalendar.html', context)
        else:
            return render(request, 'dashboard/fullcalendar_error.html', {'error_info':_('Sorry, you don\'t have enough permissions. Please contact your administrator.')})
    except CalendarConfiguration.DoesNotExist:
        return render(request, 'dashboard/fullcalendar_error.html', {'error_info':_('Calendar Configuration not found. Please contact your administrator.')})

@ajax_view
@login_required
@user_passes_test(schedule_permissions)
def change_event(request):
    start = int(request.POST.get('start'))
    start = datetime.datetime.fromtimestamp(start / 1000.0)
    schedule_id = int(request.POST.get('id'))
    schedule = get_object_or_404(Schedule.objects.select_related('programme'), id=schedule_id)

    '''
    # next episodes from now or when the schedule board starts
    now = datetime.datetime.now()
    dt = datetime.datetime.combine(schedule.schedule_board.start_date, datetime.time(0, 0))
    if now > dt:
        dt = now
    next_episodes = Episode.next_episodes(programme=schedule.programme, hour=schedule.start_hour, after=dt)
    '''
    # change schedule
    schedule.start_hour = start.time()
    schedule.day = start.weekday()
    schedule.clean()
    schedule.save()
    Episode.rearrange_episodes(schedule.programme, datetime.datetime.now())
    '''
    # modify date of next episodes
    if len(next_episodes) > 0:
        # get the next emission date
        first_date_start = schedule.date_after(dt)
        time_offset = first_date_start - next_episodes[0].issue_date

        for episode in next_episodes:
            # if the episode belongs to the same board
            if ScheduleBoard.get_current(episode.issue_date) == schedule.schedule_board:
                episode.issue_date = episode.issue_date + time_offset
                episode.save()
    '''


background_colours = { "L": "#F9AD81", "B": "#C4DF9B", "S": "#8493CA" }
text_colours = { "L": "black", "B": "black", "S": "black" }

@ajax_view
@login_required
@user_passes_test(schedule_permissions)
def create_schedule(request):
    start = int(request.POST.get('start'))
    start = datetime.datetime.fromtimestamp(start / 1000.0)
    emission_type = request.POST.get('type')
    programme_id = int(request.POST.get('programmeId'))
    programme = get_object_or_404(Programme, id=programme_id)
    schedule_board_id = int(request.POST.get('scheduleBoardId'))
    scheduleBoard = get_object_or_404(ScheduleBoard, id=schedule_board_id)

    schedule = Schedule(programme=programme, schedule_board=scheduleBoard, day=start.weekday(), start_hour=start.time(), type=emission_type)
    schedule.clean()
    schedule.save()

    Episode.rearrange_episodes(programme, datetime.datetime.now())
    return {'scheduleId': schedule.id, 'backgroundColor':background_colours[schedule.type], 'textColor':text_colours[schedule.type], 'type':schedule.type}

@ajax_view
@login_required
@user_passes_test(schedule_permissions)
def delete_schedule(request):
    schedule_id = int(request.POST.get('scheduleId'))
    schedule = get_object_or_404(Schedule.objects.select_related('programme'), id=schedule_id)
    schedule.delete()
    Episode.rearrange_episodes(schedule.programme, datetime.datetime.now())

@ajax_view
@login_required
@user_passes_test(schedule_permissions)
def programmes(request):
    schedule_board_id = int(request.POST.get('scheduleBoardId'))
    scheduleBoard = get_object_or_404(ScheduleBoard, id=schedule_board_id)
    start_date = datetime.datetime.now().date()
    if scheduleBoard.start_date and scheduleBoard.start_date > start_date:
        start_date = scheduleBoard.start_date
    programmes = Programme.actives(start_date, scheduleBoard.end_date)
    response_data = []
    for programme in programmes:
        response_data.append({'title' : programme.name, 'runtime' : programme._runtime, 'programmeId' : programme.id})
    return response_data


@login_required
@user_passes_test(schedule_permissions)
def all_events(request):
    if not settings.DEBUG and not request.is_ajax():
        return HttpResponseBadRequest()
    schedule_board_id = int(request.GET.get('scheduleBoardId'))
    first_day = int(request.GET.get('firstDay'))
    scheduleBoard = get_object_or_404(ScheduleBoard, id=schedule_board_id)

    schedules = Schedule.objects.filter(schedule_board=scheduleBoard)
    json_list = []
    for schedule in schedules:
        day = schedule.day + 1
        if day < first_day:
            day = day + 7
        date = datetime.datetime.combine(datetime.date(2011, 8, day), schedule.start_hour)
        json_entry = {'id':schedule.id, 'start':str(date), 'end':str(date + schedule.runtime()),
                      'allDay':False, 'title': schedule.programme.name, 'type':schedule.type,
                      'textColor':text_colours[schedule.type],
                      'backgroundColor':background_colours[schedule.type]}
        json_list.append(json_entry)

    return HttpResponse(json.dumps(json_list), content_type='application/json')

