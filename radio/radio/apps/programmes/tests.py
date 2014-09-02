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
from django.test import TestCase

from radio.apps.programmes.models import Programme, Episode


class ProgrammeMethodTests(TestCase):

    def test_save_programme(self):
        programme = Programme.objects.create(name="Test programme", synopsis="This is a description", _runtime=60, start_date=datetime.date(2014, 1, 31), current_season=1)
        self.assertEqual(programme, Programme.objects.get(id=programme.id))
        self.assertTrue(programme in Programme.objects.all())

    def test_save_episode(self):
        date_published = datetime.datetime(2014, 1, 31, 0, 0, 0, 0)
        programme = Programme.objects.create(name="Test programme", synopsis="This is a description", _runtime=60, start_date=datetime.date(2014, 1, 31), current_season=1)
        episode = Episode.create_episode(date=date_published, programme=programme)

        self.assertEqual(episode, Episode.objects.get(id=episode.id))
        self.assertEqual(programme, Programme.objects.get(id=programme.id))
        self.assertEqual(episode.programme, Programme.objects.get(id=episode.programme.id))

