from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    site_name = models.CharField(max_length=255, default='RadioCo', verbose_name=_("Site Name"))

    def __unicode__(self):
        return _('Global Configuration')

    class Meta:
        verbose_name = _('Global Configuration')
        verbose_name_plural = _('Global Configuration')



class PodcastConfiguration(SingletonModel):
    url_source = models.CharField(blank=True, default="", max_length=500, verbose_name=_("URL Source"))
    start_delay = models.PositiveIntegerField(default=0, verbose_name=_("start delay"), help_text=_("In seconds."))
    end_delay = models.PositiveIntegerField(default=0, verbose_name=_("end delay"), help_text=_("In seconds."))

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
