from django.contrib import admin

from radio.apps.programmes.models import Programme, Episode


class ProgrammeAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    list_display = ('name',)
    search_fields = ['name']

class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'published')
    list_filter = ['published', 'programme']
    search_fields = ['programme__name']

admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(Episode, EpisodeAdmin)
