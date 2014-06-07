from django.contrib import admin
from solo.admin import SingletonModelAdmin
from radio.libs.global_settings.models import SiteConfiguration, PodcastConfiguration

admin.site.register(SiteConfiguration, SingletonModelAdmin)
admin.site.register(PodcastConfiguration, SingletonModelAdmin)
