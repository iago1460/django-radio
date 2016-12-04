import datetime

import mock
import pytz
from rest_framework import status
from rest_framework.test import APITestCase

from radioco.apps.radioco.tests import TestDataMixin


def mock_now():
    return pytz.utc.localize(datetime.datetime(2015, 1, 6, 14, 30, 0))


class TestSchedulesAPI(TestDataMixin, APITestCase):
    def test_schedules_get_all(self):
        response = self.client.get('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schedules_get_by_programme(self):
        response = self.client.get(
            '/api/2/schedules', {'programme': self.programme.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], self.programme.name)

    def test_schedules_get_by_nonexisting_programme(self):
        response = self.client.get(
            '/api/2/schedules', {'programme': 'foo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_schedules_get_by_calendar(self):
        response = self.client.get(
            '/api/2/schedules', {'calendar': self.calendar.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(
            response.data[0]['calendar'], self.calendar.id)

    def test_schedules_get_by_nonexisting_calendar(self):
        response = self.client.get(
            '/api/2/schedules', {'calendar': 'foobar'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_schedules_get_by_type(self):
        response = self.client.get('/api/2/schedules?type=L')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(
            response.data[0]['calendar'], self.calendar.id)

    def test_schedules_get_by_nonexiting_type(self):
        response = self.client.get('/api/2/schedules?type=B')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TestTransmissionAPI(TestDataMixin, APITestCase):
    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmissions_between(self):
        response = self.client.get(
            '/api/2/transmissions',
            {
                'after': datetime.date(2015, 2, 1),
                'before': datetime.date(2015, 2, 7),
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0],
            {
                u'end': u'2015-02-01T09:00:00Z', u'name': u'Morning News', u'schedule': 1,
                u'url': u'/programmes/morning-news/', u'id': 1, u'start': u'2015-02-01T08:00:00Z', u'source': None,
                u'type': u'L', u'slug': u'morning-news'
            }
        )

    def test_transmissions_between_requesting_tz(self):
        response = self.client.get(
            '/api/2/transmissions',
            {
                'after': datetime.date(2015, 2, 1),
                'before': datetime.date(2015, 2, 7),
                'timezone': 'Europe/Madrid'
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data[0],
            {
                u'end': u'2015-02-01T10:00:00+01:00', u'name': u'Morning News', u'schedule': 1,
                u'url': u'/programmes/morning-news/', u'id': 1, u'start': u'2015-02-01T09:00:00+01:00', u'source': None,
                u'type': u'L', u'slug': u'morning-news'
            }
        )

    def test_incorrect_transmission_queries(self):
        response = self.client.get('/api/2/transmissions')
        self.assertEqual(response.data['after'], [u'This field is required.'])
        self.assertEqual(response.data['before'], [u'This field is required.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get('/api/2/transmissions', {'after': datetime.date(2015, 2, 1)})
        self.assertEqual(response.data['before'], [u'This field is required.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get('/api/2/transmissions', {'before': datetime.date(2015, 2, 1)})
        self.assertEqual(response.data['after'], [u'This field is required.'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(
            '/api/2/transmissions',
            {'after': datetime.date(2015, 2, 2), 'before': datetime.date(2015, 2, 1)}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmission_list_filter_non_active_calendar(self):
        calendar_id = self.another_calendar.id
        response = self.client.get(
            '/api/2/transmissions',
            {
                'calendar': calendar_id,
                'after': datetime.date(2015, 1, 1), 'before': datetime.date(2015, 2, 1)
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            map(lambda t: (t['slug'], t['start']), response.data),
            [(u'classic-hits', '2015-01-06T16:30:00Z')])

    def test_transmission_same_day(self):
        response = self.client.get(
            '/api/2/transmissions',
            {
                'after': datetime.date(2015, 2, 1),
                'before': datetime.date(2015, 2, 1),
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(response.data, key=lambda t: t['start'])[0]['start'],
            '2015-02-01T08:00:00Z')

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmission_before(self):
        response = self.client.get(
            '/api/2/transmissions',
            {'after': datetime.date(2015, 1, 14), 'before': datetime.date(2015, 1, 14)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            sorted(response.data, key=lambda t: t['start'])[-1]['start'],
            '2015-01-14T14:00:00Z')

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmission_now(self):
        response = self.client.get('/api/2/transmissions/now')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            map(lambda t: (t['slug'], t['start']), response.data),
            [(u'classic-hits', '2015-01-06T14:00:00Z')])

    def test_transmissions_filter_calendar_nonexistend(self):
        response = self.client.get(
            '/api/2/transmissions', {'calendar': 9999})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestRestrictedMethodsScheduleAPI(TestDataMixin, APITestCase):

    def test_schedules_post(self):
        response = self.client.post('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_schedules_put(self):
        response = self.client.put('/api/2/schedules')
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN)

    def test_schedules_delete(self):
        response = self.client.delete('/api/2/schedules')
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN)

    def test_transmissions_post(self):
        response = self.client.post('/api/2/transmissions')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_transmissions_put(self):
        response = self.client.put('/api/2/transmissions')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_transmissions_delete(self):
        response = self.client.delete('/api/2/transmissions')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
