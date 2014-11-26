# Radioco - Broadcasting Radio Recording Scheduling system.
# Copyright (C) 2014  Iago Veloso Abalo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
