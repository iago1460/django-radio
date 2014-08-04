from django import forms
from django.utils.translation import ugettext_lazy as _


class ScheduleForm(forms.Form):

    def __init__(self, queryset, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.fields['source'] = forms.ModelChoiceField(queryset=queryset, required=False, empty_label=_('Without reference'), label=_("source"))
        self.fields['source'].widget.attrs.update({'class' : 'form-control'})
