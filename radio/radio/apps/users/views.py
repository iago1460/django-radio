from django.core.exceptions import ObjectDoesNotExist
from django.views import generic

from radio.apps.users.models import UserProfile


class UsersView(generic.ListView):
    model = UserProfile

    def get_queryset(self):
        return UserProfile.objects.filter(display_personal_page=True)

class UserProfileDetailView(generic.DetailView):
    model = UserProfile

    def get_object(self):
        try:
            return UserProfile.objects.get(slug=self.kwargs['slug'], display_personal_page=True)
        except ObjectDoesNotExist:
            return None
