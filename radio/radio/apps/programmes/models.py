import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


SPANISH = "ES"
GALICIAN = "GA"
LANGUAGES = ((SPANISH, _("Spanish")),
    (GALICIAN, _("Galician")))


PRESENTER = 'PR'
INFORMER = 'IN'
CONTRIBUTOR = 'CO'
ROLES = ((CONTRIBUTOR, _("Contributor")),
    (PRESENTER, _("Presenter")),
    (INFORMER, _("Informer")))

class Programme(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("name"), help_text=_("please DON'T change this value. It's used to build URL's."))
    start_date = models.DateField(verbose_name=_('start date'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('end date'), help_text=_("This camp can be null."))
    announcers = models.ManyToManyField(User, blank=True, null=True, through='Role', verbose_name=_("announcers"))
    synopsis = models.TextField(blank=True, verbose_name=_("synopsis"))
    photo = models.ImageField(upload_to='photos/', default='/static/radio/images/default-programme-photo.jpg', verbose_name=_("photo"))
    language = models.CharField(verbose_name=_("language"), choices=LANGUAGES, max_length=2, default=SPANISH)
    current_season = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    slug = models.SlugField(max_length=100, unique=True)
    _runtime = models.PositiveIntegerField(validators=[MinValueValidator(1)])

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
            ("change_his_programme", "Can change some information"),
        )

    def get_absolute_url(self):
        return reverse('programmes:detail', args=[self.slug])

    def __unicode__(self):
        return self.name


class Episode(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("title"))
    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    schedule = models.ForeignKey('schedules.Schedule', blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("schedule"))
    summary = models.TextField(blank=True, verbose_name=_("summary"))
    issue_date = models.DateTimeField(verbose_name=_('issue date'))
    season = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_("season"))
    number_in_season = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_("No. in season"))
    # slug = models.SlugField(max_length=100)

    @classmethod
    def last_episode(cls, programme):
        try:
            return cls.objects.filter(programme=programme, season=programme.current_season).order_by('number_in_season').select_related('programme')[0]
        except:
            return None

    def clean(self):
        if self.schedule is None and  self.issue_date > datetime.datetime.now():
            raise ValidationError(_('schedule can\'t be null'))
        if self.schedule is not None and self.programme != self.schedule.programme:
            raise ValidationError(_('This schedule doesn\'t belong to the same programme'))

    def get_absolute_url(self):
        return reverse('programmes:episode_detail', args=[self.programme.slug, self.season, self.number_in_season])

    def save(self, *args, **kwargs):
        # self.slug = slugify(self.title)
        super(Episode, self).save(*args, **kwargs)

    class Meta:
        # unique_together = (('slug', 'programme'), ('season', 'number_in_season', 'programme'))
        unique_together = (('season', 'number_in_season', 'programme'))
        verbose_name = _('episode')
        verbose_name_plural = _('episodes')

    def __unicode__(self):
        return str(self.season) + 'x' + str(self.number_in_season) + ' ' + str(self.programme)


def model_created(sender, **kwargs):
    the_instance = kwargs['instance']
    if kwargs['created']:
        for role in Role.objects.filter(programme=the_instance.programme):
            Participant.objects.create(person=role.person, episode=the_instance, role=role.role, description=role.description)

post_save.connect(model_created, sender=Episode)


class Participant(models.Model):
    person = models.ForeignKey(User, verbose_name=_("person"))
    episode = models.ForeignKey(Episode, verbose_name=_("episode"))
    role = models.CharField(blank=True, null=True, verbose_name=_("role"), choices=ROLES, max_length=2)
    description = models.TextField(blank=True, verbose_name=_("description"))

    def clean(self):
        if self.role is None:
            try:
                p = Participant.objects.get(person=self.person, episode=self.episode, role__isnull=True)
                if p == self:
                    raise Exception()
            except:
                pass
            else:
                raise ValidationError(_('Already exist '))

    class Meta:
        unique_together = ('person', 'episode', 'role')
        verbose_name = _('participant')
        verbose_name_plural = _('participants')

    def __unicode__(self):
        return self.episode.title + ": " + self.person.username




class Role(models.Model):
    person = models.ForeignKey(User, verbose_name=_("person"))
    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    role = models.CharField(blank=True, null=True, verbose_name=_("role"), choices=ROLES, max_length=2)
    description = models.TextField(blank=True, verbose_name=_("description"))
    date_joined = models.DateField(auto_now_add=True)

    def clean(self):
        if self.role is None:
            try:
                r = Role.objects.get(person=self.person, programme=self.programme, role__isnull=True)
                if r == self:
                    raise Exception()
            except:
                pass
            else:
                raise ValidationError(_('Already exist '))
    class Meta:
        unique_together = ('person', 'programme', 'role')
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        permissions = (
            ("change_his_role", "Can change his role"),
        )

    def __unicode__(self):
        return self.programme.name + ": " + self.person.username

class Podcast(models.Model):
    episode = models.OneToOneField(Episode, primary_key=True)
