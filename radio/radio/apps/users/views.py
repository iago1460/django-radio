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


from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views import generic

from radio.apps.programmes.models import  Role, NOT_SPECIFIED
from radio.apps.users.models import UserProfile


class UsersView(generic.ListView):
    model = UserProfile

    def get_queryset(self):
        return UserProfile.objects.filter(display_personal_page=True).select_related('user')


def userprofile_detail(request, slug):
    userprofile = get_object_or_404(UserProfile.objects.select_related('user'), slug=slug, display_personal_page=True)
    context = {'userprofile': userprofile, 'unspecified': NOT_SPECIFIED,
               'role_list':Role.objects.filter(person=userprofile.user).select_related('programme')}
    return render(request, 'users/userprofile_detail.html', context)

"""
class UserProfileDetailView(generic.DetailView):
    model = UserProfile

    def get_object(self):
        try:
            return UserProfile.objects.get(slug=self.kwargs['slug'], display_personal_page=True)
        except ObjectDoesNotExist:
            return None
"""