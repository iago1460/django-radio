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
from django.db.models import Q

from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from radioco.apps.programmes.models import Episode, Programme, Role, Participant


def get_filtered_programmes(name, category, isActiveParam):
    isActive = True if isActiveParam == 'on' else False
    today = timezone.now()

    if (isActive):
        filterParam = (Q(end_date=None) | Q(end_date__gte=today)) & Q(name__icontains=name) & Q(category__icontains=category)
    else:
        filterParam = Q(end_date__lt=today) & Q(name__icontains=name) & Q(category__icontains=category)

    filteredPrograms = Programme.objects.order_by('name').filter(filterParam)
    return filteredPrograms


def programme_search(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        category = request.POST.get('category', '')
        isActiveParam = request.POST.get('isActiveParam', 'off')

        context = {
            'programme_list': get_filtered_programmes(name, category, isActiveParam),
            'name': name,
            'category': category,
            'isActiveParam': isActiveParam,
            'categories': Programme.CATEGORY_CHOICES,
        }
    else:
        name = request.GET.get('name', '')
        category = request.GET.get('category', '')
        isActiveParam = request.GET.get('isActiveParam', 'on')

        context = {
            'programme_list': get_filtered_programmes(name, category, isActiveParam),
            'name': name,
            'category': category,
            'isActiveParam': isActiveParam,
            'categories': Programme.CATEGORY_CHOICES,
        }
    return render(request, 'programmes/programme_list.html', context)


def programme_detail(request, slug):
    programme = get_object_or_404(Programme, slug=slug)
    context = {
        'programme': programme, 'language': programme.get_language_display(),
        'role_list': Role.objects.filter(programme=programme).select_related('person__userprofile', 'programme'),
        'episode_list': Episode.objects.filter(
            programme=programme
        ).select_related('programme').order_by('-season', '-number_in_season')
    }
    return render(request, 'programmes/programme_detail.html', context)


def episode_detail(request, slug, season_number, episode_number):
    programme = get_object_or_404(Programme, slug=slug)
    episode = None
    episode_end_date = None
    try:
        episode = Episode.objects.select_related(
            'podcast', 'programme'
        ).get(programme=programme, season=season_number, number_in_season=episode_number)
        # TODO: why am I adding 1 hour?
        episode_end_date = episode.issue_date + episode.runtime + datetime.timedelta(hours=1)
    except:
        pass
    context = {
        'episode': episode, 'programme': programme, 'now': timezone.now(),
        'episode_end_date': episode_end_date,
        'role_list': Participant.objects.filter(episode=episode).select_related('person__userprofile')
    }
    return render(request, 'programmes/episode_detail.html', context)
