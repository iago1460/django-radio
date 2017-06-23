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

from django.contrib import admin
from django.core.checks import messages
from django.utils.translation import ugettext_lazy as _

from radioco.apps.global_settings.models import CalendarConfiguration
from radioco.apps.schedules.models import Schedule, Calendar

try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']
    actions = ['clone_calendar', 'set_active']

    def set_active(self, request, queryset):
        if queryset.count() == 1:
            calendar = queryset.get()
            calendar.is_active = True
            calendar.save()
            self.message_user(request, _('Calendar marked as active'))
        else:
            self.message_user(request, _('You cannot mark more than 1 schedule as active'), level=messages.ERROR)
    set_active.short_description = _("Set a calendar active")

    def clone_calendar(self, request, queryset):
        for obj in queryset:
            obj_copy = copy.copy(obj)
            obj_copy.id = None
            obj_copy.pk = None
            copy_name = _('Copy of ') + obj.name
            obj_copy.name = copy_name
            obj_copy.is_active = False
            try:
                if Calendar.objects.get(name=copy_name):
                    self.message_user(
                        request,
                        _('A calendar with the name %(obj)s already exists') % {'obj': force_unicode(obj)},
                        level=messages.ERROR
                    )
            except Calendar.DoesNotExist:
                obj_copy.save()
                # Live schedules have to be created first because we are linking to those objects
                schedules = []
                schedules.extend(Schedule.objects.filter(calendar=obj, type='L'))
                schedules.extend(Schedule.objects.filter(calendar=obj).exclude(type='L'))
                for schedule in schedules:
                    schedule_copy = copy.copy(schedule)
                    schedule_copy.id = schedule_copy.pk = None
                    schedule_copy.calendar = obj_copy
                    if schedule_copy.source:
                        source = schedule_copy.source
                        # We should have created the referenced object first
                        # Only live schedules should be in the source field
                        schedule_copy.source = Schedule.objects.get(
                            calendar=obj_copy, start_dt=source.start_dt,
                            type=source.type, programme=source.programme
                        )
                    schedule_copy.save()

    clone_calendar.short_description = _("Make a Clone of the selected calendar")


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('programme', 'type', 'start_dt', 'recurrences')
        }),
        (_('Advanced options'), {
            'classes': ('collapse',),
            'fields': ('effective_start_dt', 'effective_end_dt', 'from_collection', 'source'),
        }),
    )
    readonly_fields = ('effective_start_dt', 'effective_end_dt', 'source', 'from_collection')
    change_list_template = "admin/schedules/calendar.html"

    def changelist_view(self, request, extra_context=None):
        calendar_configuration = CalendarConfiguration.get_global()
        extra_context = extra_context or {}
        extra_context['calendars'] = Calendar.objects.all()
        extra_context['slot_duration'] = unicode(calendar_configuration.slot_duration)
        return super(ScheduleAdmin, self).changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False
