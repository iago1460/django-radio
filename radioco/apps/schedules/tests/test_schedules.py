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
import recurrence
from django.contrib.admin import AdminSite
from django.core.exceptions import ValidationError, FieldError
from django.core.urlresolvers import reverse
from django.forms import modelform_factory
from django.test import TestCase
from django.test import override_settings
from django.utils import timezone
from pytz import utc

from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.radioco.test_utils import TestDataMixin
from radioco.apps.schedules.admin import CalendarAdmin
from radioco.apps.schedules.models import Calendar, CalendarManager
from radioco.apps.schedules.models import Schedule, Transmission
from radioco.apps.schedules.utils import next_dates


def mock_now(dt=pytz.utc.localize(datetime.datetime(2014, 1, 1, 13, 30, 0))):
    return dt


class ScheduleValidationTests(TestDataMixin, TestCase):
    def test_fields(self):
        schedule = Schedule()
        with self.assertRaisesMessage(
            ValidationError,
            "{'programme': ['This field cannot be null.'], 'type': ['This field cannot be blank.'], 'calendar': ['This field cannot be null.'], 'start_dt': ['This field cannot be null.']}"
        ):
            schedule.clean_fields()


@override_settings(TIME_ZONE='UTC')
class ScheduleModelTests(TestDataMixin, TestCase):
    def setUp(self):
        self.calendar = Calendar.objects.create(name='Calendar', is_active=True)

        self.recurrences = recurrence.Recurrence(
            rrules=[recurrence.Rule(recurrence.WEEKLY, until=utc.localize(datetime.datetime(2014, 1, 31)))])

        programme = Programme.objects.filter(name="Classic hits").get()
        programme.name = "Classic hits 2"
        programme.slug = None
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
        self.programme.rearrange_episodes(pytz.utc.localize(datetime.datetime(1970, 1, 1)), Calendar.get_active())
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
        self.assertCountEqual(
            self.schedule.dates_between(
                utc.localize(datetime.datetime(2014, 1, 1)), utc.localize(datetime.datetime(2014, 1, 14))),
            [utc.localize(datetime.datetime(2014, 1, 6, 14, 0)),
             utc.localize(datetime.datetime(2014, 1, 13, 14, 0))])

    def test_dates_between_later_start_by_programme(self):
        self.programme.start_date = datetime.date(2014, 1, 7)
        self.programme.save()
        self.schedule.refresh_from_db()
        self.assertCountEqual(
            self.schedule.dates_between(
                utc.localize(datetime.datetime(2014, 1, 1)), utc.localize(datetime.datetime(2014, 1, 14))),
            [utc.localize(datetime.datetime(2014, 1, 13, 14, 0))])

    def test_dates_between_earlier_end_by_programme(self):
        self.programme.end_date = datetime.date(2014, 1, 7)
        self.programme.save()
        self.schedule.refresh_from_db()
        self.assertCountEqual(
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

        self.assertCountEqual(
            schedule.dates_between(
                utc.localize(datetime.datetime(2014, 1, 1)), utc.localize(datetime.datetime(2014, 1, 9))),
            [utc.localize(datetime.datetime(2014, 1, 2, 14, 0)),
             utc.localize(datetime.datetime(2014, 1, 4, 14, 0)),
             utc.localize(datetime.datetime(2014, 1, 8, 14, 0))])

    def test_unicode(self):
        self.assertEqual(str(self.schedule), 'Monday - 14:00:00')

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

        self.schedule_without_recurrences = Schedule.objects.create(
            programme=self.programme,
            type='L',
            start_dt=utc.localize(datetime.datetime(2014, 1, 2, 0, 30, 0)),
            calendar=self.calendar)

    def test_dates_between_includes_started_episode(self):
        self.assertCountEqual(
            self.schedule.dates_between(
                utc.localize(datetime.datetime(2014, 1, 2, 0, 0, 0)),
                utc.localize(datetime.datetime(2014, 1, 3, 23, 59, 59))
            ),
            [
                utc.localize(datetime.datetime(2014, 1, 1, 23, 30, 0)),  # Not finished yet
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
            [(t.slug, t.start) for t in list(between)],
            [('classic-hits',  utc.localize(datetime.datetime(2014, 1, 1, 23, 30, 0))),  # Not finished yet
             ('classic-hits',  utc.localize(datetime.datetime(2014, 1, 2, 0, 30, 0))),
             ('classic-hits',  utc.localize(datetime.datetime(2014, 1, 2, 23, 30, 0))),
             ('classic-hits',  utc.localize(datetime.datetime(2014, 1, 3, 23, 30, 0)))])


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
        self.assertEqual(len(Calendar.objects.filter(is_active=True)), 1)

        new_active_calendar = Calendar.objects.create(name="test", is_active=True)

        self.assertEqual(Calendar.objects.get(is_active=True), new_active_calendar)

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


class CalendarAdminTests(TestDataMixin, TestCase):

    def setUp(self):
        self.app_admin = CalendarAdmin(Calendar, AdminSite())

    def test_clone_calendar(self):
        schedule_ids = [_schedule.id for _schedule in self.calendar.schedule_set.all()]
        num_of_schedules = len(schedule_ids)

        self.app_admin.clone_calendar(request=None, queryset=Calendar.objects.filter(id=self.calendar.id))
        cloned_calendar = Calendar.objects.order_by('-id').first()
        self.calendar.refresh_from_db()

        self.assertNotEqual(self.calendar.id, cloned_calendar.id)
        self.assertEqual(num_of_schedules, self.calendar.schedule_set.count())
        self.assertEqual(num_of_schedules, cloned_calendar.schedule_set.count())
        self.assertFalse(
            any(
                [x in schedule_ids for x in [_schedule.id for _schedule in cloned_calendar.schedule_set.all()]]
            )
        )
        self.assertNotEqual(
            frozenset([_schedule.id for _schedule in self.calendar.schedule_set.all()]),
            frozenset([_schedule.id for _schedule in cloned_calendar.schedule_set.all()]),
        )

    # @mock.patch('django.utils.timezone.now', mock_now)
    # @mock.patch('radioco.apps.schedules.utils.rearrange_programme_episodes')
    # def test_delete(self, rearrange_programme_episodes):
    #     def calls():
    #         for programme in Programme.objects.all():
    #             yield mock.call(programme, mock_now())
    # 
    #     post_delete.send(Calendar, instance=self.calendar)
    #     rearrange_programme_episodes.assert_has_calls(calls(), any_order=True)


@override_settings(TIME_ZONE='UTC')
class TransmissionModelTests(TestDataMixin, TestCase):
    def setUp(self):
        dt = utc.localize(datetime.datetime(2015, 1, 6, 14, 0, 0))
        self.episode_in_transmission = Episode.objects.create_episode(date=dt, programme=self.programme)
        self.transmission = Transmission(self.schedule, dt, self.episode_in_transmission)

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

    def test_programme_url(self):
        self.assertEqual(
            self.transmission.programme_url,
            reverse('programmes:detail', args=[self.schedule.programme.slug]))

    def test_episode__url(self):
        self.assertEqual(
            self.transmission.episode_url,
            self.episode_in_transmission.get_absolute_url())

    def test_at(self):
        now = Transmission.at(utc.localize(datetime.datetime(2015, 1, 6, 11, 59, 59)))
        self.assertListEqual(
            [(t.slug, t.start) for t in list(now)],
            [('the-best-wine', utc.localize(datetime.datetime(2015, 1, 6, 11, 0, 0)))])

        now = Transmission.at(utc.localize(datetime.datetime(2015, 1, 6, 12, 0, 0)))
        self.assertListEqual(
            [(t.slug, t.start) for t in list(now)],
            [('local-gossips', utc.localize(datetime.datetime(2015, 1, 6, 12, 0, 0)))])

        now = Transmission.at(utc.localize(datetime.datetime(2015, 1, 6, 12, 59, 59)))
        self.assertListEqual(
            [(t.slug, t.start) for t in list(now)],
            [('local-gossips', utc.localize(datetime.datetime(2015, 1, 6, 12, 0, 0)))])

        now = Transmission.at(utc.localize(datetime.datetime(2015, 1, 6, 13, 0, 0)))
        self.assertListEqual(list(now), [])

    def test_between(self):
        between = Transmission.between(
            utc.localize(datetime.datetime(2015, 1, 6, 11, 0, 0)),
            utc.localize(datetime.datetime(2015, 1, 6, 17, 0, 0)))
        self.assertListEqual(
            [(t.slug, t.start) for t in list(between)],
            [('the-best-wine', utc.localize(datetime.datetime(2015, 1, 6, 11, 0))),
             ('local-gossips', utc.localize(datetime.datetime(2015, 1, 6, 12, 0))),
             ('classic-hits', utc.localize(datetime.datetime(2015, 1, 6, 14, 0)))])

    def test_between_by_queryset(self):
        between = Transmission.between(
            utc.localize(datetime.datetime(2015, 1, 6, 12, 0, 0)),
            utc.localize(datetime.datetime(2015, 1, 6, 17, 0, 0)),
            schedules=Schedule.objects.filter(
                calendar=self.another_calendar).all())
        self.assertListEqual(
            [(t.slug, t.start) for t in list(between)],
            [('classic-hits', utc.localize(datetime.datetime(2015, 1, 6, 16, 30, 0)))])


@override_settings(TIME_ZONE='UTC')
class ScheduleUtilsTests(TestDataMixin, TestCase):

    def setUp(self):
        self.manager = CalendarManager()
        programme = Programme.objects.filter(name="Classic hits").get()
        programme.name = "Classic hits - ScheduleUtilsTests"
        programme.slug = None
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
        programme.rearrange_episodes(pytz.utc.localize(datetime.datetime(1970, 1, 1)), Calendar.get_active())

    def test_available_dates_after(self):
        Schedule.objects.create(
            programme=self.programme,
            calendar=self.calendar,
            type="L",
            start_dt=utc.localize(datetime.datetime(2015, 1, 6, 16, 0, 0)),
            recurrences=recurrence.Recurrence(
                rrules=[recurrence.Rule(recurrence.WEEKLY)]))

        dates = next_dates(self.calendar, self.programme, utc.localize(datetime.datetime(2015, 1, 5)))
        self.assertEqual(next(dates), utc.localize(datetime.datetime(2015, 1, 5, 14, 0)))
        self.assertEqual(next(dates), utc.localize(datetime.datetime(2015, 1, 6, 14, 0)))
        self.assertEqual(next(dates), utc.localize(datetime.datetime(2015, 1, 6, 16, 0)))

    def test_available_dates_none(self):
        dates = next_dates(self.calendar, Programme(), timezone.now())
        with self.assertRaises(StopIteration):
            next(dates)

    def test_rearrange_episodes(self):
        self.programme.rearrange_episodes(pytz.utc.localize(datetime.datetime(2015, 1, 1)), Calendar.get_active())
        self.assertListEqual(
            [e.issue_date for e in self.programme.episode_set.all().order_by('issue_date')[:5]],
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
        # Next calendar shouldn't appear due to doesn't belong to the active calendar
        Schedule.objects.create(
            programme=self.programme,
            calendar=Calendar.objects.create(),
            type="L",
            start_dt=utc.localize(datetime.datetime(2015, 1, 3, 16, 0, 0)),
            recurrences=recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.WEEKLY)]))

        Schedule.objects.create(
            programme=self.programme,
            calendar=self.calendar,
            type="L",
            start_dt=utc.localize(datetime.datetime(2015, 1, 3, 17, 0, 0)),
            recurrences=recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.WEEKLY)]))
        # save should call rearrange
        # rearrange_programme_episodes(self.programme, pytz.utc.localize(datetime.datetime(2015, 1, 1)))
        self.assertListEqual(
            [e.issue_date for e in self.programme.episode_set.all().order_by('issue_date')[:5]],
            [
                utc.localize(datetime.datetime(2015, 1, 1, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 2, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 3, 14, 0)),
                # The next schedule doesn't belong to the active_calendar
                # utc.localize(datetime.datetime(2015, 1, 3, 16, 0)),
                utc.localize(datetime.datetime(2015, 1, 3, 17, 0)),
                utc.localize(datetime.datetime(2015, 1, 4, 14, 0)),
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
            [e.issue_date for e in self.programme.episode_set.all().order_by('issue_date')[:5]],
            [
                utc.localize(datetime.datetime(2015, 1, 1, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 2, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 3, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 4, 14, 0)),
                utc.localize(datetime.datetime(2015, 1, 5, 14, 0)),
            ]
        )
