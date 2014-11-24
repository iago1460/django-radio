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

from radio.apps.schedules import views


urlpatterns = patterns('',
    url(r'^$', views.schedule_list, name='list'),
    url(r'^feed_schedules/', views.feed_schedules, name='feed_schedules'),
)



"""
url(r'^$',
    ListView.as_view(
        queryset=Episode.objects.order_by('-start_date')[:5],
        template_name='schedules/schedules_list.html'),
    name='list'),
"""
