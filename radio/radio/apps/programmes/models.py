import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


languages = (("ES", _("Spanish")),
    ("GA", _("Galician")))


class Programme(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("name"), help_text=_("please DON'T change this value. It's used to build URL's."))
    start_date = models.DateField(verbose_name=_('start date'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('end date'), help_text=_("This camp can be null."))
    announcers = models.ManyToManyField(User, blank=True, null=True, verbose_name=_("announcers"))
    synopsis = models.TextField(blank=True, verbose_name=_("synopsis"))
    photo = models.ImageField(upload_to='photos/', default='/static/radio/images/default-programme-photo.jpg', verbose_name=_("photo"))
    language = models.CharField(verbose_name=_("language"), choices=languages, max_length=2)
    slug = models.SlugField(max_length=100, unique=True)
    _runtime = models.PositiveIntegerField()

    @property
    def runtime(self):
        return datetime.timedelta(minutes=self._runtime)

    @runtime.setter
    def runtime(self, value):
        self._runtime = value

    def clean(self):
        if self._runtime <= 0:
            raise ValidationError(_('Duration must be greater than 0.'))
        if self.end_date is not None and self.start_date >= self.end_date:
            raise ValidationError(_('start date must be before end date.'))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Programme, self).save(*args, **kwargs)


    @classmethod
    def actives(cls, start_date, end_date=None):
        if end_date:
            return cls.objects.filter(start_date__lte=end_date, end_date__isnull=True).order_by('-start_date') | cls.objects.filter(start_date__lte=end_date, end_date__gte=start_date).order_by('-start_date')
        else:
            return cls.objects.filter(end_date__isnull=True).order_by('-start_date').select_related('programme') | cls.objects.filter(end_date__gte=start_date).order_by('-start_date')

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


class Podcast(models.Model):
    episode = models.OneToOneField(Episode, primary_key=True)
