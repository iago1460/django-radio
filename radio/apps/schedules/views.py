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

from dateutil import rrule
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from radio.apps.programmes.models import Programme, Episode
from radio.apps.schedules.models import Schedule
from radio.libs.global_settings.models import CalendarConfiguration


def schedule_list(request):
    calendar_configuration = CalendarConfiguration.objects.get()
    context = {
        'scroll_time': calendar_configuration.scroll_time.strftime('%H:%M:%S'),
        'min_time': calendar_configuration.min_time.strftime('%H:%M:%S'),
        'max_time': calendar_configuration.max_time.strftime('%H:%M:%S'),
        'first_day': calendar_configuration.first_day + 1,
        'language' : request.LANGUAGE_CODE,
        'feed_schedules' : reverse('schedules:feed_schedules'),
    }
    return render(request, 'schedules/schedules_list.html', context)


def feed_schedules(request):
    start = datetime.datetime.strptime(request.GET.get('start'), '%Y-%m-%d')
    end = datetime.datetime.strptime(request.GET.get('end'), '%Y-%m-%d')
    return HttpResponse(json.dumps(__get_events(after=start, before=end, json_mode=True)), content_type='application/json')



background_colours = { "L": "#F9AD81", "B": "#C4DF9B", "S": "#8493CA" }
text_colours = { "L": "black", "B": "black", "S": "black" }

def __get_events(after, before, json_mode=False):
    next_schedules, next_dates = Schedule.between(after=after, before=before)
    schedules = []
    dates = []
    episodes = []
    event_list = []
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
            # broadcast
            elif next_schedules[x].source:
                try:
                    source_date = next_schedules[x].source.date_before(date)
                    if source_date:
                        episode = Episode.objects.get(issue_date=source_date)
                except Episode.DoesNotExist:
                    pass
            episodes.append(episode)

            if episode:
                url = reverse('programmes:episode_detail', args=(schedule.programme.slug, episode.season, episode.number_in_season,))
            else:
                url = reverse('programmes:detail', args=(schedule.programme.slug,))


            event_entry = {'id':schedule.id, 'start':str(date), 'end':str(date + schedule.runtime()),
                'allDay':False, 'title': schedule.programme.name, 'type':schedule.type,
                'textColor':text_colours[schedule.type],
                'backgroundColor':background_colours[schedule.type],
                'url':url}
            event_list.append(event_entry)

    if json_mode:
        return event_list
    else:
        if (schedules):
            dates, schedules, episodes = (list(t) for t in zip(*sorted(zip(dates, schedules, episodes))))
            return zip(schedules, dates, episodes)
        return None


