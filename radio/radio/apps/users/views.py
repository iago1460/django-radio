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