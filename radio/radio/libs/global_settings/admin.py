from django.contrib import admin
from solo.admin import SingletonModelAdmin
from radio.libs.global_settings.models import SiteConfiguration, PodcastConfiguration, CalendarConfiguration


class PodcastConfigurationAdmin(SingletonModelAdmin):
    readonly_fields = ['recorder_token']
    pass

admin.site.register(SiteConfiguration, SingletonModelAdmin)
admin.site.register(CalendarConfiguration, SingletonModelAdmin)
admin.site.register(PodcastConfiguration, PodcastConfigurationAdmin)
