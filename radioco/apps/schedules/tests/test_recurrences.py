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

import recurrence
from django.test import TestCase

from radioco.apps.radioco.test_utils import TestDataMixin
from radioco.apps.radioco.tz_utils import recurrence_after, recurrence_before


class RecurrenceTests(TestDataMixin, TestCase):
    """
    Tests to check django-recurrence behaviour
    """
    def setUp(self):
        self.monthly_recurrence = recurrence.Recurrence(
            rrules=[recurrence.Rule(recurrence.MONTHLY)])

    def test_when_date_doesnt_exist_on_february(self):
        after_dt = datetime.datetime(2014, 1, 29, 14, 0, 0)
        before_dt = datetime.datetime(2014, 12, 29, 13, 59, 59)
        start_dt = after_dt
        dts = self.monthly_recurrence.between(after_dt, before_dt, inc=True, dtstart=start_dt)

        self.assertEquals(10, len(dts), dts)

        # assert datetime.datetime(2014, 2, 29, 14, 0, 0) not in dts, day is out of range for month
        assert datetime.datetime(2014, 12, 29, 14, 0, 0) not in dts

    def test_last_date_is_equals_before_limit(self):
        after_dt = datetime.datetime(2014, 1, 20, 14, 0, 0)
        before_dt = datetime.datetime(2014, 2, 20, 14, 0, 0)
        start_dt = after_dt

        dts = self.monthly_recurrence.between(after_dt, before_dt, inc=True, dtstart=start_dt)

        self.assertEquals(2, len(dts), dts)
        assert datetime.datetime(2014, 2, 20, 14, 0, 0) in dts

    def test_start_date_is_before_start_limit(self):
        after_dt = datetime.datetime(2014, 1, 20, 14, 0, 0)
        before_dt = datetime.datetime(2014, 2, 20, 14, 0, 0)
        start_dt = datetime.datetime(2014, 1, 19, 14, 0, 0)

        dts = self.monthly_recurrence.between(after_dt, before_dt, inc=True, dtstart=start_dt)

        self.assertEquals(1, len(dts), dts)
        assert datetime.datetime(2014, 2, 19, 14, 0, 0) in dts

    def test_after(self):
        start_dt = datetime.datetime(2014, 1, 20, 14, 0, 0)
        after = datetime.datetime(2014, 1, 1, 13, 59, 59)
        dt = self.monthly_recurrence.after(after, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 20, 14, 0, 0), dt)

        after = start_dt
        dt = self.monthly_recurrence.after(after, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 2, 20, 14, 0, 0), dt)

    def test_after_inclusive(self):
        start_dt = datetime.datetime(2014, 1, 20, 14, 0, 0)
        after = start_dt
        dt = self.monthly_recurrence.after(after, True, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 20, 14, 0, 0), dt)

    def test_before_dt(self):
        start_dt = datetime.datetime(2014, 1, 20, 14, 0, 0)
        before = datetime.datetime(2014, 1, 20, 14, 0, 1)
        dt = self.monthly_recurrence.before(before, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 20, 14, 0, 0), dt)

        before = start_dt
        assert self.monthly_recurrence.before(before, dtstart=start_dt) is None

    def test_before_inclusive(self):
        start_dt = datetime.datetime(2014, 1, 20, 14, 0, 0)
        before = start_dt
        dt = self.monthly_recurrence.before(before, True, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 20, 14, 0, 0), dt)

    def test_impossible_recurrence_after(self):
        """
        Testing error calling after and function wrapper to solve it (recurrence_after)
        """
        start_dt = datetime.datetime(2014, 1, 20, 14, 0, 0)
        until_dt = datetime.datetime(2014, 1, 19, 14, 0, 0)
        daily_recurrence = recurrence.Recurrence(
            rrules=[recurrence.Rule(recurrence.DAILY, until=until_dt)])

        dt = daily_recurrence.after(start_dt, True, dtstart=start_dt)
        self.assertEquals(start_dt, dt)  # wrong!

        self.assertIsNone(recurrence_after(daily_recurrence, start_dt, start_dt))

    def test_impossible_recurrence_before(self):
        """
        Testing error calling before and function wrapper to solve it (recurrence_before)
        """
        start_dt = datetime.datetime(2014, 1, 20, 14, 0, 0)
        until_dt = datetime.datetime(2014, 1, 19, 14, 0, 0)
        daily_recurrence = recurrence.Recurrence(
            rrules=[recurrence.Rule(recurrence.MONTHLY, until=until_dt)])

        dt = daily_recurrence.before(start_dt + datetime.timedelta(seconds=1), dtstart=start_dt)
        self.assertEquals(start_dt, dt)  # wrong!

        self.assertIsNone(recurrence_before(daily_recurrence, start_dt + datetime.timedelta(seconds=1), start_dt))


class EmptyRecurrenceTests(TestDataMixin, TestCase):
    """
    Tests to check django-recurrence behaviour when there are no recurrences
    """
    def setUp(self):
        self.empty_recurrence = recurrence.Recurrence()

    def test_no_values(self):
        self.assertFalse(bool(self.empty_recurrence))

    def test_after(self):
        start_dt = datetime.datetime(2014, 1, 1, 14, 0, 0)
        after = datetime.datetime(2014, 1, 1, 13, 59, 59)
        dt = self.empty_recurrence.after(after, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 1, 14, 0, 0), dt)

        after = start_dt
        self.assertIsNone(self.empty_recurrence.after(after, dtstart=start_dt))

        after = datetime.datetime(2014, 1, 1, 14, 0, 1)
        self.assertIsNone(self.empty_recurrence.after(after, dtstart=start_dt))

    def test_after_inclusive(self):
        start_dt = datetime.datetime(2014, 1, 1, 14, 0, 0)
        after = datetime.datetime(2014, 1, 1, 13, 59, 59)
        dt = self.empty_recurrence.after(after, True, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 1, 14, 0, 0), dt)

        after = start_dt
        dt = self.empty_recurrence.after(after, True, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 1, 14, 0, 0), dt)

        after = datetime.datetime(2014, 1, 1, 14, 0, 1)
        self.assertIsNone(self.empty_recurrence.after(after, True, dtstart=start_dt))

    def test_before(self):
        start_dt = datetime.datetime(2014, 1, 1, 14, 0, 0)
        before = datetime.datetime(2014, 1, 1, 14, 0, 1)
        dt = self.empty_recurrence.before(before, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 1, 14, 0, 0), dt)

        before = start_dt
        self.assertIsNone(self.empty_recurrence.before(before, dtstart=start_dt))

        before = datetime.datetime(2014, 1, 1, 13, 59, 59)
        self.assertIsNone(self.empty_recurrence.before(before, dtstart=start_dt))

    def test_before_inclusive(self):
        start_dt = datetime.datetime(2014, 1, 1, 14, 0, 0)
        before = datetime.datetime(2014, 1, 1, 14, 0, 1)
        dt = self.empty_recurrence.before(before, True, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 1, 14, 0, 0), dt)

        before = start_dt
        dt = self.empty_recurrence.before(before, True, dtstart=start_dt)
        self.assertEquals(datetime.datetime(2014, 1, 1, 14, 0, 0), dt)

        before = datetime.datetime(2014, 1, 1, 13, 59, 59)
        self.assertIsNone(self.empty_recurrence.before(before, True, dtstart=start_dt))
