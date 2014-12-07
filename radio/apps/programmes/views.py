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


import datetime

from django.shortcuts import render, get_object_or_404

from radio.apps.programmes.models import Episode, Programme, Role, Participant, \
    NOT_SPECIFIED


def programme_detail(request, slug):
    programme = get_object_or_404(Programme, slug=slug)
    context = {'programme': programme, 'unspecified': NOT_SPECIFIED, 'language': programme.get_language_display(),
               'role_list':Role.objects.filter(programme=programme).select_related('person__userprofile', 'programme'),
               'episode_list': Episode.objects.filter(programme=programme).select_related('programme').order_by('-season', '-number_in_season')}
    return render(request, 'programmes/programme_detail.html', context)

def episode_detail(request, slug, season_number, episode_number):
    programme = get_object_or_404(Programme, slug=slug)
    episode = None
    episode_end_date = None
    try:
        episode = Episode.objects.select_related('podcast', 'programme').get(programme=programme, season=season_number, number_in_season=episode_number)
        episode_end_date = episode.issue_date + episode.runtime + datetime.timedelta(hours=1)
    except:
        pass
    context = {'episode': episode, 'programme': programme, 'now':datetime.datetime.now(), 'episode_end_date':episode_end_date,
               'role_list':Participant.objects.filter(episode=episode).select_related('person__userprofile'), 'unspecified': NOT_SPECIFIED }
    return render(request, 'programmes/episode_detail.html', context)
