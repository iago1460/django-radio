from django.contrib import admin

from radio.apps.schedules.models import Schedule, ScheduleBoard


class ScheduleInline(admin.StackedInline):
    model = Schedule
    extra = 0

class ScheduleBoardAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ['start_date', 'end_date']
    search_fields = ['name']
    inlines = [ScheduleInline]

admin.site.register(ScheduleBoard, ScheduleBoardAdmin)