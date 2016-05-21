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

from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.schedules.models import Schedule, ScheduleBoard
from django.core.urlresolvers import reverse
from django.test import TestCase
import datetime
import utils


class TestDataMixin(object):
    @classmethod
    def setUpTestData(cls):
        utils.create_example_data()
        cls.programme = Programme.objects.filter(name="Classic hits").get()
        cls.schedule = cls.programme.schedule_set.first()
        cls.schedule_board = cls.schedule.schedule_board
        cls.episode = cls.programme.episode_set.first()
        cls.another_board = ScheduleBoard.objects.create(name="Another")
        cls.another_board.schedule_set.add(Schedule(
            programme=cls.programme,
            type='S',
            start=datetime.datetime(2015, 1, 6, 16, 30, 0)))


class RadioIntegrationTests(TestDataMixin, TestCase):
    def test_index(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

