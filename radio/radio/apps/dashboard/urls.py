from django.conf.urls import patterns, url
from radio.apps.dashboard import views

urlpatterns = patterns('',
    url(r'^schedule_editor/$', 'radio.apps.dashboard.views.full_calendar', name="schedule_editor"),
    url(r'^schedule_editor/all_events/', 'radio.apps.dashboard.views.all_events'),
    url(r'^schedule_editor/change_event', 'radio.apps.dashboard.views.change_event'),
    url(r'^schedule_editor/create_schedule', 'radio.apps.dashboard.views.create_schedule'),
    url(r'^schedule_editor/delete_schedule', 'radio.apps.dashboard.views.delete_schedule'),
    url(r'^schedule_editor/programmes', 'radio.apps.dashboard.views.programmes'),

    url(r'^schedule_editor/change_broadcast/(?P<pk>\d+)/$', 'radio.apps.dashboard.views.change_broadcast', name="change_broadcast"),
)
