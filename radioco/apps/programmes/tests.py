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

from radioco.apps.programmes.models import Programme, Episode, EpisodeManager, Role
from radioco.apps.radio.tests import TestDataMixin
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, FieldError
from django.core.urlresolvers import reverse
from django.test import TestCase
import datetime


class ProgrammeModelTests(TestCase):

    def setUp(self):
        self.programme = Programme.objects.create(
            name="Test programme",
            synopsis="This is a description",
            _runtime=540,
            current_season=1)

    def test_save_programme(self):
        self.assertEqual(
            self.programme, Programme.objects.get(id=self.programme.id))

    def test_slug(self):
        self.assertEqual(self.programme.slug, "test-programme")

    def test_runtime(self):
        self.assertEqual(datetime.timedelta(hours=+9), self.programme.runtime)

    def test_runtime_not_get(self):
        programme = Programme(name="foo", current_season=1)
        with self.assertRaises(FieldError):
            programme.runtime

    def test_runtime_not_set(self):
        programme = Programme(name="foo", current_season=1, slug="foo")
        with self.assertRaises(ValidationError):
            programme.clean_fields()

    def test_runtime_is_zero(self):
        programme = Programme(name="foo", current_season=1, slug="foo")
        programme.runtime = 0
        with self.assertRaises(ValidationError):
            programme.clean_fields()

    def test_absolute_url(self):
        self.assertEqual(
            self.programme.get_absolute_url(), "/programmes/test-programme/")

    def test_str(self):
        self.assertEqual(str(self.programme), "Test programme")

#    def test_save_episode(self):
#        date_published = datetime.datetime(2014, 1, 31, 0, 0, 0, 0)
#        episode = Episode.create_episode(
#            date=date_published, programme=self.programme)
#
#        self.assertEqual(episode, Episode.objects.get(id=episode.id))
#        self.assertEqual(
#            episode.programme, Programme.objects.get(id=episode.programme.id))


class ProgrammeModelAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()

    def test_fieldset(self):
        ma = ModelAdmin(Programme, self.site)
        self.assertEqual(
            ma.get_fields(None),
            ['name', 'synopsis', 'photo', 'language', 'current_season', 'category', 'slug', '_runtime'])


class EpisodeManagerTests(TestDataMixin, TestCase):
    def setUp(self):
        self.manager = EpisodeManager()

        self.episode = self.manager.create_episode(
            datetime.datetime(2014, 6, 14, 10, 0, 0), self.programme)

    def test_create_episode(self):
        self.assertIsInstance(self.episode, Episode)

    def test_season(self):
        self.assertEqual(self.episode.season, self.programme.current_season)

    def test_number_in_season(self):
        self.assertEqual(self.episode.number_in_season, 6)

    def test_programme(self):
        self.assertEqual(self.episode.programme, self.programme)

    def test_issue_date(self):
        self.assertEqual(
            self.episode.issue_date, datetime.datetime(2014, 6, 14, 10, 0, 0))

    def test_people(self):
        self.assertQuerysetEqual(
            self.episode.people.all(), self.programme.announcers.all())

    def test_last(self):
        episode = self.manager.last(self.programme)
        self.assertEqual(episode.season, 7)
        self.assertEqual(episode.number_in_season, 6)

    def test_last_none(self):
        episode = self.manager.last(Programme())
        self.assertIsNone(episode)

    def test_unfinished(self):
        episodes = self.manager.unfinished(
            self.programme, datetime.datetime(2015, 1, 1))
        self.assertEqual(
            episodes.next().issue_date, datetime.datetime(2015, 1, 1, 14, 0))

    def test_unfinished_none(self):
        episodes = self.manager.unfinished(Programme())
        with self.assertRaises(StopIteration):
            episodes.next()


class EpisodeModelTests(TestCase):
    def setUp(self):
        self.programme = Programme.objects.create(
            name="Test programme",
            synopsis="This is a description",
            _runtime=540,
            current_season=8)

        self.episode = Episode.objects.create_episode(
            datetime.datetime(2014, 1, 14, 10, 0, 0), self.programme)

    def test_model_manager(self):
        self.assertIsInstance(self.episode, Episode)

    def test_runtime(self):
        self.assertEqual(self.episode.runtime, datetime.timedelta(0, 32400))

    def test_absoulte_url(self):
        self.assertEqual(
            self.episode.get_absolute_url(), "/programmes/test-programme/8x1/")

    def test_str(self):
        self.assertEqual(str(self.episode), "8x1 Test programme")
