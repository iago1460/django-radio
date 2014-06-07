from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    site_name = models.CharField(max_length=255, default='RadioCo', verbose_name=_("Site Name"))

    def __unicode__(self):
        return _('Global Configuration')

    class Meta:
        verbose_name = _('Global Configuration')
        verbose_name_plural = _('Global Configuration')



class PodcastConfiguration(SingletonModel):
    """
    iTunes - Compatible Audio File Types:
        .mp3    audio/mpeg
        .m4a    audio/x-m4a
    """
    MIME_CHOICES = (
        ("mp3", "audio/mpeg"),
        ("m4a", "audio/x-m4a"),
        ("ogg", "audio/ogg"),
        ("wav", "audio/wav"),
    )

    url_source = models.CharField(blank=True, null=True, max_length=500, verbose_name=_("URL Source"))
    mime = models.CharField(max_length=3, choices=MIME_CHOICES, default="mp3", verbose_name=_("mime format"))

    def __unicode__(self):
        return _('Podcast Configuration')

    class Meta:
        verbose_name = _('Podcast Configuration')
        verbose_name_plural = _('Podcast Configuration')
