from django.shortcuts import render, get_object_or_404
from django.templatetags.static import static

from radio.apps.programmes.models import Episode, Programme, Role, Participant


def programme_detail(request, slug):
    programme = get_object_or_404(Programme, slug=slug)
    url_flag = static('radio/images/' + programme.language + '.png')
    context = {'programme': programme,
               'role_list':Role.objects.filter(programme=programme).select_related('person__userprofile'),
               'episode_list': Episode.objects.filter(programme=programme).order_by('issue_date')[:5], 'url_flag':url_flag}
    return render(request, 'programmes/programme_detail.html', context)

def episode_detail(request, slug, season_number, episode_number):
    programme = get_object_or_404(Programme, slug=slug)
    episode = None
    try:
        episode = Episode.objects.get(programme=programme, season=season_number, number_in_season=episode_number)
    except:
        pass
    context = {'episode': episode, 'programme': programme,
               'role_list':Participant.objects.filter(episode=episode).select_related('person__userprofile'), }
    return render(request, 'programmes/episode_detail.html', context)
