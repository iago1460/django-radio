from django.contrib import admin

from radio.apps.schedules.models import Schedule, Recurrence


class RecurrenceInline(admin.StackedInline):
    model = Recurrence
    # can_delete = False

class ScheduleAdmin(admin.ModelAdmin):
    inlines = (RecurrenceInline,)


admin.site.register(Schedule, ScheduleAdmin)
