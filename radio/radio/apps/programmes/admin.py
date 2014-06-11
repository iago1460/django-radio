from django.contrib import admin

from radio.apps.programmes.models import Programme, Podcast, Episode, Role, Participant
from radio.apps.schedules.models import Schedule

class ScheduleInline(admin.StackedInline):
    model = Schedule
    extra = 0


class RoleInline(admin.StackedInline):
    model = Role
    extra = 0

class ProgrammeAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ['start_date', 'end_date']
    search_fields = ['name']
    inlines = [RoleInline, ScheduleInline]

class PodcastInline(admin.StackedInline):
    model = Podcast

class ParticipantInline(admin.StackedInline):
    model = Participant
    extra = 0

class EpisodeAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('__unicode__', 'issue_date')
    list_filter = ['issue_date', 'programme']
    search_fields = ['programme__name']
    inlines = (ParticipantInline, PodcastInline,)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('role', 'programme', 'person')
    list_filter = ['role', 'programme', 'person']


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('role', 'episode', 'person')
    list_filter = ['role', 'episode', 'person']


admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(Episode, EpisodeAdmin)
# admin.site.register(Role, RoleAdmin)
