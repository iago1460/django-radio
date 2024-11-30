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


import re

from django import forms
from django.urls import re_path
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core import validators
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from radioco.apps.users.models import UserProfile

try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_str as force_unicode


# USER

class UserProfileInline(admin.StackedInline):
    inline_classes = ('grp-collapse grp-open',)
    extra = 1
    model = UserProfile
    can_delete = False
    exclude = ('slug',)


class UserProfileAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'userprofile__display_personal_page')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)


# PROFILE

class NonStaffUserProfileForm(forms.ModelForm):
    username = forms.CharField(
        label=_('username'), max_length=30,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ]
    )
    first_name = forms.CharField(label=_('first name'), max_length=30, required=False)
    last_name = forms.CharField(label=_('last name'), max_length=30, required=False)
    email = forms.EmailField(label=_('email address'), required=False)

    def __init__(self, *args, **kwargs):
        super(NonStaffUserProfileForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.instance = kwargs['instance']
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, force_insert=False, force_update=False, commit=True):
        instance = super(NonStaffUserProfileForm, self).save(commit=False)
        instance.user.username = self.cleaned_data['username']
        instance.user.first_name = self.cleaned_data['first_name']
        instance.user.last_name = self.cleaned_data['last_name']
        instance.user.email = self.cleaned_data['email']
        if commit:
            instance.user.save()
            instance.save()
        return instance

    def clean_username(self):
        username = self.cleaned_data['username']
        user = self.instance.user
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            raise forms.ValidationError(_('User with this Username already exists.'))
        return username


class SingletonProfileAdmin(admin.ModelAdmin):
    form = NonStaffUserProfileForm
    fields = ['username', 'first_name', 'last_name', 'email', 'bio', 'avatar', 'display_personal_page']

    def save_model(self, request, obj, form, change):
        if obj.pk:
            user = obj.user
            user.save()
            obj.save()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super(SingletonProfileAdmin, self).get_urls()
        url_name_prefix = '%(app_name)s_%(model_name)s' % {
            'app_name': self.model._meta.app_label,
            'model_name': self.model._meta.model_name,
        }
        custom_urls = [
            re_path(r'^history/$',
                self.admin_site.admin_view(self.history_view),
                {'object_id': '-1'},
                name='%s_history' % url_name_prefix
            ),
            re_path(r'^$',
                self.admin_site.admin_view(self.change_view),
                {'object_id': '-1'},
                name='%s_change' % url_name_prefix
            ),
        ]
        # By inserting the custom URLs first, we overwrite the standard URLs.
        return custom_urls + urls

    def response_change(self, request, obj):
        msg = _('%(obj)s was changed successfully.') % {'obj': force_unicode(obj)}
        if '_continue' in request.POST:
            # self.message_user(request, msg + ' ' + _('You may edit it again below.'))
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)
            return HttpResponseRedirect("../../")

    def change_view(self, request, object_id, extra_context=None):
        if object_id == '-1':
            object_id = str(request.user.id)
        return super(SingletonProfileAdmin, self).change_view(
            request,
            object_id,
            extra_context=extra_context,
        )


admin.site.register(UserProfile, SingletonProfileAdmin)
