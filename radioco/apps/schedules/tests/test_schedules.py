# Radioco - Broadcasting Radio Recording Scheduling system.
# Copyright (C) 2014  Iago Veloso Abalo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import datetime
from functools import partial

import mock
import pytz
from django.test import override_settings
from django.utils import unittest
from pytz import utc
import recurrence
from django.core.exceptions import ValidationError, FieldError
from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete
from django.forms import modelform_factory
from django.test import TestCase
from django.utils import timezone

from radioco.apps.schedules.utils import rearrange_episodes, next_dates
from radioco.apps.radioco.tests import TestDataMixin
from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule, Transmission
from radioco.apps.schedules.models import Calendar, CalendarManager


def mock_now(dt=pytz.utc.localize(datetime.datetime(2014, 1, 1, 13, 30, 0))):
    return dt


class ScheduleValidationTests(TestDataMixin, TestCase):
    def test_fields(self):
        schedule = Schedule()
        with self.assertRaisesMessage(
            ValidationError,
            "{'calendar': [u'This field cannot be null.'], "
            "'start_dt': [u'This field cannot be null.'], "
            "'type': [u'This field cannot be blank.'], "
            "'programme': [u'This field cannot be null.']}"):
            schedule.clean_fields()


@override_settings(TIME_ZONE='UTC')
class ScheduleModelTests(TestDataMixin, TestCase):
    def setUp(self):
        self.calendar = Calendar.objects.create(name='Calendar', is_active=True)

        self.recurrences = recurrence.Recurrence(
            rrules=[recurrence.Rule(recurrence.WEEKLY, until=utc.localize(datetime.datetime(2014, 1, 31)))])

        programme = Programme.objects.filter(name="Classic hits").get()
        programme.name = "Classic hits 2"
        programme.id = programme.pk = None
        programme.save()
        self.programme = programme

        self.schedule = Schedule.objects.create(
            programme=self.programme,
            type='L',
            recurrences=self.recurrences,
            start_dt=utc.localize(datetime.datetime(2014, 1, 6, 14, 0, 0)),
            calendar=self.calendar)

        self.episode = Episode.objects.create(
            title='Episode 1',
            programme=programme,
            summary='',
            season=1,
            number_in_season=1,
        )
        rearrange_episodes(self.programme, pytz.utc.localize(datetime.datetime(1970, 1, 1)))
        self.episode.refresh_from_db()

    def test_runtime(self):
        self.assertEqual(datetime.timedelta(hours=+1), self.schedule.runtime)

    def test_runtime_not_set(self):
        schedule = Schedule(programme=Programme())
        with self.assertRaises(FieldError):
            schedule.runtime

    def test_start(self):
        self.assertEqual(
            self.schedule.start_dt, utc.localize(datetime.datetime(2014, 1, 6, 14, 0, 0)))

    def test_start_lt_calendar(self):
        self.programme.start_date = datetime.date(2014, 1, 14)
        self.programme.save()
        self.schedule.refresh_from_db()
        self.assertEqual(
            self.schedule.effective_start_dt, utc.localize(datetime.datetime(2014, 1, 20, 14, 0, 0)))

    def test_end_gt_calendar(self):
        self.programme.end_date = datetime.date(2014, 1, 14)
        self.programme.save()
        self.schedule.refresh_from_db()
        self.assertEqual(
            self.schedule.effective_end_dt,
            utc.localize(datetime.datetime(2014, 1, 13, 15, 0, 0))  # last date including runtime duration
        )

    def test_recurrence_rules(self):
        self.assertListEqual(
            self.schedule.recurrences.rrules, self.recurrences.rrules)

    def test_date_before(self):
        self.assertEqual(
            self.schedule.date_before(utc.localize(datetime.datetime(2014, 1, 14))),
            utc.localize(datetime.datetime(2014, 1, 13, 14, 0)))

    def test_date_after(self):
        self.assertEqual(
            self.schedule.date_after(utc.localize(datetime.datetime(2014, 1, 14))),
            utc.localize(datetime.datetime(2014, 1, 20, 14, 0)))

    def test_date_after_exclude(self):
        self.assertEqual(
            self.schedule.date_after(utc.localize(datetime.datetime(2014, 1, 6, 14, 0, 0, 1))),
            utc.localize(datetime.datetime(2014, 1, 13, 14, 0)))

    def test_dates_between(self):
        self.assertItemsEqual(
            self.schedule.dates_between(
                utc.localize(datetime.datetime(2014, 1, 1)), utc.localize(datetime.datetime(2014, 1, 14))),
            [utc.localize(datetime.datetime(2014, 1, 6, 14, 0)),
             utc.localize(datetime.datetime(2014, 1, 13, 14, 0))])

    def test_dates_between_later_start_by_programme(self):
        self.programme.start_date = datetime.date(2014, 1, 7)
        self.programme.save()
        self.schedule.refresh_from_db()
        self.assertItemsEqual(
            self.schedule.dates_between(
                utc.localize(datetime.datetime(2014, 1, 1)), utc.localize(datetime.datetime(2014, 1, 14))),
            [utc.localize(datetime.datetime(2014, 1, 13, 14, 0))])

    def test_dates_between_earlier_end_by_programme(self):
        self.programme.end_date = datetime.date(2014, 1, 7)
        self.programme.save()
        self.schedule.refresh_from_db()
        self.assertItemsEqual(
            self.schedule.dates_between(
                utc.localize(datetime.datetime(2014, 1, 1)), utc.localize(datetime.datetime(2014, 1, 14))),
            [utc.localize(datetime.datetime(2014, 1, 6, 14, 0))])

    def test_dates_between_complex_ruleset(self):
        programme = Programme.objects.create(name="Programme 14:00 - 15:00", current_season=1, runtime=60)
        schedule = Schedule.objects.create(
            programme=programme,
            calendar=self.calendar,
            start_dt=utc.localize(datetime.datetime(2014, 1, 2, 14, 0, 0)),
            recurrences=recurrence.Recurrence(
                rrules=[recurrence.Rule(recurrence.DAILY, interval=2)],
                exrules=[recurrence.Rule(
                    recurrence.WEEKLY, byday=[recurrence.MO, recurrence.TU])]))

        self.assertItemsEqual(
            schedule.dates_between(
                utc.localize(datetime.datetime(2014, 1, 1)), utc.localize(datetime.datetime(2014, 1, 9))),
            [utc.localize(datetime.datetime(2014, 1, 2, 14, 0)),
             utc.localize(datetime.datetime(2014, 1, 4, 14, 0)),
             utc.localize(datetime.datetime(2014, 1, 8, 14, 0))])

    def test_unicode(self):
        self.assertEqual(unicode(self.schedule), 'Monday - 14:00:00')

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_save_rearrange_episodes(self):
        self.assertEqual(self.episode.issue_date, utc.localize(datetime.datetime(2014, 1, 6, 14, 0, 0)))
        self.episode.issue_date = None
        self.episode.save()
        self.schedule.save()
        self.episode.refresh_from_db()
        self.assertEqual(self.episode.issue_date, utc.localize(datetime.datetime(2014, 1, 6, 14, 0, 0)))


