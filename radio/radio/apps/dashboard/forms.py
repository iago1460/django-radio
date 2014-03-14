from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Button
from crispy_forms.layout import Submit
from django import forms
from django.forms.extras import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

from radio.apps.programmes.models import Programme
from radio.apps.users.models import UserProfile


# import floppyforms as forms
class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        widgets = {
            'start_date': SelectDateWidget(required=True),
            'end_date': SelectDateWidget(required=False),
        }
        exclude = ('slug',)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'slug',)
