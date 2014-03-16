from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import User
from django.forms.extras import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

from radio.apps.programmes.models import Programme
from radio.apps.users.models import UserProfile


class ProgrammeMinimumForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = ['name', 'synopsis', 'photo', 'language']

class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        widgets = {
            'start_date': SelectDateWidget(required=True),
            'end_date': SelectDateWidget(required=False),
        }
        exclude = ('slug',)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'slug',)
