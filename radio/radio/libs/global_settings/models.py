import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from solo.models import SingletonModel
from radio.apps.schedules.models import WEEKDAY_CHOICES


class SiteConfiguration(SingletonModel):
    site_name = models.CharField(max_length=255, default='RadioCo', verbose_name=_("Site Name"))

    def __unicode__(self):
        return _('Global Configuration')

    class Meta:
        verbose_name = _('Global Configuration')
        verbose_name_plural = _('Global Configuration')



class PodcastConfiguration(SingletonModel):
    url_source = models.CharField(blank=True, default="", max_length=500, verbose_name=_("URL Source"), help_text=_("The source url where the recordings will be available after the upload. For example: \"http://RadioCo.org/recordings/\""))
    start_delay = models.PositiveIntegerField(default=0, verbose_name=_("start delay"), help_text=_("In seconds. Initial delay of recordings"))
    end_delay = models.PositiveIntegerField(default=0, verbose_name=_("end delay"), help_text=_("In seconds."))
    next_events = models.PositiveIntegerField(default=32, verbose_name=_("next events"), help_text=_("In hours. The next events supplied to the recorder program"))

    @property
    def recorder_token(self):
        username = settings.USERNAME_RADIOCO_RECORDER
        try:
            user = User.objects.get(username=username)
            token, created = Token.objects.get_or_create(user=user)
            return token.key
        except User.DoesNotExist:
            return _('User %(username)s doesn\'t exist') % {'username': username, }

    def __unicode__(self):
        return _('Podcast Configuration')

    class Meta:
        verbose_name = _('Podcast Configuration')
        verbose_name_plural = _('Podcast Configuration')


class CalendarConfiguration(SingletonModel):
    scroll_time = models.TimeField(default=datetime.time(0, 0, 0), verbose_name=_('scroll time'), help_text=_("Determines how far down the scroll pane is initially scrolled down."))
    first_day = models.IntegerField(choices=WEEKDAY_CHOICES, default=0, verbose_name=_('first day'), help_text=_('The day that the calendar begins'))
    min_time = models.TimeField(default=datetime.time(0, 0, 0), verbose_name=_('min time'), help_text=_("Determines the starting time that will be displayed, even when the scrollbars have been scrolled all the way up."))
    max_time = models.TimeField(default=datetime.time(23, 59, 59), verbose_name=_('max time'), help_text=_("Determines the end time (exclusively) that will be displayed, even when the scrollbars have been scrolled all the way down."))
    display_next_weeks = models.PositiveIntegerField(default=1, verbose_name=_("display next weeks"))

    def __unicode__(self):
        return _('Calendar Configuration')

    class Meta:
        verbose_name = _('Calendar Configuration')
        verbose_name_plural = _('Calendar Configuration')
