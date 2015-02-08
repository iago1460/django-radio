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


import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _u
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token

from ckeditor.fields import RichTextField
from radio.apps.schedules.models import WEEKDAY_CHOICES


class SingletonModelManager(models.Manager):
    def get(self, *args, **kwargs):
        obj, created = super(SingletonModelManager, self).get_or_create(**kwargs)
        return obj

class SingletonModel(models.Model):
    objects = SingletonModelManager()

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_global(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        abstract = True


class SiteConfiguration(SingletonModel):
    site_name = models.CharField(max_length=255, default='RadioCo', verbose_name=_("Site Name"))
    footer = models.TextField(blank=True, default="", verbose_name=_("Footer"), help_text=_('Can contain raw HTML.'))

    def __unicode__(self):
        return _u('Global Configuration')

    class Meta:
        default_permissions = ('change',)
        verbose_name = _('Global Configuration')
        verbose_name_plural = _('Global Configuration')


class PodcastConfiguration(SingletonModel):
    url_source = models.CharField(blank=True, default="", max_length=500, verbose_name=_("URL Source"), help_text=_("The source url where the recordings will be available after the upload. For example: \"http://RadioCo.org/recordings/\""))
    start_delay = models.PositiveIntegerField(default=0, verbose_name=_("start delay"), help_text=_("In seconds. Initial delay of recordings"))
    end_delay = models.PositiveIntegerField(default=0, verbose_name=_("end delay"), help_text=_("In seconds."))
    next_events = models.PositiveIntegerField(default=32, verbose_name=_("next events"), help_text=_("In hours. The next events supplied to the recorder program"))

    @property
    def recorder_token(self):
        if hasattr(settings, 'USERNAME_RADIOCO_RECORDER'):
            username = settings.USERNAME_RADIOCO_RECORDER
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(User.objects.make_random_password())
                user.save()
            token, created = Token.objects.get_or_create(user=user)
            return token.key
        else:
            return _('Variable USERNAME_RADIOCO_RECORDER doesn\'t exist in your settings file')

    def __unicode__(self):
        # In django 1.7 we can't use lazy
        return _u('Podcast Configuration')

    class Meta:
        default_permissions = ('change',)
        verbose_name = _('Podcast Configuration')
        verbose_name_plural = _('Podcast Configuration')


class CalendarConfiguration(SingletonModel):
    scroll_time = models.TimeField(default=datetime.time(0, 0, 0), verbose_name=_('scroll time'), help_text=_("Determines how far down the scroll pane is initially scrolled down."))
    first_day = models.IntegerField(choices=WEEKDAY_CHOICES, default=0, verbose_name=_('first day'), help_text=_('The day that the calendar begins'))
    min_time = models.TimeField(default=datetime.time(0, 0, 0), verbose_name=_('min time'), help_text=_("Determines the starting time that will be displayed, even when the scrollbars have been scrolled all the way up."))
    max_time = models.TimeField(default=datetime.time(23, 59, 59), verbose_name=_('max time'), help_text=_("Determines the end time (exclusively) that will be displayed, even when the scrollbars have been scrolled all the way down."))

    def __unicode__(self):
        return _u('Calendar Configuration')

    class Meta:
        default_permissions = ('change',)
        verbose_name = _('Calendar Configuration')
        verbose_name_plural = _('Calendar Configuration')
