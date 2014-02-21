from django.shortcuts import render, get_object_or_404

from radio.apps.programmes.models import Episode, Programme
from radio.apps.users.models import UserProfile


def programme_detail(request, slug):
    programme = get_object_or_404(Programme, slug=slug)
    context = {'programme': programme,
               'userprofile_list' : UserProfile.objects.filter(user__in=programme.announcers.all()),
               'episode_list': Episode.objects.filter(programme=programme)}
    return render(request, 'programmes/programme_detail.html', context)

def episode_detail(request, slug, id):
    programme = get_object_or_404(Programme, slug=slug)
    episode = get_object_or_404(Episode, id=id, programme=programme)
    context = {'episode': episode, 'programme': programme}
    return render(request, 'programmes/episode_detail.html', context)