@override_settings(TIME_ZONE='UTC')
class ScheduleBetweenTests(TestDataMixin, TestCase):
    def setUp(self):
        self.recurrences = recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.DAILY)])

        self.schedule = Schedule.objects.create(
            programme=self.programme,
            type='L',
            recurrences=self.recurrences,
            start_dt=utc.localize(datetime.datetime(2014, 1, 1, 23, 30, 0)),
            calendar=self.calendar)

    def test_dates_between_includes_started_episode(self):
        self.assertItemsEqual(
            self.schedule.dates_between(
                utc.localize(datetime.datetime(2014, 1, 2, 0, 0, 0)),
                utc.localize(datetime.datetime(2014, 1, 3, 23, 59, 59))
            ),
            [
                utc.localize(datetime.datetime(2014, 1, 1, 23, 30, 0)), # Not finished yet
                utc.localize(datetime.datetime(2014, 1, 2, 23, 30, 0)),
                utc.localize(datetime.datetime(2014, 1, 3, 23, 30, 0)),
            ]
        )

    def test_between_includes_started_episode(self):
        between = Transmission.between(
            utc.localize(datetime.datetime(2014, 1, 2, 0, 0, 0)),
            utc.localize(datetime.datetime(2014, 1, 3, 23, 59, 59))
        )
        self.assertListEqual(
            map(lambda t: (t.slug, t.start), list(between)),
            [(u'classic-hits',  utc.localize(datetime.datetime(2014, 1, 1, 23, 30, 0))),
             (u'classic-hits',  utc.localize(datetime.datetime(2014, 1, 2, 23, 30, 0))),
             (u'classic-hits',  utc.localize(datetime.datetime(2014, 1, 3, 23, 30, 0)))])


