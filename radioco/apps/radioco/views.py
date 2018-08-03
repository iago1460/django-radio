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

from django.contrib.auth import (
    logout,
)
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Transmission


def index(request):
    now = timezone.now()

    transmissions_between = Transmission.between(now, now + datetime.timedelta(hours=+16))
    next_transmissions = []

    try:
        live_transmission = next(transmissions_between)
        if live_transmission.start <= now < live_transmission.end:
            percentage = int(round(
                (now - live_transmission.start).total_seconds() /
                (live_transmission.end - live_transmission.start).total_seconds() * 100))
        else:
            next_transmissions.append(live_transmission)
            live_transmission = None
            percentage = None
    except StopIteration:
        live_transmission = None
        percentage = None

    try:
        max_num_of_next_transmissions = 6 - len(next_transmissions)
        for num in range(max_num_of_next_transmissions):
            next_transmissions.append(next(transmissions_between))
    except StopIteration:
        pass

    other_programmes = Programme.objects.filter(Q(end_date__gte=now) | Q(end_date__isnull=True)).order_by('?').all()[:10]
    latest_episodes = Episode.objects.filter(podcast__isnull=False).select_related('programme').order_by('-issue_date')[:5]

    context = {
        'now': now, 'percentage': percentage,
        'transmission': live_transmission, 'next_transmissions': next_transmissions,
        'other_programmes': other_programmes, 'latest_episodes': latest_episodes
    }
    return render(request, 'radioco/index.html', context)


# User Logout View
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
