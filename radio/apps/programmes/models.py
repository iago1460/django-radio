from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class Programme(models.Model):
    announcers = models.ManyToManyField(User, verbose_name=_("announcers"))
    name = models.CharField(max_length=100, unique=True, verbose_name=_("name"), help_text=_("please DON'T change this value. It's used to build URL's."))
    synopsis = models.TextField(blank=True, verbose_name=_("synopsis"))
    photo = models.ImageField(upload_to='photos/', default='/static/radio/images/default-programme-photo.jpg', verbose_name=_("photo"))
    slug = models.SlugField(max_length=100, unique=True)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Programme, self).save(*args, **kwargs)
    class Meta:
        verbose_name = _('programme')
        verbose_name_plural = _('programmes')
        ordering = ['name']
        permissions = (
            ("radio_change_synopsis", "Can change synopsis"),
        )
    def get_absolute_url(self):
        return reverse('programmes:detail', args=[self.slug])

    def __unicode__(self):
        return self.name

class Episode(models.Model):
    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    summary = models.TextField(blank=True, verbose_name=_("summary"))
    published = models.DateTimeField(verbose_name=_('published'))
    def get_absolute_url(self):
        return reverse('programmes:episode_detail', args=[self.programme.slug, str(self.id)])
    class Meta:
        verbose_name = _('episode')
        verbose_name_plural = _('episodes')
        permissions = (
            ("radio_change_summary", "Can change summary"),
        )
    def __unicode__(self):
        return self.programme.name