#class ScheduleClassModelTests(TestCase):
#    def setUp(self):
#        daily = recurrence.Recurrence(
#            rrules=[recurrence.Rule(recurrence.DAILY)])
#
#        weekly = recurrence.Recurrence(
#            rrules=[recurrence.Rule(recurrence.WEEKLY)])
#
#        self.calendar = Calendar.objects.create(
#            name='Board', start_date=datetime.datetime(2014, 1, 1, 0, 0, 0, 0))
#
#        midnight_programme = Programme.objects.create(
#            name="Programme 00:00 - 09:00",
#            synopsis="This is a description",
#            current_season=1, runtime=540)
#
#        Schedule.objects.create(
#            programme=midnight_programme,
#            day=WE,
#            start_hour=datetime.time(0, 0, 0),
#            type='L',
#            calendar=self.calendar)
#
#        programme = Programme.objects.create(
#            name="Programme 09:00 - 10:00",
#            synopsis="This is a description",
#            current_season=1, runtime=60)
#
#        for day in (MO, WE, FR):
#            Schedule.objects.create(
#                programme=programme, day=day, type='L',
#                calendar=self.calendar)
#
#        programme = Programme.objects.create(
#            name="Programme 10:00 - 12:00",
#            synopsis="This is a description",
#            current_season=1, runtime=120)
#
#        for day in (MO, WE, FR):
#            Schedule.objects.create(
#                programme=programme,
#                day=day, type='B',
#                start_hour=datetime.time(10, 0, 0),
#                calendar=self.calendar)
#
#        for schedule in Schedule.objects.all():
#            schedule.clean()
#
#    def test_day_schedule(self):
#        schedules, dates = Schedule.between(datetime.datetime(2014, 1, 6), datetime.datetime(2014, 1, 7))
#        self.assertEqual(3, len(schedules))
#
#        schedule_1 = Schedule.objects.get(programme=Programme.objects.get(name="Programme 00:00 - 09:00"), day=WE)
#        schedule_2 = Schedule.objects.get(programme=Programme.objects.get(name="Programme 09:00 - 10:00"), day=MO)
#        schedule_3 = Schedule.objects.get(programme=Programme.objects.get(name="Programme 10:00 - 12:00"), day=MO)
#        self.assertTrue(schedule_1 in schedules)
#        self.assertTrue(schedule_2 in schedules)
#        self.assertTrue(schedule_3 in schedules)
#
#    def test_between(self):
#        schedules, dates = Schedule.between(
#            datetime.datetime(2014, 1, 1), datetime.datetime(2014, 1, 2))
#        self.assertEqual(dates, [
#            [datetime.datetime(2014, 1, 1, 0, 0),
#             datetime.datetime(2014, 1, 2, 0, 0)],
#            [datetime.datetime(2014, 1, 1, 9, 0)],
#            [datetime.datetime(2014, 1, 1, 10, 0)]])
#
#    def test_between_live(self):
#        schedules, dates = Schedule.between(
#            datetime.datetime(2014, 1, 1),
#            datetime.datetime(2014, 1, 2),
#            live=True)
#        self.assertEqual(dates, [
#            [datetime.datetime(2014, 1, 1, 0, 0),
#             datetime.datetime(2014, 1, 2, 0, 0)],
#            [datetime.datetime(2014, 1, 1, 9, 0)]])
#
#    def test_between_calendar(self):
#        schedules, dates = Schedule.between(
#            datetime.datetime(2014, 1, 1),
#            datetime.datetime(2014, 1, 2),
#            calendar=self.calendar)
#        self.assertEqual(dates, [
#            [datetime.datetime(2014, 1, 1, 0, 0),
#             datetime.datetime(2014, 1, 2, 0, 0)],
#            [datetime.datetime(2014, 1, 1, 9, 0)],
#            [datetime.datetime(2014, 1, 1, 10, 0)]])
#
#    def test_between_emtpy_calendar(self):
#        schedules, dates = Schedule.between(
#            datetime.datetime(2014, 1, 1),
#            datetime.datetime(2014, 1, 2),
#            calendar=Calendar())
#        self.assertFalse(dates)
#
#    def test_between_exclude(self):
#        programme = Programme.objects.get(name="Programme 09:00 - 10:00")
#        schedule = Schedule.objects.get(
#            programme=programme,
#            day=WE,
#            start_hour=datetime.time(9, 0))
#        schedules, dates = Schedule.between(
#            datetime.datetime(2014, 1, 1),
#            datetime.datetime(2014, 1, 2),
#            exclude=schedule)
#        self.assertEqual(dates, [
#            [datetime.datetime(2014, 1, 1, 0, 0),
#             datetime.datetime(2014, 1, 2, 0, 0)],
#            [datetime.datetime(2014, 1, 1, 10, 0)]])
#
#    def test_schedule(self):
#        schedule, date = Schedule.schedule(datetime.datetime(2014, 1, 2, 4, 0))
#        self.assertEqual(schedule.programme.name, 'Programme 00:00 - 09:00')
#        self.assertEqual(schedule.start_hour, datetime.time(0, 0))
#        self.assertEqual(date, datetime.datetime(2014, 1, 2, 0, 0))
#
#    def test_schedule_silence(self):
#        schedule, date = Schedule.schedule(
#            datetime.datetime(2014, 1, 1, 14, 0))
#        self.assertIsNone(schedule)
#        self.assertIsNone(date)
#
#    def test_schedule_exclude(self):
#        programme = Programme.objects.get(name="Programme 00:00 - 09:00")
#        schedule = Schedule.objects.get(
#            programme=programme,
#            day=WE,
#            start_hour=datetime.time(0, 0))
#        schedule, date = Schedule.schedule(
#            datetime.datetime(2014, 1, 2, 4, 0),
#            exclude=schedule)
#        self.assertIsNone(schedule)
#        self.assertIsNone(date)
#
#    def test_get_next_date(self):
#        programme = Programme.objects.get(name="Programme 00:00 - 09:00")
#        schedule, date = Schedule.get_next_date(
#            programme, datetime.datetime(2014, 1, 2, 4, 0))
#        self.assertEqual(date, datetime.datetime(2014, 1, 3, 0, 0))
#
#    def test_get_next_date_no_schedule(self):
#        programme = Programme.objects.get(name="Programme 00:00 - 09:00")
#        schedule, date = Schedule.get_next_date(
#            programme, datetime.datetime(2014, 2, 1, 4, 0))
#        self.assertIsNone(date)
#
#    def test_get_next_date_no_current_board(self):
#        programme = Programme.objects.get(name="Programme 00:00 - 09:00")
#        schedule, date = Schedule.get_next_date(
#            programme, datetime.datetime(2013, 1, 2, 4, 0))
#        self.assertEqual(date, datetime.datetime(2014, 1, 1, 0, 0))


