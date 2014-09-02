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
from django.views.generic import DetailView, ListView

from radio.apps.programmes import views
from radio.apps.programmes.feeds import RssProgrammeFeed
from radio.apps.programmes.models import Programme

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=Programme.objects.order_by('name'),
            template_name='programmes/programme_list.html'),
        name='list'),
    url(r'^(?P<slug>[-\w]+)/$', views.programme_detail, name='detail'),
    url(r'^(?P<slug>[-\w]+)/(?P<season_number>\d+)x(?P<episode_number>\d+)/$', views.episode_detail, name='episode_detail'),

    url(r'^(?P<slug>[-\w]+)/rss/$', RssProgrammeFeed(), name='rss')
)
