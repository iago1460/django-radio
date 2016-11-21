import datetime

import mock
import pytz
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

import serializers
from radioco.apps.programmes.models import Programme
from radioco.apps.radioco.tests import TestDataMixin
from radioco.apps.schedules.models import Transmission


def mock_now():
    return pytz.utc.localize(datetime.datetime(2015, 1, 6, 14, 30, 0))


class TestSerializers(TestDataMixin, TestCase):
    def test_programme(self):
        serializer = serializers.ProgrammeSerializer(self.programme)
        self.assertListEqual(
            serializer.data.keys(),
            ['slug', 'name', 'synopsis', 'runtime', 'photo', 'language', 'category'])

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


class TestAPI(TestDataMixin, APITestCase):
    def setUp(self):
        admin = User.objects.create_user(
            username='klaus', password='topsecret')
        admin.user_permissions.add(
            Permission.objects.get(codename='add_schedule'))

        someone = User.objects.create_user(
            username='someone', password='topsecret')

        self.summer_programme = Programme.objects.create(
            name='Summer Programme',
            synopsis='',
            language='en',
            current_season=1,
            _runtime=60,
            start_date=datetime.date(2015, 6, 1),
            end_date=datetime.date(2015, 8, 31),
        )

    def test_api(self):
        response = self.client.get('/api/2/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_programmes_get_all(self):
        response = self.client.get('/api/2/programmes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_programmes_before(self):
        response = self.client.get(
            '/api/2/programmes',
            {
                'before': datetime.date(2015, 6, 1),
            })
        self.assertIn(u'summer-programme', map(lambda t: t['slug'], response.data))

        response = self.client.get(
            '/api/2/programmes',
            {
                'before': datetime.date(2015, 5, 30),
            })
        self.assertNotIn(u'summer-programme', map(lambda t: t['slug'], response.data))

    def test_programmes_after(self):
        response = self.client.get(
            '/api/2/programmes',
            {
                'after': datetime.date(2015, 8, 31),
            })
        self.assertIn(u'summer-programme', map(lambda t: t['slug'], response.data))

        response = self.client.get(
            '/api/2/programmes',
            {
                'after': datetime.date(2015, 9, 1),
            })
        self.assertNotIn(u'summer-programme', map(lambda t: t['slug'], response.data))

    def test_programmes_between(self):
        response = self.client.get(
            '/api/2/programmes',
            {
                'after': datetime.date(2015, 1, 1),
                'before': datetime.date(2015, 12, 31),
            })
        self.assertIn(u'summer-programme', map(lambda t: t['slug'], response.data))

        response = self.client.get(
            '/api/2/programmes',
            {
                'after': datetime.date(2015, 1, 1),
                'before': datetime.date(2015, 5, 30),
            })
        self.assertNotIn(u'summer-programme', map(lambda t: t['slug'], response.data))

    def test_programmes_post(self):
        response = self.client.post('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_programmes_put(self):
        response = self.client.put('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_programmes_delete(self):
        response = self.client.delete('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_episodes_get_all(self):
        response = self.client.get('/api/2/episodes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_episodes_get_by_programme(self):
        response = self.client.get(
            '/api/2/episodes', {'programme': self.programme.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['programme'], self.programme.slug)

    def test_episodes_post(self):
        response = self.client.post('/api/2/episodes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_episodes_put(self):
        response = self.client.put('/api/2/episodes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_episodes_delete(self):
        response = self.client.delete('/api/2/episodes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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

    def test_schedules_post(self):
        response = self.client.post('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_schedules_post_authenticated_no_permission(self):
        self.client.login(username="someone", password="topsecret")
        response = self.client.post('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#    def test_schedules_post_authenticated(self):
#        self.client.login(username="klaus", password="topsecret")
#        data = {
#            "programme": self.programme.id,
#            "calendar": self.calendar.id,
#            "start": "2015-01-01T07:30:00", "type": "L"}
#        response = self.client.post('/api/2/schedules', data)
#        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmissions_without_parameters(self):
        response = self.client.get(
            '/api/2/transmissions',
            {
                'after': datetime.date(2015, 2, 1),
                'before': datetime.date(2015, 2, 7),
            })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

        response = self.client.get('/api/2/transmissions', {'after': datetime.date(2015, 2, 2), 'before': datetime.date(2015, 2, 1)})
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


@override_settings(TIME_ZONE='Europe/Madrid')
class TestFullCalendarApi(TestDataMixin, APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='iago', email='author@radioco.org', password='1234')

    def _login(self):
        self.client.login(username="iago", password="1234")

    def test_schedules_post(self):
        self._login()
        data = {
            'calendar': self.calendar.id,
            'programme': self.programme.slug,
            'start': "2016-11-17T01:00:00",
            'type': "L"
        }
        response = self.client.post('/api/2/schedules', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(
            response.data,
            {
                'title': u'Classic hits', 'start': '2016-11-17T01:00:00+01:00', 'source': None, 'calendar': 2,
                'runtime': datetime.timedelta(0, 3600), 'type': 'L', 'id': 7, 'programme': u'classic-hits'
            })
