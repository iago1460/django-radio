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


import copy

from django.conf.urls import url, patterns
from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.utils.translation import ugettext_lazy as _

from radio.apps.schedules.models import Schedule, ScheduleBoard


'''
class ScheduleInline(admin.StackedInline):
    model = Schedule
    extra = 0

    def get_queryset(self, request):
        return super(ScheduleInline, self).get_queryset(request).select_related('programme')
'''
class ScheduleBoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ['start_date', 'end_date']
    search_fields = ['name']
    ordering = ['start_date']
    inlines = []
    actions = ['copy_ScheduleBoard']

    def copy_ScheduleBoard(self, request, queryset):
        for obj in queryset:
            obj_copy = copy.copy(obj)
            obj_copy.id = None
            obj_copy.pk = None
            copy_name = _('Copy of ') + obj.name
            obj_copy.name = copy_name
            obj_copy.start_date = None
            obj_copy.end_date = None
            try:
                if ScheduleBoard.objects.get(name=copy_name):
                    pass
                    # Don't work
                    # self.message_user(request, _('There is already a calendar with this name \"%s\"') % copy_name, level=messages.ERROR)
            except ScheduleBoard.DoesNotExist:
                obj_copy.save()
                # Live Schedules lives must be created first
                schedules = []
                schedules.extend(Schedule.objects.filter(schedule_board=obj, type='L'))
                schedules.extend(Schedule.objects.filter(schedule_board=obj).exclude(type='L'))
                for schedule in schedules:
                    schedule_copy = copy.copy(schedule)
                    schedule_copy.id = None
                    schedule_copy.pk = None
                    schedule_copy.schedule_board = obj_copy
                    if schedule_copy.source:
                        source = schedule_copy.source
                        source_copy = Schedule.objects.get(schedule_board=obj_copy, day=source.day, start_hour=source.start_hour, type=source.type, programme=source.programme)
                        schedule_copy.source = source_copy
                    schedule_copy.save()

    copy_ScheduleBoard.short_description = _("Make a Copy of calendar")




admin.site.register(ScheduleBoard, ScheduleBoardAdmin)


try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode




class FullcalendarAdmin(admin.ModelAdmin):
    # change_form_template = 'schedules/fullcalendar.html'

    def schedule_detail(self, request):
        return HttpResponseRedirect(reverse("dashboard:schedule_editor"))
        # return redirect('dashboard:schedule_editor')
        '''
        model = self.model
        opts = model._meta

        app_label = opts.app_label
        # create tempate page and extend admin/base.html
        config_detail_view_template = 'schedules/fullcalendar.html'
        context = { 'data' : Schedule.objects.get(id=2),
                    'event_url':'all_events/', 'scheduleBoards' : ScheduleBoard.objects.all().order_by('start_date'),
                    'scroll_time': CalendarConfiguration.objects.get().scroll_time.strftime('%H:%M:%S'),
                    'first_day': CalendarConfiguration.objects.get().first_day + 1,
                    'language' : request.LANGUAGE_CODE,
                    'current_scheduleBoard':ScheduleBoard.get_current(datetime.datetime.now())}
        return render_to_response(config_detail_view_template , context, context_instance=RequestContext(request))
        '''

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super(FullcalendarAdmin, self).get_urls()
        url_name_prefix = '%(app_name)s_%(model_name)s' % {
            'app_name': self.model._meta.app_label,
            'model_name': self.model._meta.model_name,
        }
        custom_urls = patterns('',
            url(r'^$',
                self.admin_site.admin_view(self.schedule_detail),
                {},
                # self.admin_site.admin_view(self.change_view),
                # {'object_id': '2'},
                name='%s_change' % url_name_prefix),
        )
        # By inserting the custom URLs first, we overwrite the standard URLs.
        return custom_urls + urls

    def response_change(self, request, obj):
        msg = _('%(obj)s was changed successfully.') % {'obj': force_unicode(obj)}
        if '_continue' in request.POST:
            return HttpResponseRedirect(request.path)
        else:
            return HttpResponseRedirect("../../")
    '''
    def change_view(self, request, object_id, extra_context=None):
        return super(FullcalendarAdmin, self).change_view(
            request,
            object_id,
            extra_context=extra_context,
        )
    '''

admin.site.register(Schedule, FullcalendarAdmin)
