from django.contrib import admin

from radio.apps.schedules.models import Schedule, Recurrence


class RecurrenceInline(admin.StackedInline):
    model = Recurrence
    # can_delete = False

class ScheduleAdmin(admin.ModelAdmin):
    inlines = (RecurrenceInline,)
    list_display = ('__unicode__', 'start_date', 'end_date')
    list_filter = ['start_date', 'programme']
    search_fields = ['programme__name']


admin.site.register(Schedule, ScheduleAdmin)
