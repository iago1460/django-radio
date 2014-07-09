from django.conf.urls import patterns, url
from radio.apps.dashboard import views
urlpatterns = patterns('',
    url(r'^$', 'radio.apps.dashboard.views.index', name="index"),
    url(r'^profile/$', 'radio.apps.dashboard.views.edit_profile', name="edit_profile"),
    url(r'^programmes/$', 'radio.apps.dashboard.views.programme_list', name="programme_list"),
    url(r'^roles/$', 'radio.apps.dashboard.views.role_list', name="role_list"),
    url(r'^programmes/create/$', 'radio.apps.dashboard.views.create_programme', name="create_programme"),
    url(r'^roles/create/$', 'radio.apps.dashboard.views.create_role', name="create_role"),
    url(r'^programmes/(?P<slug>[-\w]+)/$', 'radio.apps.dashboard.views.edit_programme', name="edit_programme"),
    url(r'^roles/(?P<id>\d+)/$', 'radio.apps.dashboard.views.edit_role', name="edit_role"),
    url(r'^own/programmes/$', 'radio.apps.dashboard.views.my_programme_list', name="my_programme_list"),
    url(r'^own/roles/$', 'radio.apps.dashboard.views.my_role_list', name="my_role_list"),
    url(r'^own/programmes/(?P<slug>[-\w]+)/$', 'radio.apps.dashboard.views.edit_my_programme', name="edit_my_programme"),
    url(r'^own/roles/(?P<id>\d+)/$', 'radio.apps.dashboard.views.edit_my_role', name="edit_my_role"),

    url(r'^schedule_editor/$', 'radio.apps.dashboard.views.full_calendar', name="schedule_editor"),
    url(r'^schedule_editor/all_events/', 'radio.apps.dashboard.views.all_events'),
    url(r'^schedule_editor/change_event', 'radio.apps.dashboard.views.change_event'),
    url(r'^schedule_editor/create_schedule', 'radio.apps.dashboard.views.create_schedule'),
    url(r'^schedule_editor/delete_schedule', 'radio.apps.dashboard.views.delete_schedule'),
    url(r'^schedule_editor/programmes', 'radio.apps.dashboard.views.programmes'),

    url(r'^schedule_editor/change_broadcast/(?P<pk>\d+)/$', 'radio.apps.dashboard.views.change_broadcast', name="change_broadcast"),
)
