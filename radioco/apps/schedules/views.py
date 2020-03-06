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

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.generic import FormView

from radioco.apps.global_settings.models import CalendarConfiguration
from radioco.apps.radioco.tz_utils import transform_dt_to_default_tz
from radioco.apps.radioco.utils import GetObjectMixin, DeletePermissionMixin
from radioco.apps.schedules.forms import DeleteScheduleForm
from radioco.apps.schedules.models import Schedule


def schedule_list(request):
    calendar_configuration = CalendarConfiguration.get_global()
    context = {
        'min_time': calendar_configuration.min_time.strftime('%H:%M:%S'),
        'max_time': calendar_configuration.max_time.strftime('%H:%M:%S'),
        'slot_duration': str(calendar_configuration.slot_duration),
        'first_day': calendar_configuration.first_day + 1,
        'language': request.LANGUAGE_CODE,
        'transmissions': reverse('api:transmission-list'),
    }
    return render(request, 'schedules/schedules_list.html', context)


class DeleteScheduleView(GetObjectMixin, DeletePermissionMixin, FormView):
    template_name = 'admin/schedules/delete_modal.html'
    form_class = DeleteScheduleForm
    model = Schedule

    schedule_id = None
    transmission_dt = None

    def get(self, request, *args, **kwargs):
        try:
            self.transmission_dt = parse_datetime(request.GET['transmission_dt'])
        except ValueError:
            pass
        if not self.transmission_dt:
            return HttpResponseBadRequest('Invalid request! transmission_dt is invalid.')

        return super(DeleteScheduleView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(DeleteScheduleView, self).get_form_kwargs()
        kwargs.update({
            'has_recurrences': self.object.has_recurrences(),
        })
        return kwargs

    def get_initial(self):
        return {
            'schedule': self.object,
            'transmission_dt': self.transmission_dt,
        }

    def get_context_data(self, **kwargs):
        context = super(DeleteScheduleView, self).get_context_data(**kwargs)
        context['schedule'] = self.object
        context['transmission_dt'] = self.transmission_dt
        return context

    def form_valid(self, form):
        cleaned_data = form.clean()
        schedule = cleaned_data['schedule']
        transmission_dt = cleaned_data['transmission_dt']
        action = cleaned_data.get('action')
        if not schedule.has_recurrences() or action == DeleteScheduleForm.DELETE_ALL:
            schedule.delete()
        elif action == DeleteScheduleForm.DELETE_ONLY_THIS:
            schedule.exclude_date(transmission_dt)
            schedule.save()
        elif action == DeleteScheduleForm.DELETE_THIS_AND_FOLLOWING:
            # until_dt is the end of the previous day
            until_dt = timezone.get_default_timezone().localize(
                datetime.datetime.combine(
                    transform_dt_to_default_tz(transmission_dt).date() - datetime.timedelta(days=1),
                    datetime.time(23, 59, 59)
                )
            )
            # removing rdates rules that are bigger than until_dt
            schedule.recurrences.rdates = [_dt for _dt in schedule.recurrences.rdates if _dt > until_dt]
            # Add a until constraint to all rules (except if they have a date more restrictive)
            for rrule in schedule.recurrences.rrules:
                if not rrule.until or rrule.until > until_dt:
                    rrule.until = until_dt
            schedule.save()

        return HttpResponse(
            json.dumps({'result': 'ok'}),
            content_type='application/json'
        )
