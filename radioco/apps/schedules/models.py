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
import heapq
from functools import partial
from itertools import imap

from radioco.apps.programmes.models import Programme, Episode
from dateutil import rrule
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from recurrence.fields import RecurrenceField
import datetime
import django.utils.timezone


EMISSION_TYPE = (
    ("L", _("live")),
    ("B", _("broadcast")),
    ("S", _("broadcast syndication"))
)

MO = 0
TU = 1
WE = 2
TH = 3
FR = 4
SA = 5
SU = 6

WEEKDAY_CHOICES = (
    (MO, _('Monday')),
    (TU, _('Tuesday')),
    (WE, _('Wednesday')),
    (TH, _('Thursday')),
    (FR, _('Friday')),
    (SA, _('Saturday')),
    (SU, _('Sunday')),
)


class ScheduleBoardManager(models.Manager):
    # XXX get from global setting
    def current(self, date=None):
        if not date:
            date = datetime.date.today()

        current_board = (ScheduleBoard.objects
                  .order_by("-start_date")
                  .filter(
                      Q(start_date__lte=date, end_date__isnull=True) |
                      Q(start_date__lte=date, end_date__gte=date))
                  .first())
        return current_board


class ScheduleBoard(models.Model):
    class Meta:
        verbose_name = _('schedule board')
        verbose_name_plural = _('schedule board')

    name = models.CharField(max_length=255, unique=True, verbose_name=_("name"))
    slug = models.SlugField(max_length=255, unique=True)
    start_date = models.DateField(blank=True, null=True, verbose_name=_('start date'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('end date'))

    def clean(self):
        if self.start_date is None:
            return
        if self.end_date is None:
            return
        if self.start_date > self.end_date:
            raise ValidationError(
                _('end date must be greater than or equal to start date.'),
                code='date missmatch')

    def save(self, *args, **kwargs):
        import utils

        self.slug = slugify(self.name)

        # rearrange episodes
        if self.pk is not None:
            orig = ScheduleBoard.objects.get(pk=self.pk)
            if (orig.start_date == self.start_date and
                orig.end_date == self.end_date and
                orig.schedule_set == self.schedule_set):
                # no relevant fields have changed

                super(ScheduleBoard, self).save(*args, **kwargs)
                return

        super(ScheduleBoard, self).save(*args, **kwargs)
        # XXX filter unique programmes
        for schedule in self.schedule_set.all():
            utils.rearrange_episodes(
                schedule.programme, django.utils.timezone.now())

    def __unicode__(self):
        return u"%s" % (self.name)


@receiver(post_delete, sender=ScheduleBoard)
def delete_ScheduleBoard_handler(sender, **kwargs):
    import utils
    now = django.utils.timezone.now()
    for programme in Programme.objects.all():
        utils.rearrange_episodes(programme, now)


class Schedule(models.Model):
    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')

    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    type = models.CharField(verbose_name=_("type"), choices=EMISSION_TYPE, max_length=1)
    schedule_board = models.ForeignKey(ScheduleBoard, verbose_name=_("schedule board"))
    recurrences = RecurrenceField(verbose_name=_("recurrences"))
    source = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("source"),
        help_text=_("It is used when is a broadcast.")
    )

    @property
    def runtime(self):
        return self.programme.runtime

    @property
    def start(self):
        if not self.schedule_board.start_date:
            return self.rr_start
        else:
            start_date_board = datetime.datetime.combine(
                self.schedule_board.start_date, datetime.time(0))
        # XXX this does not make any sense
        if not self.rr_start:
            return start_date_board
        return max(start_date_board, self.rr_start)

    @start.setter
    def start(self, start_date):
        self.rr_start = start_date

    @property
    def end(self):
        if not self.schedule_board.end_date:
            return self.rr_end
        else:
            end_date_board = datetime.datetime.combine(
                self.schedule_board.end_date, datetime.time(23, 59, 59))
        if not self.rr_end:
            return end_date_board
        return min(end_date_board, self.rr_end)

    @property
    def rr_start(self):
        return self.recurrences.dtstart

    @rr_start.setter
    def rr_start(self, start_date):
        self.recurrences.dtstart = start_date

    @property
    def rr_end(self):
        return self.recurrences.dtend


    def dates_between(self, after, before):
        """
            Return a sorted list of dates between after and before
        """
        return self.recurrences.between(
            self._merge_after(after), self._merge_before(before), inc=True)

    def date_before(self, before):
        return self.recurrences.before(self._merge_before(before), inc=True)

    def date_after(self, after, inc=True):
        return self.recurrences.after(self._merge_after(after), inc)

    def save(self, *args, **kwargs):
        import utils
        super(Schedule, self).save(*args, **kwargs)
        utils.rearrange_episodes(self.programme, django.utils.timezone.now())

    def _merge_before(self, before):
        if not self.end:
            return before
        return min(before, self.end)

    def _merge_after(self, after):
        if not self.schedule_board.start_date:
            return after

        return max(after, datetime.datetime.combine(
            self.schedule_board.start_date, datetime.time(0)))

    def __unicode__(self):
        return ' - '.join([self.start.strftime('%A'), self.start.strftime('%X')])


