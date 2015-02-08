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
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch.dispatcher import receiver
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField


if hasattr(settings, 'PROGRAMME_LANGUAGES'):
    PROGRAMME_LANGUAGES = settings.PROGRAMME_LANGUAGES
else:
    PROGRAMME_LANGUAGES = settings.LANGUAGES


PRESENTER = 'PR'
INFORMER = 'IN'
CONTRIBUTOR = 'CO'
NOT_SPECIFIED = 'NO'

ROLES = ((NOT_SPECIFIED, _("Not specified")),
    (PRESENTER, _("Presenter")),
    (INFORMER, _("Informer")),
    (CONTRIBUTOR, _("Contributor")))


class Programme(models.Model):
    CATEGORY_CHOICES = (
        ('Arts', _('Arts')),
        ('Business', _('Business')),
        ('Comedy', _('Comedy')),
        ('Education', _('Education')),
        ('Games & Hobbies', _('Games & Hobbies')),
        ('Government & Organizations', _('Government & Organizations')),
        ('Health', _('Health')),
        ('Kids & Family', _('Kids & Family')),
        ('Music', _('Music')),
        ('News & Politics', _('News & Politics')),
        ('Religion & Spirituality', _('Religion & Spirituality')),
        ('Science & Medicine', _('Science & Medicine')),
        ('Society & Culture', _('Society & Culture')),
        ('Sports & Recreation', _('Sports & Recreation')),
        ('Technology', _('Technology')),
        ('TV & Film', _('TV & Film')),
    )

    name = models.CharField(max_length=100, unique=True, verbose_name=_("name"), help_text=_("Please DON'T change this value. It's used to build URL's."))
    start_date = models.DateField(verbose_name=_('start date'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('end date'), help_text=_("This field can be null."))
    announcers = models.ManyToManyField(User, blank=True, null=True, through='Role', verbose_name=_("announcers"))
    synopsis = RichTextField(blank=True, verbose_name=_("synopsis"))
    photo = models.ImageField(upload_to='photos/', default='/static/radio/images/default-programme-photo.jpg', verbose_name=_("photo"))
    language = models.CharField(default=PROGRAMME_LANGUAGES[0][0], verbose_name=_("language"), choices=map(lambda (k, v): (k, _(v)), PROGRAMME_LANGUAGES), max_length=7)
    current_season = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_("current season"))
    category = models.CharField(blank=True, null=True, max_length=50, choices=CATEGORY_CHOICES, verbose_name=_("category"))
    slug = models.SlugField(max_length=100, unique=True)
    _runtime = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_("runtime"), help_text=_("In minutes."))

    @property
    def runtime(self):
        return datetime.timedelta(minutes=self._runtime)

    @runtime.setter
    def runtime(self, value):
        self._runtime = value

    def clean(self):
        if self._runtime <= 0:
            raise ValidationError(_('Duration must be greater than 0.'))
        if self.end_date is not None and self.start_date > self.end_date:
            raise ValidationError(_('end date must be greater than or equal to start date.'))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        # rearrange episodes if dates has changed
        if self.pk is not None:
            orig = Programme.objects.get(pk=self.pk)
            if orig.start_date != self.start_date or orig.end_date != self.end_date:  # Field has changed
                super(Programme, self).save(*args, **kwargs)
                Episode.rearrange_episodes(programme=self, after=datetime.datetime.now())
            else:
                super(Programme, self).save(*args, **kwargs)
        else:
            super(Programme, self).save(*args, **kwargs)


    @classmethod
    def actives(cls, start_date, end_date=None):
        programme_list = cls.objects.filter(end_date__isnull=True).order_by('-start_date') | cls.objects.filter(end_date__gte=start_date).order_by('-start_date')
        if end_date:
            programme_list = programme_list.filter(start_date__lte=end_date)
        return programme_list

    class Meta:
        verbose_name = _('programme')
        verbose_name_plural = _('programmes')
        permissions = (
            ("see_all_programmes", "Can see all programmes"),
        )

    def get_absolute_url(self):
        return reverse('programmes:detail', args=[self.slug])

    def __unicode__(self):
        return u"%s" % (self.name)



