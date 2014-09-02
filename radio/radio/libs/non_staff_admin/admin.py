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


from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from radio.libs.non_staff_admin.forms import UserAdminAuthenticationForm


class UserAdmin(AdminSite):

    index_template = 'non_staff_admin/index.html'
    login_form = UserAdminAuthenticationForm

    def has_permission(self, request):
        '''
        Removed check for is_staff.
        '''
        return request.user.is_active


non_staff_admin_site = UserAdmin(name='usersadmin')
