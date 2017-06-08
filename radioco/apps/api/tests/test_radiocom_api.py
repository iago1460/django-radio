import datetime

import mock
import pytz
from rest_framework import status
from rest_framework.test import APITestCase

from radioco.apps.programmes.models import Programme
from radioco.apps.radioco.test_utils import TestDataMixin


def mock_now():
    return pytz.utc.localize(datetime.datetime(2015, 1, 6, 14, 30, 0))


class TestProgramme(TestDataMixin, APITestCase):
    def setUp(self):
        self.summer_programme = Programme.objects.create(
            name='Summer Programme',
            synopsis='',
            language='en',
            current_season=1,
            _runtime=60,
            start_date=datetime.date(2015, 6, 1),
            end_date=datetime.date(2015, 8, 31),
        )

    def test_programme_in_list(self):
        response = self.client.get('/api/2/radiocom/programmes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            {
                'id': self.summer_programme.id,
                'name': 'Summer Programme',
                'logo_url': 'http://testserver/media/defaults/default-programme-photo.jpg',
                'rss_url': 'http://testserver/programmes/summer-programme/rss/',
                'description': ''
            },
            response.data)


class TestTransmission(TestDataMixin, APITestCase):
    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmission_now(self):
        response = self.client.get('/api/2/radiocom/transmissions/now')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'start': '2015-01-06T14:00:00Z',
                'end': '2015-01-06T15:00:00Z',
                'name': 'Classic hits',
                'description': "\n        Lorem Ipsum is simply dummy text of the printing and typesetting industry.\n        Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,\n        when an unknown printer took a galley of type and scrambled it to make a type specimen book.\n    ",
                'programme_url': 'http://testserver/programmes/classic-hits/',
                'logo_url': 'http://testserver/media/defaults/example/radio_5.jpg',
                'rss_url': 'http://testserver/programmes/classic-hits/rss/',
                'type': 'L',
            }
        )
