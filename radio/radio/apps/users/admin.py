import re

from django import forms
from django.conf.urls import url, patterns
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core import validators
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from radio.apps.users.models import UserProfile
from radio.libs.non_staff_admin.admin import non_staff_admin_site

try:
    from django.utils.encoding import force_unicode
except ImportError:
    from django.utils.encoding import force_text as force_unicode


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    exclude = ('slug',)

class UserProfileAdmin(UserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)



########### Profile ###########


class NonStaffUserProfileForm(forms.ModelForm):

    username = forms.CharField(label=_('username'), max_length=30,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), 'invalid')
        ])
    first_name = forms.CharField(label=_('first name'), max_length=30, required=False)
    last_name = forms.CharField(label=_('last name'), max_length=30, required=False)
    email = forms.EmailField(label=_('email address'), required=False)
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, required=False, help_text=_("Enter the same password as above, for verification."))

    def __init__(self, *args, **kwargs):
        super(NonStaffUserProfileForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.instance = kwargs['instance']
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            # If one field gets autocompleted but not the other, our 'neither
            # password or both password' validation will be triggered.
            self.fields['password1'].widget.attrs['autocomplete'] = 'off'
            self.fields['password2'].widget.attrs['autocomplete'] = 'off'


    def save(self, force_insert=False, force_update=False, commit=True):
        instance = super(NonStaffUserProfileForm, self).save(commit=False)
        instance.user.username = self.cleaned_data['username']
        instance.user.first_name = self.cleaned_data['first_name']
        instance.user.last_name = self.cleaned_data['last_name']
        instance.user.email = self.cleaned_data['email']
        instance.user.set_password(self.cleaned_data['password1'])
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

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if (password1 and password2 and password1 != password2) or (password1 and not password2) or (password2 and not password1):
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

class SingletonProfileAdmin(admin.ModelAdmin):
    form = NonStaffUserProfileForm
    fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email' , 'bio', 'avatar', 'display_personal_page']

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
            'model_name': self.model._meta.module_name,
        }
        custom_urls = patterns('',
            url(r'^history/$',
                self.admin_site.admin_view(self.history_view),
                {'object_id': '-1'},
                name='%s_history' % url_name_prefix),
            url(r'^$',
                self.admin_site.admin_view(self.change_view),
                {'object_id': '-1'},
                name='%s_change' % url_name_prefix),
        )
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

non_staff_admin_site.register(UserProfile, SingletonProfileAdmin)



