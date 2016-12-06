import datetime
import json

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext as _
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from radioco.apps.global_settings.models import PodcastConfiguration
from radioco.apps.programmes.models import Episode, Programme, Podcast
from radioco.apps.radioco.tz_utils import transform_dt_to_default_tz
from radioco.apps.schedules.models import Schedule, Transmission


def check_recorder_program(user):
    return user.username == settings.USERNAME_RADIOCO_RECORDER


@api_view(['GET'])
@authentication_classes((BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
@user_passes_test(check_recorder_program)
def recording_schedules(request):
    podcast_config = PodcastConfiguration.objects.get()
    default_tz = timezone.get_default_timezone()
    start = default_tz.localize(datetime.datetime.strptime(request.GET.get('start'), '%Y-%m-%d %H:%M:%S'))
    next_hours = int(request.GET.get("next_hours") or podcast_config.next_events)

    json_list = []
    next_transmissions = Transmission.between(
        start, start + datetime.timedelta(hours=next_hours),
        schedules=Schedule.objects.filter(calendar__is_active=True, type='L')
    )

    for transmission in next_transmissions:
        try:
            episode = Episode.objects.get(issue_date=transmission.start, programme=transmission.programme)
        except Episode.DoesNotExist:
            episode = Episode.objects.create_episode(transmission.start, transmission.programme)

        issue_date = transform_dt_to_default_tz(transmission.start)
        start_dt = issue_date + datetime.timedelta(seconds=podcast_config.start_delay)
        duration = transmission.schedule.runtime.seconds - podcast_config.start_delay - podcast_config.end_delay
        json_entry = {
            'id': transmission.programme.id, 'issue_date': issue_date.strftime('%Y-%m-%d %H-%M-%S'),
            'start': start_dt.strftime('%Y-%m-%d %H-%M-%S'), 'duration': str(duration),
            'genre': transmission.programme.get_category_display(), 'programme_name': transmission.programme.slug,
            'title': episode.title, 'author': transmission.programme.name, 'album': _('Season') + ' ' + str(episode.season),
            'track': episode.number_in_season
        }
        json_list.append(json_entry)

    return HttpResponse(json.dumps(json_list), content_type='application/json')


@api_view(['GET'])
@authentication_classes((BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
@user_passes_test(check_recorder_program)
def submit_recorder(request):
    podcast_config = PodcastConfiguration.objects.get()
    default_tz = timezone.get_default_timezone()

    programme_id = int(request.GET.get('programme_id'))
    programme = get_object_or_404(Programme, id=programme_id)
    date = default_tz.localize(datetime.datetime.strptime(request.GET.get('date'), '%Y-%m-%d %H-%M-%S'))
    file_name = request.GET.get('file_name')
    mime_type = request.GET.get('mime_type')
    length = int(request.GET.get('length'))
    url = podcast_config.url_source + file_name

    try:
        episode = Episode.objects.select_related('programme').get(issue_date=date, programme=programme)
    except Episode.DoesNotExist:
        # This shouldn't happen, we are creating episodes when the recorder ask for programmes to record
        episode = Episode.objects.create_episode(date, programme)

    duration = episode.programme._runtime
    try:
        # Podcast can exist but it should have the same values
        # DECISION: overwrite values
        podcast = Podcast.objects.get(episode=episode)
        podcast.url = url
        podcast.mime_type = mime_type
        podcast.length = length
        podcast.duration = duration
        podcast.save()
    except Podcast.DoesNotExist:
        Podcast.objects.create(episode=episode, url=url, mime_type=mime_type, length=length, duration=duration)
    return HttpResponse()
