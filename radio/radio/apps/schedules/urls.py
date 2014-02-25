from django.conf.urls import patterns, url

from radio.apps.schedules import views


urlpatterns = patterns('',
    url(r'^$', views.schedule_list, name='list'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.schedule_day, name='daily_schedule'),
)



"""
url(r'^$',
    ListView.as_view(
        queryset=Episode.objects.order_by('-start_date')[:5],
        template_name='schedules/schedules_list.html'),
    name='list'),
"""
