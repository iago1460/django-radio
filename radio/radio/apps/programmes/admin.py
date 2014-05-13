from django.contrib import admin

from radio.apps.programmes.models import Programme, Episode, Role, Participant
from radio.apps.schedules.models import Schedule

class ScheduleInline(admin.StackedInline):
    model = Schedule
    extra = 3

class ProgrammeAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ['start_date', 'end_date']
    search_fields = ['name']
    inlines = [ScheduleInline]

class EpisodeAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('__unicode__', 'issue_date')
    list_filter = ['issue_date', 'programme']
    search_fields = ['programme__name']

class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'programme', 'person')
    list_filter = ['role', 'programme', 'person']


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('role', 'episode', 'person')
    list_filter = ['role', 'episode', 'person']


admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Participant, ParticipantAdmin)
