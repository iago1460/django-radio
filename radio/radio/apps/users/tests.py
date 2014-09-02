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

from django.contrib.auth.models import User
from django.test import TestCase

from radio.apps.programmes.models import Programme, Role
from radio.apps.users.models import UserProfile


class UserProfileMethodTests(TestCase):

    def test_save(self):
        user_profile = UserProfile(user=User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword'), bio='my bio')
        user_profile.save()
        self.assertEqual(user_profile, UserProfile.objects.get(id=user_profile.id))

    def test_get_announcers_and_profile(self):
        user = User(username='user1', password='a')
        user.save()
        user_profile = UserProfile(user=user, bio='my bio')
        user_profile.save()
        programme = Programme.objects.create(name="Test programme", synopsis="This is a description", current_season=1, _runtime=60, start_date=datetime.date(2014, 1, 31))
        role = Role.objects.create(person=user, programme=programme)
        self.assertEqual(programme, Programme.objects.get(id=programme.id))
        self.assertEqual(user_profile, UserProfile.objects.get(id=user_profile.id))
        self.assertEqual(user, user_profile.user)
        self.assertEqual(user, programme.announcers.all()[0])

