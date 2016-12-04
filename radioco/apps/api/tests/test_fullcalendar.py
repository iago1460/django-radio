import datetime

import mock
import pytz
from django.contrib.auth.models import User
from django.test import override_settings
from recurrence import Recurrence
from rest_framework import status
from rest_framework.test import APITestCase

from radioco.apps.schedules.models import ExcludedDates, Schedule
from radioco.apps.radioco.tests.utils import TestDataMixin, SPAIN_TZ


class TestFullCalendarApi(TestDataMixin, APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='iago', email='author@radioco.org', password='1234')

    def _login(self):
        self.client.login(username="iago", password="1234")

    def _get_schedule_data(self):
        return {
            'calendar': self.calendar.id,
            'programme': self.programme.slug,
            'start': "2016-11-17T01:00:00",
            'type': "L"
        }

    def _create_schedule(self):
        new_schedule = Schedule.objects.get(id=self.schedule.id)
        new_schedule.id = new_schedule.pk = None
        new_schedule.start_dt = pytz.utc.localize(datetime.datetime(2015, 1, 1, 18, 30, 0))
        new_schedule.recurrences = Recurrence()
        new_schedule.save()
        return new_schedule

    def _create_schedule_with_daily_recurrence(self):
        new_schedule = Schedule.objects.get(id=self.schedule.id)
        new_schedule.id = new_schedule.pk = None
        new_schedule.start_dt = pytz.utc.localize(datetime.datetime(2015, 1, 1, 18, 30, 0))
        new_schedule.save()
        return new_schedule

    @override_settings(TIME_ZONE='UTC')
    def test_schedules_post(self):
        self._login()
        response = self.client.post('/api/2/schedules', data=self._get_schedule_data())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(
            response.data,
            {
                'start': '2016-11-17T01:00:00Z',
                'title': u'Classic hits', 'source': None, 'calendar': 2,
                'runtime': datetime.timedelta(0, 3600), 'type': 'L', 'id': 7, 'programme': u'classic-hits'
            })

    @override_settings(TIME_ZONE='Europe/Madrid')
    def test_schedules_post_in_tz(self):
        self._login()
        response = self.client.post('/api/2/schedules', data=self._get_schedule_data())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(
            response.data,
            {
                'start': '2016-11-17T01:00:00+01:00',  # Returns the date in the default tz
                'title': u'Classic hits', 'source': None, 'calendar': 2,
                'runtime': datetime.timedelta(0, 3600), 'type': 'L', 'id': 7, 'programme': u'classic-hits'
            })

    @override_settings(TIME_ZONE='UTC')
    def test_move_schedule(self):
        new_schedule = self._create_schedule()
        self._login()
        response = self.client.patch(
            '/api/2/operations/{id}'.format(id=new_schedule.id),
            data={
                'id': new_schedule.id,
                'start': "2015-01-01T18:30:00Z",
                'new_start': "2015-01-01T20:30:00"  # Dt in naive tz
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_schedule.refresh_from_db()
        self.assertEquals(new_schedule.start_dt, pytz.utc.localize(datetime.datetime(2015, 1, 1, 20, 30, 0)))

    @override_settings(TIME_ZONE='Europe/Madrid')
    def test_move_schedule_in_tz(self):
        new_schedule = self._create_schedule()
        self._login()
        response = self.client.patch(
            '/api/2/operations/{id}'.format(id=new_schedule.id),
            data={
                'id': new_schedule.id,
                'start': "2015-01-01T18:30:00Z",
                'new_start': "2015-01-01T20:30:00"  # Dt in naive tz (should be converting using spanish tz)
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_schedule.refresh_from_db()
        self.assertEquals(new_schedule.start_dt, SPAIN_TZ.localize(datetime.datetime(2015, 1, 1, 20, 30, 0)))

    @override_settings(TIME_ZONE='UTC')
    @mock.patch('recurrence.base.localtz', pytz.utc)  # Patching global variable!  : (
    def test_move_schedule_with_schedules(self):
        schedule = self._create_schedule_with_daily_recurrence()
        self._login()
        response = self.client.patch(
            '/api/2/operations/{id}'.format(id=schedule.id),
            data={
                'id': schedule.id,
                'start': "2015-01-01T18:30:00Z",
                'new_start': "2015-01-01T20:30:00"  # Dt in naive tz
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        schedule.refresh_from_db()

        start_dt = pytz.utc.localize(datetime.datetime(2015, 1, 1, 18, 30, 0))
        new_start_dt = pytz.utc.localize(datetime.datetime(2015, 1, 1, 20, 30, 0))

        self.assertEquals(schedule.start_dt, start_dt)  # Original shouldn't change
        self.assertEquals(schedule.recurrences.exdates[0], start_dt)  # But should be excluded
        self.assertIsNotNone(ExcludedDates.objects.get(schedule=schedule, datetime=start_dt))  # Exclude that date

        new_schedule = Schedule.objects.get(programme=schedule.programme, start_dt=new_start_dt)
        self.assertIsNotNone(new_schedule)  # A new schedule should have be created
        self.assertNotEqual(new_schedule.id, schedule.id)
        self.assertFalse(new_schedule.has_recurrences())

        # Second part of the test
        # Move schedule to the previous excluded position
        response = self.client.patch(
            '/api/2/operations/{id}'.format(id=new_schedule.id),
            data={
                'id': new_schedule.id,
                'start': "2015-01-01T20:30:00Z",
                'new_start': "2015-01-01T18:30:00"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        schedule.refresh_from_db()

        # new_schedule has been deleted
        with self.assertRaises(Schedule.DoesNotExist):
            Schedule.objects.get(id=new_schedule.id)

        # the dt is not excluded anymore
        self.assertTrue(len(schedule.recurrences.exdates) == 0)
        with self.assertRaises(ExcludedDates.DoesNotExist):
            ExcludedDates.objects.get(schedule=schedule, datetime=start_dt)

    @override_settings(TIME_ZONE='Europe/Madrid')
    @mock.patch('recurrence.base.localtz', SPAIN_TZ)  # Patching global variable!  : (
    def test_move_schedule_with_schedules_in_tz(self):
        schedule = self._create_schedule_with_daily_recurrence()
        self._login()
        response = self.client.patch(
            '/api/2/operations/{id}'.format(id=schedule.id),
            data={
                'id': schedule.id,
                'start': "2015-01-01T18:30:00Z",
                'new_start': "2015-01-01T20:30:00"  # Dt in naive tz
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        schedule.refresh_from_db()

        start_dt = pytz.utc.localize(datetime.datetime(2015, 1, 1, 18, 30, 0))
        new_start_dt = SPAIN_TZ.localize(datetime.datetime(2015, 1, 1, 20, 30, 0))

        self.assertEquals(schedule.start_dt, start_dt)  # Original shouldn't change
        self.assertEquals(schedule.recurrences.exdates[0], start_dt)  # But should be excluded
        self.assertIsNotNone(ExcludedDates.objects.get(schedule=schedule, datetime=start_dt))  # Exclude that date

        new_schedule = Schedule.objects.get(programme=schedule.programme, start_dt=new_start_dt)
        self.assertIsNotNone(new_schedule)  # A new schedule should have be created
        self.assertNotEqual(new_schedule.id, schedule.id)
        self.assertFalse(new_schedule.has_recurrences())

        # Second part of the test
        # Move schedule to the previous excluded position
        response = self.client.patch(
            '/api/2/operations/{id}'.format(id=new_schedule.id),
            data={
                'id': new_schedule.id,
                'start': "2015-01-01T19:30:00Z",  # same as 2015-01-01T20:30:00 using this tz
                'new_start': "2015-01-01T19:30:00"  # same as 2015-01-01T18:30:00Z
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        schedule.refresh_from_db()

        # new_schedule has been deleted
        with self.assertRaises(Schedule.DoesNotExist):
            Schedule.objects.get(id=new_schedule.id)

        # the dt is not excluded anymore
        self.assertTrue(len(schedule.recurrences.exdates) == 0)
        with self.assertRaises(ExcludedDates.DoesNotExist):
            ExcludedDates.objects.get(schedule=schedule, datetime=start_dt)
