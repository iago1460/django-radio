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
