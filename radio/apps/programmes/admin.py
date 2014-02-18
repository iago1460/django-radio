from django.contrib import admin

from radio.apps.programmes.models import Programme, Episode


class ProgrammeAdmin(admin.ModelAdmin):
    exclude = ('slug',)

admin.site.register(Programme, ProgrammeAdmin)
admin.site.register(Episode)