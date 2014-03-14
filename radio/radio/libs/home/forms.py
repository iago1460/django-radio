from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

"""
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password',)
"""
class LoginForm(forms.Form):
    username = forms.CharField(required=True, label=_('username'))
    password = forms.CharField(required=True, label=_('password'), widget=forms.PasswordInput)
