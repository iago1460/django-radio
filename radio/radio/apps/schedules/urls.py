from django.conf.urls import patterns, url

from radio.apps.schedules import views


urlpatterns = patterns('',
    url(r'^$', views.schedule_list, name='list'),
    
    url(r'^full/$', 'radio.apps.schedules.views.full_calendar'),
    url(r'^full/all_events/', 'radio.apps.schedules.views.all_events'),
    url(r'^full/change_event', 'radio.apps.schedules.views.change_event'),
    url(r'^full/create_schedule', 'radio.apps.schedules.views.create_schedule'),
    url(r'^full/delete_schedule', 'radio.apps.schedules.views.delete_schedule'),
    url(r'^full/programmes', 'radio.apps.schedules.views.programmes'),
    
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', views.schedule_day, name='daily_schedule'),
)



"""
url(r'^$',
    ListView.as_view(
        queryset=Episode.objects.order_by('-start_date')[:5],
        template_name='schedules/schedules_list.html'),
    name='list'),
"""
