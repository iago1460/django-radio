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

import mock
import pytz
import recurrence
from django.core.exceptions import ValidationError, FieldError
from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete
from django.forms import modelform_factory
from django.test import TestCase
from django.utils import timezone

from radioco.apps.radioco.tests import TestDataMixin
from radioco.apps.programmes.models import Programme
from radioco.apps.schedules import utils
from radioco.apps.schedules.models import Schedule, Transmission
from radioco.apps.schedules.models import Calendar, CalendarManager


class RecurrenceTests(TestDataMixin, TestCase):
    def setUp(self):
        # self.daily_recurrence = recurrence.Recurrence(
        #     dtstart=datetime.datetime(2014, 1, 6, 14, 0, 0),
        #     dtend=datetime.datetime(2014, 1, 31, 14, 0, 0),
        #     rrules=[recurrence.Rule(recurrence.DAILY)])
        # 
        # self.weekly_recurrence = recurrence.Recurrence(
        #     dtstart=datetime.datetime(2014, 1, 6, 14, 0, 0),
        #     dtend=datetime.datetime(2014, 1, 31, 14, 0, 0),
        #     rrules=[recurrence.Rule(recurrence.WEEKLY)])

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
