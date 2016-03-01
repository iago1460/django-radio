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
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.options import ModelAdmin

from apps.programmes.models import Programme, Episode


class ProgrammeModelTests(TestCase):

    def setUp(self):
        self.programme = Programme.objects.create(
            name="Test programme",
            synopsis="This is a description",
            _runtime=540,
            start_date=datetime.date(2014, 1, 31),
            end_date=datetime.datetime(2014, 1, 31, 12, 0, 0, 0),
            current_season=1)

    def test_save_programme(self):
        self.assertEqual(
            self.programme, Programme.objects.get(id=self.programme.id))

    def test_runtime(self):
        self.assertEqual(datetime.timedelta(hours=+9), self.programme.runtime)

    def test_save_episode(self):
        date_published = datetime.datetime(2014, 1, 31, 0, 0, 0, 0)
        episode = Episode.create_episode(
            date=date_published, programme=self.programme)

        self.assertEqual(episode, Episode.objects.get(id=episode.id))
        self.assertEqual(
            episode.programme, Programme.objects.get(id=episode.programme.id))

    def test_recurrence_is_empty(self):
        self.assertFalse(self.programme.recurrences.rrules)

    def test_recurrences_contains_rrules(self):
        rrule = recurrence.Rule(recurrence.DAILY)
        self.programme.recurrences=recurrence.Recurrence(rrules=[rrule])
        self.assertEqual(
            self.programme.recurrences.rrules[0].to_text(), 'daily')


class ProgrammeModelAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()

    def test_fieldset(self):
        ma = ModelAdmin(Programme, self.site)
        self.assertEqual(
            ma.get_fields(None), 
            ['name', 'start_date', 'end_date', 'synopsis', 'photo', 'language',
             'current_season', 'category', 'slug', '_runtime', 'recurrences'])
