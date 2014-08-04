import datetime

from django.shortcuts import render, get_object_or_404
from django.templatetags.static import static

from radio.apps.programmes.models import Episode, Programme, Role, Participant, \
    NOT_SPECIFIED


def programme_detail(request, slug):
    programme = get_object_or_404(Programme, slug=slug)
    url_flag = static('radio/images/' + programme.language + '.png')
    context = {'programme': programme, 'unspecified': NOT_SPECIFIED, 'language': programme.get_language_display(),
               'role_list':Role.objects.filter(programme=programme).select_related('person__userprofile', 'programme'),
               'episode_list': Episode.objects.filter(programme=programme).select_related('programme').order_by('-season', '-number_in_season'), 'url_flag':url_flag}
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