# XXX entry point for transmission details (episode, recordings, ...)
class Transmission(object):
    def __init__(self, schedule, date):
        self.schedule = schedule
        self.start = date

    @property
    def programme(self):
        return self.schedule.programme

    @property
    def name(self):
        return self.programme.name

    @property
    def end(self):
        return self.start + self.schedule.runtime

    @property
    def slug(self):
        return self.programme.slug

    @property
    def url(self):
        return reverse('programmes:detail', args=[self.programme.slug])

    @classmethod
    def at(cls, at):
        # XXX filter board, filter schedule start / end
        schedules = Schedule.objects.all()
        for schedule in schedules:
            date = schedule.date_before(at)
            if date is None:
                continue
            if at < date + schedule.runtime:
                yield cls(schedule, date)

    @classmethod
    def between(cls, after, before, schedules=None):
        """
        Return a list of Transmissions sorted by date
        """
        if schedules is None:
            schedules = Schedule.objects.all()

        transmission_dates = [
            imap(partial(_return_tuple, item2=schedule), schedule.dates_between(after, before))
            for schedule in schedules
        ]
        sorted_transmission_dates = heapq.merge(*transmission_dates)
        for sorted_transmission_date, schedule in sorted_transmission_dates:
            yield cls(schedule, sorted_transmission_date)


def _return_tuple(item1, item2):
    return item1, item2

#def __get_events(after, before, json_mode=False):
#    background_colours = {"L": "#F9AD81", "B": "#C4DF9B", "S": "#8493CA"}
#    text_colours = {"L": "black", "B": "black", "S": "black"}
#
#    next_schedules, next_dates = Schedule.between(after=after, before=before)
#    schedules = []
#    dates = []
#    episodes = []
#    event_list = []
#    for x in range(len(next_schedules)):
#        for y in range(len(next_dates[x])):
#            # next_events.append([next_schedules[x], next_dates[x][y]])
#            schedule = next_schedules[x]
#            schedules.append(schedule)
#            date = next_dates[x][y]
#            dates.append(date)
#
#            episode = None
#            # if schedule == live
#            if next_schedules[x].type == 'L':
#                try:
#                    episode = Episode.objects.get(issue_date=date)
#                except Episode.DoesNotExist:
#                    pass
#            # broadcast
#            elif next_schedules[x].source:
#                try:
#                    source_date = next_schedules[x].source.date_before(date)
#                    if source_date:
#                        episode = Episode.objects.get(issue_date=source_date)
#                except Episode.DoesNotExist:
#                    pass
#            episodes.append(episode)
#
#            if episode:
#                url = reverse(
#                    'programmes:episode_detail',
#                    args=(schedule.programme.slug, episode.season, episode.number_in_season,)
#                )
#            else:
#                url = reverse('programmes:detail', args=(schedule.programme.slug,))
#
#            event_entry = {
#                'id': schedule.id,
#                'start': str(date),
#                'end': str(date + schedule.runtime),
#                'allDay': False,
#                'title':  schedule.programme.name,
#                'type': schedule.type,
#                'textColor': text_colours[schedule.type],
#                'backgroundColor': background_colours[schedule.type],
#                'url': url
#            }
#            event_list.append(event_entry)
#
#    if json_mode:
#        return event_list
#    else:
#        if schedules:
#            dates, schedules, episodes = (list(t) for t in zip(*sorted(zip(dates, schedules, episodes))))
#            return zip(schedules, dates, episodes)
#        return None