class CalendarManagerTests(TestDataMixin, TestCase):
    def setUp(self):
        self.manager = CalendarManager()

    def test_current(self):
        self.assertIsInstance(self.manager.current(), Calendar)

    def test_current_no_date(self):
        self.assertIsInstance(self.manager.current(), Calendar)


class CalendarValidationTests(TestCase):
    def setUp(self):
        self.CalendarForm = modelform_factory(Calendar, fields=("name",))

    def test_only_one_calendar_active(self):
        self.assertEquals(len(Calendar.objects.filter(is_active=True)), 1)

        new_active_calendar = Calendar.objects.create(name="test", is_active=True)

        self.assertEquals(Calendar.objects.get(is_active=True), new_active_calendar)

# XXX there is something fishy with form validation, check!
#    def test_name_required(self):
#        board = Calendar(slug="foo")
#        form = self.CalendarForm(instance=board)
#        with self.assertRaisesMessage(
#                ValidationError, "{'name':[u'This field cannot be blank.']}"):
#            form.clean()
#
#    def test_slug_required(self):
#        board = Calendar(name="foo")
#        with self.assertRaisesMessage(
#                ValidationError, "{'slug':[u'This field cannot be blank.']}"):
#            board.full_clean()


@override_settings(TIME_ZONE='UTC')
class CalendarModelTests(TestDataMixin, TestCase):

    def test_str(self):
        self.assertEqual(str(self.calendar), "Example")

    # @mock.patch('django.utils.timezone.now', mock_now)
    # @mock.patch('radioco.apps.schedules.utils.rearrange_episodes')
    # def test_delete(self, rearrange_episodes):
    #     def calls():
    #         for programme in Programme.objects.all():
    #             yield mock.call(programme, mock_now())
    # 
    #     post_delete.send(Calendar, instance=self.calendar)
    #     rearrange_episodes.assert_has_calls(calls(), any_order=True)


