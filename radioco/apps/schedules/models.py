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

import pytz
from recurrence.base import normalize_offset_awareness, localtz

from apps.radio.tz_utils import transform_datetime_tz, convert_date_to_datetime
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
    is_active = models.BooleanField(default=False)

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

    start_date = models.DateTimeField(verbose_name=_('start date'))

    end_date = models.DateTimeField(
        blank=True, null=True, verbose_name=_('end date'),
        help_text=_('This field is dynamically generated to improve performance')
    )

    from_collection = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL, related_name='child_schedules'
    )

    source = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("source"),
        help_text=_("It is used when is a broadcast.")
    )

    def save(self, *args, **kwargs):
        # FIXME: Saving clean dates in widget
        self.recurrences.rdates = [convert_date_to_datetime(_dt.date(), time=self.start_date.time()) for _dt in self.recurrences.rdates]
        self.recurrences.exdates = [convert_date_to_datetime(_dt.date(), time=self.start_date.time()) for _dt in self.recurrences.exdates]

        # Calculation of end_date to improve performance
        end_date = self.start_date + self.runtime
        rdates = [_dt for _dt in self.recurrences.rdates]
        rrules_until_dates = [_rrule.until for _rrule in self.recurrences.rrules]
        for date in rdates + rrules_until_dates:
            if not date:
                # We cannot know the end date of a recurrence because at least one rule doesn't have an end date
                end_date = None
                break
            # WARNING: Cleaning dates from field (issue with recurrence library)
            cleaned_date = convert_date_to_datetime(date.date(), time=self.start_date.time()) + self.runtime
            if cleaned_date > end_date:
                end_date = cleaned_date

        self.end_date = end_date

        import utils
        super(Schedule, self).save(*args, **kwargs)
        utils.rearrange_episodes(self.programme, django.utils.timezone.now())

    @property
    def runtime(self):
        return self.programme.runtime

    def date_is_excluded(self, dt):
        date = transform_datetime_tz(dt)
        for schedule in Schedule.objects.filter(programme=self.programme, type=self.type):
            if date in schedule.recurrences.exdates:
                return schedule
        return None

    def exclude_date(self, dt):
        date = transform_datetime_tz(dt)
        self.recurrences.exdates.append(date)

    def include_date(self, dt):
        date = transform_datetime_tz(dt)
        self.recurrences.exdates.remove(date)

    def has_recurrences(self):
        return self.recurrences

    # @property
    # def start(self):
    #     if not self.programme.start_date:
    #         return self.start_date
    #     start_date_board = datetime.datetime.combine(
    #         self.programme.start_date, datetime.time(0)
    #     )
    #     return max(start_date_board, self.start_date)
    #
    # @start.setter
    # def start(self, start_date):
    #     self.start_date = start_date

    @property
    def end(self):
        if not self.programme.end_date:
            return self.end_date
        end_date_board = datetime.datetime.combine(self.programme.end_date, datetime.time(23, 59, 59))
        if not self.end_date:
            return end_date_board
        else:
            return min(end_date_board, self.end_date)

    def dates_between(self, after, before):
        """
            Return a sorted list of dates between after and before
        """
        after_date = transform_datetime_tz(self._merge_after(after))
        before_date = transform_datetime_tz(self._merge_before(before))
        start_date = transform_datetime_tz(self.start_date)
        recurrence_dates_between = self.recurrences.between(after_date, before_date, inc=True, dtstart=start_date)
        for date in recurrence_dates_between:
            yield self._fix_datetime(date)

    def date_before(self, before): #FIXME: probably broken
        return self._fix_datetime(
            self.recurrences.before(self._merge_before(before), inc=True, dtstart=transform_datetime_tz(self.start_date))
        )

    def date_after(self, after, inc=True): #FIXME: probably broken
        return self._fix_datetime(
            self.recurrences.after(self._merge_after(after), inc, dtstart=transform_datetime_tz(self.start_date))
        )

    def _fix_datetime(self, dt): #FIXME
        """
        The recurrence library only work with dates, we need to add the correct time
        """
        return dt

    def _merge_before(self, before):
        """
        Return the smaller last date taking into account the programme constraints
        """
        if not self.end:
            return before
        return min(before, self.end)

    def _merge_after(self, after):
        """
        Return the greater first date taking into account the programme constraints
        """
        if not self.programme.start_date:
            return after
        programme_start_date = convert_date_to_datetime(self.programme.start_date, tz=pytz.utc)
        return max(after, programme_start_date)

    def __unicode__(self):
        return ' - '.join([self.start_date.strftime('%A'), self.start_date.strftime('%X')])


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
