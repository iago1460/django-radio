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

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from mock import patch

from radio.apps.programmes.models import Programme, Episode
from radio.apps.schedules.models import ScheduleBoard, Schedule, MO, TU, WE, TH, FR, SA, SU


def to_relativedelta(tdelta):
    return relativedelta(seconds=int(tdelta.total_seconds()),
                         microseconds=tdelta.microseconds)

class ProgrammeMethodTests(TestCase):

    def setUp(self):
        midnight_programme = Programme.objects.create(name="Programme 00:00 - 09:00", synopsis="This is a description",
                                                      start_date=datetime.datetime(2014, 1, 1, 0, 0, 0, 0),
                                                      end_date=datetime.datetime(2014, 1, 31, 12, 0, 0, 0),
                                                      current_season=1, runtime=540)

        schedule_board = ScheduleBoard(name='Board', start_date=datetime.datetime(2014, 1, 1, 0, 0, 0, 0))
        schedule_board.save()
        start_hour = datetime.time(0, 0, 0)
        Schedule.objects.create(programme=midnight_programme, day=MO, start_hour=start_hour, type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=midnight_programme, day=TU, start_hour=start_hour, type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=midnight_programme, day=WE, start_hour=start_hour, type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=midnight_programme, day=TH, start_hour=start_hour, type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=midnight_programme, day=FR, start_hour=start_hour, type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=midnight_programme, day=SA, start_hour=start_hour, type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=midnight_programme, day=SU, start_hour=start_hour, type='L', schedule_board=schedule_board)

        programme = Programme.objects.create(name="Programme 09:00 - 10:00", synopsis="This is a description",
                                                     start_date=datetime.datetime(2014, 1, 1),
                                                     end_date=datetime.datetime(2014, 1, 31),
                                                     current_season=1, runtime=60)
        Schedule.objects.create(programme=programme, day=MO, start_hour=datetime.time(9, 0, 0), type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=programme, day=WE, start_hour=datetime.time(9, 0, 0), type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=programme, day=FR, start_hour=datetime.time(9, 0, 0), type='L', schedule_board=schedule_board)

        programme = Programme.objects.create(name="Programme 10:00 - 12:00", synopsis="This is a description",
                                                     start_date=datetime.datetime(2014, 1, 1),
                                                     end_date=datetime.datetime(2014, 1, 31),
                                                     current_season=1, runtime=120)
        Schedule.objects.create(programme=programme, day=MO, start_hour=datetime.time(10, 0, 0), type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=programme, day=WE, start_hour=datetime.time(10, 0, 0), type='L', schedule_board=schedule_board)
        Schedule.objects.create(programme=programme, day=FR, start_hour=datetime.time(10, 0, 0), type='L', schedule_board=schedule_board)

        for schedule in Schedule.objects.all():
            schedule.clean()

    def test_runtime(self):
        programme = Programme.objects.get(name="Programme 00:00 - 09:00")
        self.assertEqual(relativedelta(hours=+9), to_relativedelta(programme.runtime))

    def test_day_schedule(self):
        schedules, dates = Schedule.between(datetime.datetime(2014, 1, 6), datetime.datetime(2014, 1, 7))
        self.assertEqual(4, len(schedules))
        schedule_1 = Schedule.objects.get(programme=Programme.objects.get(name="Programme 00:00 - 09:00"), day=MO)
        schedule_2 = Schedule.objects.get(programme=Programme.objects.get(name="Programme 09:00 - 10:00"), day=MO)
        schedule_3 = Schedule.objects.get(programme=Programme.objects.get(name="Programme 10:00 - 12:00"), day=MO)
        schedule_4 = Schedule.objects.get(programme=Programme.objects.get(name="Programme 00:00 - 09:00"), day=TU)
        self.assertTrue(schedule_1 in schedules)
        self.assertTrue(schedule_2 in schedules)
        self.assertTrue(schedule_3 in schedules)
        self.assertTrue(schedule_4 in schedules)

    def test_now_playing_1(self):
        now_mock = datetime.datetime(2014, 1, 6, 0, 0, 0, 0)
        schedule, date = Schedule.schedule(now_mock)
        schedule_1 = Schedule.objects.get(programme=Programme.objects.get(name="Programme 00:00 - 09:00"), day=MO)
        self.assertEqual(schedule_1, schedule)
        self.assertEqual(datetime.datetime.combine(now_mock, schedule_1.start_hour), date)

    def test_now_playing_2(self):
        now_mock = datetime.datetime(2014, 1, 7, 0, 0, 0, 0)
        schedule, date = Schedule.schedule(now_mock)
        schedule_1 = Schedule.objects.get(programme=Programme.objects.get(name="Programme 00:00 - 09:00"), day=TU)
        self.assertEqual(schedule_1, schedule)
        self.assertEqual(datetime.datetime.combine(now_mock, schedule_1.start_hour), date)




class ScheduleBoardMethodTests(TestCase):
    def setUp(self):
        ScheduleBoard.objects.create(name="january", start_date=datetime.datetime(2014, 1, 1), end_date=datetime.datetime(2014, 1, 31))
        ScheduleBoard.objects.create(name="1_14_february", start_date=datetime.datetime(2014, 2, 1), end_date=datetime.datetime(2014, 2, 14))
        ScheduleBoard.objects.create(name="after_14_february", start_date=datetime.datetime(2014, 2, 15))
        for schedule_board in ScheduleBoard.objects.all():
            schedule_board.clean()

    def test_runtime(self):
        january_board = ScheduleBoard.objects.get(name="january")
        february_board = ScheduleBoard.objects.get(name="1_14_february")
        after_board = ScheduleBoard.objects.get(name="after_14_february")

        self.assertEqual(None, ScheduleBoard.get_current(datetime.datetime(2013, 12, 1, 0, 0, 0, 0)))
        self.assertEqual(january_board, ScheduleBoard.get_current(datetime.datetime(2014, 1, 1, 0, 0, 0, 0)))
        self.assertEqual(january_board, ScheduleBoard.get_current(datetime.datetime(2014, 1, 31, 0, 0, 0, 0)))
        self.assertEqual(january_board, ScheduleBoard.get_current(datetime.datetime(2014, 1, 31, 12, 0, 0, 0)))
        self.assertEqual(february_board, ScheduleBoard.get_current(datetime.datetime(2014, 2, 1, 0, 0, 0, 0)))
        self.assertEqual(february_board, ScheduleBoard.get_current(datetime.datetime(2014, 2, 14, 0, 0, 0, 0)))
        self.assertEqual(after_board, ScheduleBoard.get_current(datetime.datetime(2014, 2, 15, 0, 0, 0, 0)))
        self.assertEqual(after_board, ScheduleBoard.get_current(datetime.datetime(2014, 6, 1, 0, 0, 0, 0)))

    def test_validation_exception_1(self):
        schedule_board = ScheduleBoard.objects.create(name="2_14_february", start_date=datetime.datetime(2014, 2, 2), end_date=datetime.datetime(2014, 2, 14))
        self.assertRaises(ValidationError, schedule_board.clean)

    def test_validation_exception_2(self):
        schedule_board = ScheduleBoard.objects.create(name="after_18_february", start_date=datetime.datetime(2014, 2, 18))
        self.assertRaises(ValidationError, schedule_board.clean)