class Episode(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("title"))
    people = models.ManyToManyField(User, blank=True, null=True, through='Participant', verbose_name=_("people"))
    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    summary = RichTextField(blank=True, verbose_name=_("summary"))
    # issue_date = models.DateTimeField(db_index=True, unique=True, verbose_name=_('issue date'))
    issue_date = models.DateTimeField(blank=True, null=True, db_index=True, verbose_name=_('issue date'))
    season = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_("season"))
    number_in_season = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_("No. in season"))
    # slug = models.SlugField(max_length=100)

    @property
    def runtime(self):
        return self.programme.runtime

    @property
    def issue_date_str(self):
        if self.issue_date:
            return str(self.issue_date)
        return str(None)

    @classmethod
    def create_episode(cls, date, programme, last_episode=None, episode=None):
        if not last_episode:
            last_episode = Episode.get_last_episode(programme)
        season = programme.current_season
        if last_episode and last_episode.season == season:
            number_in_season = last_episode.number_in_season + 1
        else:
            number_in_season = 1
        if episode:
            episode.programme = programme
            episode.issue_date = date
            episode.season = season
            episode.number_in_season = number_in_season
        else:
            episode = Episode(programme=programme, issue_date=date, season=season, number_in_season=number_in_season)
        episode.save()
        for role in Role.objects.filter(programme=programme):
            Participant.objects.create(person=role.person, episode=episode, role=role.role, description=role.description)
        return episode

    @classmethod
    def rearrange_episodes(cls, programme, after):
        # TODO: improve
        from radio.apps.schedules.models import Schedule
        next_episodes = Episode.objects.filter(issue_date__gte=after) | Episode.objects.filter(issue_date__isnull=True)
        if programme:
            next_episodes = next_episodes.filter(programme=programme)
        next_episodes = next_episodes.order_by('programme', 'season', 'number_in_season').select_related('programme')

        dt = after
        current_programme = None
        for episode in next_episodes:
            if current_programme != episode.programme:
                # reset dt if programme change
                current_programme = episode.programme
                dt = after
            if dt:
                schedule, date = Schedule.get_next_date(programme=episode.programme, after=dt)
                episode.issue_date = date
                if date:
                    dt = date + episode.runtime
                else:
                    dt = None
            else:
                episode.issue_date = None
            episode.save()
        '''
        print '########################'
        my_list_len = len(next_episodes) - 1
        for i in range(my_list_len, -1, -1):
            print next_episodes[i].issue_date
            print ' , '
            next_episodes[i].save()
        '''

    @classmethod
    def next_episodes(cls, programme, hour, after=None):
        # TODO: improve query
        if after == None:
            after = datetime.datetime.now()
        episodes = Episode.objects.filter(programme=programme, issue_date__gte=after).order_by('issue_date')
        next_episodes = []
        for episode in episodes:
            if episode.issue_date.time() == hour:
                next_episodes.append(episode)
        return next_episodes

    @classmethod
    def get_last_episode(cls, programme):
        return cls.objects.filter(programme=programme).order_by('-season', '-number_in_season').select_related('programme').first()

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
        permissions = (
            ("see_all_episodes", "Can see all episodes"),
        )

    def __unicode__(self):
        return u"%sx%s %s" % (self.season, self.number_in_season, self.programme)

'''
# participants added in post_save signal
def model_created(sender, **kwargs):
    the_instance = kwargs['instance']
    if kwargs['created']:
        for role in Role.objects.filter(programme=the_instance.programme):
            Participant.objects.create(person=role.person, episode=the_instance, role=role.role, description=role.description)

post_save.connect(model_created, sender=Episode)
'''

class Participant(models.Model):
    person = models.ForeignKey(User, verbose_name=_("person"))
    episode = models.ForeignKey(Episode, verbose_name=_("episode"))
    role = models.CharField(default=NOT_SPECIFIED, verbose_name=_("role"), choices=ROLES, max_length=2)
    description = models.TextField(blank=True, verbose_name=_("description"))

    class Meta:
        unique_together = ('person', 'episode', 'role')
        verbose_name = _('contributor')
        verbose_name_plural = _('contributors')
        permissions = (
            ("see_all_participants", "Can see all participants"),
        )

    def __unicode__(self):
        return str(self.episode) + ": " + self.person.username




class Role(models.Model):
    person = models.ForeignKey(User, verbose_name=_("person"))
    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    role = models.CharField(default=NOT_SPECIFIED, verbose_name=_("role"), choices=ROLES, max_length=2)
    description = models.TextField(blank=True, verbose_name=_("description"))
    date_joined = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('person', 'programme', 'role')
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        permissions = (
            ("see_all_roles", "Can see all roles"),
        )

    def __unicode__(self):
        return self.programme.name + ": " + self.person.username


class Podcast(models.Model):
    episode = models.OneToOneField(Episode, primary_key=True)
    url = models.CharField(max_length=2048)
    mime_type = models.CharField(max_length=20)
    length = models.PositiveIntegerField()  # bytes
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def get_absolute_url(self):
        return self.episode.get_absolute_url()


