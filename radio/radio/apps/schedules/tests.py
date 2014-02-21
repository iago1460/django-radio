import datetime
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.utils import timezone

from radio.apps.programmes.models import Programme
from radio.apps.schedules.models import Schedule, Recurrence


class ProgrammeMethodTests(TestCase):

    def setUp(self):
        midnight_programme = Programme.objects.create(name="Programme 00:00 - 12:00", synopsis="This is a description")
        start_date = datetime.datetime(2014, 1, 31, 0, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime.datetime(2014, 1, 31, 12, 0, 0, 0, tzinfo=timezone.utc)
        Schedule.objects.create(programme=midnight_programme, start_date=start_date, end_date=end_date, type='L')

        every_noon_programme = Programme.objects.create(name="Programme 12:00 - 14:00", synopsis="This is a description")
        start_date = datetime.datetime(2014, 1, 31, 12, 0, 0, 0, tzinfo=timezone.utc)
        end_date = datetime.datetime(2014, 1, 31, 14, 0, 0, 0, tzinfo=timezone.utc)
        every_noon_schedule = Schedule.objects.create(programme=every_noon_programme, start_date=start_date, end_date=end_date, type='L')
        Recurrence.objects.create(schedule=every_noon_schedule, repeat=True, monday=True, tuesday=True, wednesday=True, thursday=True,
                                  friday=True, saturday=True, sunday=True)

    def test_runtime(self):
        programme = Programme.objects.get(name="Programme 00:00 - 12:00")
        schedule = Schedule.objects.get(programme=programme)
        self.assertEqual(relativedelta(hours=+12), relativedelta(seconds=schedule.runtime().total_seconds()))

    def test_playing_now(self):
        mock_now = datetime.datetime(2014, 1, 31, 0, 0, 0, 0, tzinfo=timezone.utc)
        schedule, date = Schedule.schedule(mock_now)
        self.assertEqual(schedule.programme, Programme.objects.get(name="Programme 00:00 - 12:00"))

        mock_now = datetime.datetime(2014, 1, 31, 12, 0, 0, 0, tzinfo=timezone.utc)
        schedule, date = Schedule.schedule(mock_now)
        self.assertEqual(schedule.programme, Programme.objects.get(name="Programme 12:00 - 14:00"))

    def test_playing_now_recurrence(self):
        mock_now = datetime.datetime(2014, 2, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
        schedule, date = Schedule.schedule(mock_now)
        self.assertEqual(schedule.programme, Programme.objects.get(name="Programme 12:00 - 14:00"))

        mock_now = datetime.datetime(2014, 2, 1, 13, 59, 59, 0, tzinfo=timezone.utc)
        schedule, date = Schedule.schedule(mock_now)
        self.assertEqual(schedule.programme, Programme.objects.get(name="Programme 12:00 - 14:00"))

        mock_now = datetime.datetime(2014, 3, 1, 14, 0, 0, 0, tzinfo=timezone.utc)
        schedule, date = Schedule.schedule(mock_now)
        self.assertEqual(schedule.programme, Programme.objects.get(name="Programme 12:00 - 14:00"))

    def test_ocurrences(self):
        after_date = datetime.datetime(2014, 1, 31, 0, 0, 0, 0, tzinfo=timezone.utc)
        before_date = datetime.datetime(2014, 1, 31, 12, 0, 0, 0, tzinfo=timezone.utc)
        schedules, dates = Schedule.between(after_date, before_date)
        self.assertEquals(2, len(schedules))
        self.assertTrue(Programme.objects.get(name="Programme 12:00 - 14:00") in [x.programme for x in schedules])
        self.assertTrue(Programme.objects.get(name="Programme 00:00 - 12:00") in [x.programme for x in schedules])

        after_date = datetime.datetime(2014, 2, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
        before_date = datetime.datetime(2014, 2, 1, 12, 0, 0, 0, tzinfo=timezone.utc)
        schedules, dates = Schedule.between(after_date, before_date)
        self.assertEquals(1, len(schedules))
        self.assertTrue(Programme.objects.get(name="Programme 12:00 - 14:00") in [x.programme for x in schedules])




