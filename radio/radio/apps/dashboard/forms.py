from django import forms
from django.contrib.auth.models import User
from django.forms.extras import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

from radio.apps.programmes.models import Programme, Role
from radio.apps.schedules.models import Schedule
from radio.apps.users.models import UserProfile


class ProgrammeMinimumForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = ['name', 'synopsis', 'current_season', 'photo', 'language']

class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        widgets = {
            'start_date': SelectDateWidget(required=True),
            'end_date': SelectDateWidget(required=False),
        }
        exclude = ('slug', 'announcers')

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role

class RoleMinimumForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role', 'description']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'slug',)

class ScheduleForm(forms.Form):

    def __init__(self, queryset, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.fields['source'] = forms.ModelChoiceField(queryset=queryset, required=False, empty_label=_('Without reference'), label=_("source"))
        self.fields['source'].widget.attrs.update({'class' : 'form-control'})
