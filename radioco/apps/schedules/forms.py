from django import forms

from radioco.apps.schedules.models import Schedule


class DeleteScheduleForm(forms.Form):
    # Choices if the schedule has recurrences
    DELETE_ONLY_THIS = 'only_this'
    DELETE_THIS_AND_FOLLOWING = 'this_and_following'
    DELETE_ALL = 'all'

    # http://stackoverflow.com/questions/32498247/in-django-how-can-i-get-a-widget-that-accepts-an-iso-8601-datetime-string-and-wo#comment-52859176
    # transmission_dt = forms.DateTimeField(input_formats=["%Y-%m-%dT%H:%M:%S.%z"], widget=forms.HiddenInput)
    transmission_dt = forms.DateTimeField(widget=forms.HiddenInput)
    schedule = forms.ModelChoiceField(queryset=Schedule.objects.all(), widget=forms.HiddenInput)

    def __init__(self, has_recurrences, *args, **kwargs):
        super(DeleteScheduleForm, self).__init__(*args, **kwargs)
        if has_recurrences:
            choices = (
                (self.DELETE_ONLY_THIS, 'Only this instance'),
                (self.DELETE_THIS_AND_FOLLOWING, 'This and all the following events'),
                (self.DELETE_ALL, 'All events in the series'),
            )
            self.fields['action'] = forms.ChoiceField(choices=choices, label='', help_text='', widget=forms.RadioSelect)
