import datetime

import pytz
from django.test import TestCase

from radioco.apps.api import serializers
from radioco.apps.radioco.tests import TestDataMixin
from radioco.apps.schedules.models import Transmission


class TestSerializers(TestDataMixin, TestCase):
    def test_programme(self):
        serializer = serializers.ProgrammeSerializer(self.programme)
        self.assertListEqual(
            serializer.data.keys(),
            ['id', 'slug', 'name', 'synopsis', 'runtime', 'photo', 'language', 'category'])

    def test_programme_photo_url(self):
        serializer = serializers.ProgrammeSerializer(self.programme)
        self.assertEqual(
            serializer.data['photo'], "/media/defaults/example/radio_5.jpg")

    def test_episode(self):
        serializer = serializers.EpisodeSerializer(self.episode)
        self.assertListEqual(
            serializer.data.keys(),
            ['title', 'programme', 'summary', 'issue_date', 'season', 'number_in_season'])

    def test_episode_programme(self):
        serializer = serializers.EpisodeSerializer(self.episode)
        self.assertEqual(serializer.data['programme'], "classic-hits")

    def test_schedule(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        schedule_id = self.schedule.id
        calendar_id = self.calendar.id
        self.assertDictEqual(serializer.data, {
            'title': u'Classic hits',
            'source': None,
            'start': '2015-01-01T14:00:00Z',
            'calendar': calendar_id,
            'runtime': datetime.timedelta(minutes=60),
            'type': 'L',
            'id': schedule_id,
            'programme': u'classic-hits'})

    def test_transmission(self):
        serializer = serializers.TransmissionSerializer(
            Transmission(self.schedule, pytz.utc.localize(datetime.datetime(2015, 1, 6, 14, 0, 0)))
        )
        schedule_id = self.schedule.id
        self.assertDictEqual(serializer.data, {
            'id': schedule_id,
            'schedule': schedule_id,
            'source': None,
            'type': u'L',
            'start': '2015-01-06T14:00:00Z',
            'end': '2015-01-06T15:00:00Z',
            'name': u'Classic hits',
            'slug': u'classic-hits',
            'url': u'/programmes/classic-hits/'})