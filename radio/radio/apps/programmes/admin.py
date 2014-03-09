from django.contrib import admin

from radio.apps.programmes.models import Programme, Episode
from radio.apps.schedules.models import Schedule

class ScheduleInline(admin.StackedInline):
    model = Schedule
    extra = 3

class ProgrammeAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('name',)
    search_fields = ['name']
    inlines = [ScheduleInline]

class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'published')
    list_filter = ['published', 'programme']
    search_fields = ['programme__name']

admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(Episode, EpisodeAdmin)