@override_settings(TIME_ZONE='UTC')
class TransmissionModelTests(TestDataMixin, TestCase):
    def setUp(self):
        self.transmission = Transmission(
            self.schedule, utc.localize(datetime.datetime(2015, 1, 6, 14, 0, 0)))

    def test_name(self):
        self.assertEqual(
            self.transmission.name, self.schedule.programme.name)

    def test_start(self):
        self.assertEqual(
            self.transmission.start, utc.localize(datetime.datetime(2015, 1, 6, 14, 0, 0)))

    def test_end(self):
        self.assertEqual(
            self.transmission.end, utc.localize(datetime.datetime(2015, 1, 6, 15, 0, 0)))

    def test_slug(self):
        self.assertEqual(
            self.transmission.slug, self.schedule.programme.slug)

    def test_url(self):
        self.assertEqual(
            self.transmission.url,
            reverse('programmes:detail', args=[self.schedule.programme.slug]))

    def test_at(self):
        now = Transmission.at(utc.localize(datetime.datetime(2015, 1, 6, 14, 30, 0)))
        self.assertListEqual(
            map(lambda t: (t.slug, t.start), list(now)),
            [(u'classic-hits', utc.localize(datetime.datetime(2015, 1, 6, 14, 0)))])

    def test_between(self):
        between = Transmission.between(
            utc.localize(datetime.datetime(2015, 1, 6, 11, 0, 0)),
            utc.localize(datetime.datetime(2015, 1, 6, 17, 0, 0)))
        self.assertListEqual(
            map(lambda t: (t.slug, t.start), list(between)),
            [(u'the-best-wine', utc.localize(datetime.datetime(2015, 1, 6, 11, 0))),
             (u'local-gossips', utc.localize(datetime.datetime(2015, 1, 6, 12, 0))),
             (u'classic-hits', utc.localize(datetime.datetime(2015, 1, 6, 14, 0)))])

    def test_between_by_queryset(self):
        between = Transmission.between(
            utc.localize(datetime.datetime(2015, 1, 6, 12, 0, 0)),
            utc.localize(datetime.datetime(2015, 1, 6, 17, 0, 0)),
            schedules=Schedule.objects.filter(
                calendar=self.another_calendar).all())
        self.assertListEqual(
            map(lambda t: (t.slug, t.start), list(between)),
            [(u'classic-hits', utc.localize(datetime.datetime(2015, 1, 6, 16, 30, 0)))])


