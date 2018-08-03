import datetime

import pytz
from django.test import TestCase, RequestFactory
from rest_framework import status

from radioco.apps.api import serializers
from radioco.apps.radioco.test_utils import TestDataMixin
from radioco.apps.schedules.models import Transmission


MOCK_CONTEXT = {'request': RequestFactory().get('')}


class TestApi(TestDataMixin):

    def test_api(self):
        response = self.client.get('/api/2/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestSerializers(TestDataMixin, TestCase):
    def test_programme(self):
        serializer = serializers.ProgrammeSerializer(
            self.programme,
            context=MOCK_CONTEXT
        )
        self.assertListEqual(
            list(serializer.data.keys()),
            ['id', 'slug', 'name', 'synopsis', 'runtime', 'photo_url', 'rss_url', 'language', 'category'])

    def test_programme_photo_url(self):
        serializer = serializers.ProgrammeSerializer(
            self.programme,
            context=MOCK_CONTEXT
        )
        self.assertEqual(
            serializer.data['photo_url'], "http://testserver/media/defaults/example/radio_5.jpg"
        )

    def test_episode(self):
        serializer = serializers.EpisodeSerializer(self.episode)
        self.assertListEqual(
            list(serializer.data.keys()),
            ['title', 'programme', 'summary', 'issue_date', 'season', 'number_in_season'])

    def test_episode_programme(self):
        serializer = serializers.EpisodeSerializer(self.episode)
        self.assertEqual(serializer.data['programme'], 'classic-hits')

    def test_schedule(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        schedule_id = self.schedule.id
        calendar_id = self.calendar.id
        self.assertDictEqual(serializer.data, {
            'title': 'Classic hits',
            'source': None,
            'start': '2015-01-01T14:00:00Z',
            'calendar': calendar_id,
            'runtime': datetime.timedelta(minutes=60),
            'type': 'L',
            'id': schedule_id,
            'programme': 'classic-hits'})

    def test_transmission(self):
        serializer = serializers.TransmissionSerializer(
            Transmission(self.schedule, pytz.utc.localize(datetime.datetime(2015, 1, 6, 14, 0, 0))),
            context=MOCK_CONTEXT
        )
        self.assertDictEqual(
            serializer.data,
            {
                'id': self.schedule.id,
                'schedule': self.schedule.id,
                'programme': self.schedule.programme.id,
                'episode': None,
                'source': None,
                'type': 'L',
                'start': '2015-01-06T14:00:00Z',
                'end': '2015-01-06T15:00:00Z',
                'name': 'Classic hits',
                'slug': 'classic-hits',
                'programme_url': 'http://testserver/programmes/classic-hits/',
                'episode_url': None,
            }
        )