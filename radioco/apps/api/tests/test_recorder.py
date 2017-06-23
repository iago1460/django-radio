import datetime
import json

import mock
import pytz
import recurrence
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from radioco.apps.global_settings.models import PodcastConfiguration
from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule, Calendar


class PodcastMock():
    @classmethod
    def _get_podcast_config_mock(cls):
        podcast_config = PodcastConfiguration()
        podcast_config.url_source = u''
        podcast_config.start_delay = 20
        podcast_config.end_delay = 10
        podcast_config.next_events = 48
        return podcast_config


@override_settings(TIME_ZONE='Europe/Madrid')
@override_settings(USERNAME_RADIOCO_RECORDER='iago')
class TestProgrammesAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        calendar, created = Calendar.objects.get_or_create(name='Example', is_active=True)

        admin_user = User.objects.create_superuser(username='iago', email='author@radioco.org', password='1234')

        cls.recorder_programme, created = Programme.objects.get_or_create(
            name='Recorder me',
            defaults={
                u'synopsis': u'synopsis',
                u'language': u'en',
                u'photo': u'defaults/example/radio_5.jpg',
                u'current_season': 3,
                u'category': u'News & Politics',
                u'_runtime': 60
            }
        )
        cls.recorder_schedule, created = Schedule.objects.get_or_create(
            programme=cls.recorder_programme,
            type='L',
            calendar=calendar,
            recurrences=recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.DAILY)]),
            start_dt=pytz.utc.localize(datetime.datetime(2015, 1, 1, 14, 0, 0))
        )
        Schedule.objects.get_or_create(
            programme=cls.recorder_programme,
            type='B',
            calendar=calendar,
            recurrences=recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.DAILY)]),
            start_dt=pytz.utc.localize(datetime.datetime(2015, 1, 1, 18, 0, 0))
        )

        Episode.objects.get_or_create(
            title='Episode 2x1',
            programme=cls.recorder_programme,
            summary="summary",
            season=2,
            number_in_season=1,
            issue_date=pytz.utc.localize(datetime.datetime(2015, 1, 1, 14, 0, 0))
        )

    def _login(self):
        self.client.login(username="iago", password="1234")

    @mock.patch('radioco.apps.global_settings.models.PodcastConfiguration.get_global', PodcastMock._get_podcast_config_mock)
    def test_recording_schedules(self):
        self._login()
        self.assertEquals(Episode.objects.count(), 1)
        response = self.client.get(
            u'/api/1/recording_schedules/',
            {
                u'start': u'2015-01-01 00:00:00',
                u'next_hours': 24 + 15
            },
            HTTP_AUTHORIZATION='Token {token}'.format(token=PodcastConfiguration.get_global().recorder_token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Episode.objects.count(), 2)
        self.assertEquals(
            json.loads(response.content),
            [
                {
                    u'id': self.recorder_programme.id, u'issue_date': u'2015-01-01 15-00-00', u'start': u'2015-01-01 15-00-20',
                    u'duration': u'3570', u'genre': u'News & Politics',
                    u'title': u'Episode 2x1', u'programme_name': u'recorder-me', u'author': u'Recorder me',
                    u'album': u'Season 2', u'track': 1
                },
                {
                    u'id': self.recorder_programme.id, u'issue_date': u'2015-01-02 15-00-00', u'start': u'2015-01-02 15-00-20',
                    u'duration': u'3570', u'genre': u'News & Politics',
                    u'title': None, u'programme_name': u'recorder-me', u'author': u'Recorder me',
                    u'album': u'Season 3', u'track': 1
                },
            ]
        )

    @mock.patch('radioco.apps.global_settings.models.PodcastConfiguration.get_global', PodcastMock._get_podcast_config_mock)
    def test_submit_recorder(self):
        self._login()
        podcast_data = {
            u'programme_id': self.recorder_programme.id,
            u'date': u'2015-01-02 15-00-00',
            u'file_name': u'show.mp3',
            u'mime_type': u'audio/mp3',
            u'length': 0,
            u'duration': 666,
        }
        response = self.client.get(
            u'/api/1/submit_recorder/',
            podcast_data,
            HTTP_AUTHORIZATION='Token {token}'.format(token=PodcastConfiguration.get_global().recorder_token)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        episode = Episode.objects.get(
            issue_date=pytz.utc.localize(datetime.datetime(2015, 1, 2, 14, 0, 0)),
            programme=self.recorder_programme
        )
        expected_info = {
            'url': PodcastConfiguration.get_global().url_source + podcast_data['file_name'],
            'duration': self.recorder_programme._runtime,
            'mime_type': u'audio/mp3',
            'length': 0,
            'episode': episode
        }
        self.assertEquals(
            expected_info,
            {_key: getattr(episode.podcast, _key) for _key in expected_info.keys()}
        )
