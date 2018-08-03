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

import pytz
from django.core.urlresolvers import reverse
from django.test import TestCase

from radioco.apps.radioco.utils import create_example_data
from radioco.apps.radioco.test_utils import TestDataMixin, SPAIN_TZ


class UtilsTest(TestCase):

    def test_example_data(self):
        """
        Running example data function, If nothing crash we are happy
        """
        create_example_data()

    def test_dictionary_key(self):
        """
        Making sure that is safe to use a dt tz aware object in a different timezone to access a dictionary
        """
        utc_dt = pytz.utc.localize(datetime.datetime(2015, 1, 1, 13, 0, 0))
        spanish_dt = SPAIN_TZ.localize(datetime.datetime(2015, 1, 1, 13, 0, 0))

        utc_dict = {utc_dt: 'Created using utc dt'}
        spain_dict = {spanish_dt: 'Created using spanish dt'}
        self.assertEqual(utc_dict.get(utc_dt), utc_dict.get(utc_dt.astimezone(SPAIN_TZ)))
        self.assertEqual(spain_dict.get(spanish_dt), spain_dict.get(spanish_dt.astimezone(pytz.utc)))


class RadioIntegrationTests(TestDataMixin, TestCase):
    def test_index(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