@override_settings(TIME_ZONE='UTC')
class ScheduleUtilsTests(TestDataMixin, TestCase):

    def setUp(self):
        self.manager = CalendarManager()
        programme = Programme.objects.filter(name="Classic hits").get()
        programme.name = "Classic hits - ScheduleUtilsTests"
        programme.id = programme.pk = None
        programme.save()
        self.programme = programme

        Schedule.objects.get_or_create(
            programme=programme,
            type='L',
            calendar=self.calendar,
            recurrences=recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.DAILY)]),
            start_dt=pytz.utc.localize(datetime.datetime(2015, 1, 1, 14, 0, 0)))

        for number in range(1, 11):
            Episode.objects.create(
                title='Episode %s' % number,
                programme=programme,
                summary='',
                season=1,
                number_in_season=number,
            )
        rearrange_episodes(programme, pytz.utc.localize(datetime.datetime(1970, 1, 1)))

    def test_available_dates_after(self):
        Schedule.objects.create(
            programme=self.programme,
            calendar=self.calendar,
            type="L",
            start_dt=utc.localize(datetime.datetime(2015, 1, 6, 16, 0, 0)),
            recurrences=recurrence.Recurrence(
                rrules=[recurrence.Rule(recurrence.WEEKLY)]))

        dates = next_dates(self.programme, utc.localize(datetime.datetime(2015, 1, 5)))
        self.assertEqual(dates.next(), utc.localize(datetime.datetime(2015, 1, 5, 14, 0)))
        self.assertEqual(dates.next(), utc.localize(datetime.datetime(2015, 1, 6, 14, 0)))
        self.assertEqual(dates.next(), utc.localize(datetime.datetime(2015, 1, 6, 16, 0)))

    def test_available_dates_none(self):
        dates = next_dates(Programme(), timezone.now())
        with self.assertRaises(StopIteration):
            dates.next()

    def test_rearrange_episodes(self):
        rearrange_episodes(self.programme, utc.localize(datetime.datetime(2015, 1, 1)))
        self.assertListEqual(
            map(lambda e: e.issue_date, self.programme.episode_set.all().order_by('issue_date')[:5]),
            [
                utc.localize(datetime.datetime(2015, 1, 1, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 2, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 3, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 4, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 5, 14, 0))
            ]
        )

    @mock.patch('django.utils.timezone.now', partial(mock_now, dt=utc.localize(datetime.datetime(2015, 1, 1))))
    def test_rearrange_episodes_new_schedule(self):
        Schedule.objects.create(
            programme=self.programme,
            calendar=Calendar.objects.create(),
            type="L",
            start_dt=utc.localize(datetime.datetime(2015, 1, 3, 16, 0, 0)),
            recurrences=recurrence.Recurrence(
                rrules=[recurrence.Rule(
                    recurrence.WEEKLY, until=utc.localize(datetime.datetime(2015, 1, 31, 16, 0, 0)))]))
        # save should call rearrange
        # rearrange_episodes(self.programme, pytz.utc.localize(datetime.datetime(2015, 1, 1)))
        self.assertListEqual(
            map(lambda e: e.issue_date, self.programme.episode_set.all().order_by('issue_date')[:5]),
            [
                utc.localize(datetime.datetime(2015, 1, 1, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 2, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 3, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 3, 16, 0)),
                utc.localize(datetime.datetime(2015, 1, 4, 14, 0))
            ]
        )

    @mock.patch('django.utils.timezone.now', partial(mock_now, dt=utc.localize(datetime.datetime(2015, 1, 3, 16, 0, 1))))
    def test_rearrange_only_non_emited_episodes(self):
        Schedule.objects.create(
            programme=self.programme,
            calendar=Calendar.objects.create(),
            type="L",
            start_dt=utc.localize(datetime.datetime(2015, 1, 3, 16, 0, 0)),
            recurrences=recurrence.Recurrence(
                rrules=[recurrence.Rule(
                    recurrence.WEEKLY, until=utc.localize(datetime.datetime(2015, 1, 31, 16, 0, 0)))]))
        # save should call rearrange
        self.assertListEqual(
            map(lambda e: e.issue_date, self.programme.episode_set.all().order_by('issue_date')[:5]),
            [
                utc.localize(datetime.datetime(2015, 1, 1, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 2, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 3, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 4, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 5, 14, 0)),
            ]
        )
