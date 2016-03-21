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

from apps.programmes.models import Programme, Episode
from dateutil import rrule
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from recurrence.fields import RecurrenceField
import datetime


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
    start_date = models.DateField(blank=True, null=True, verbose_name=_('start date'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('end date'))

# XXX Form validation != model validation
#    def clean(self):
#        if self.start_date:
#            if self.end_date:
#                if self.start_date > self.end_date:
#                    raise ValidationError(_('end date must be greater than or equal to start date.'))
#                # check date collision
#                qs = (
#                    ScheduleBoard.objects.filter(start_date__lte=self.end_date, end_date__isnull=True) |
#                    ScheduleBoard.objects.filter(start_date__lte=self.end_date, end_date__gte=self.start_date)
#                )
#
#                if self.pk is not None:
#                    qs = qs.exclude(pk=self.pk)
#                if qs.exists():
#                    raise ValidationError(_('there is another object between this dates.'))
#
#            else:
#                # start_date != None and end_date == None only one can exist
#                qs = (
#                    ScheduleBoard.objects.filter(start_date__isnull=False, end_date__isnull=True) |
#                    ScheduleBoard.objects.filter(end_date__gte=self.start_date)
#                )
#                if self.pk is not None:
#                    qs = qs.exclude(pk=self.pk)
#                if qs.exists():
#                    raise ValidationError(_('there is another object without end_date'))
#                pass
#
#        elif self.end_date:
#            raise ValidationError(_('start date cannot be null if end date exists'))

    def save(self, *args, **kwargs):
        # rearrange episodes
        if self.pk is not None:
            orig = ScheduleBoard.objects.get(pk=self.pk)
            if orig.start_date != self.start_date or orig.end_date != self.end_date:  # Field has changed
                super(ScheduleBoard, self).save(*args, **kwargs)
                Episode.rearrange_episodes(programme=None, after=datetime.datetime.now())
            else:
                super(ScheduleBoard, self).save(*args, **kwargs)
        else:
            super(ScheduleBoard, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%s" % (self.name)


@receiver(post_delete, sender=ScheduleBoard)
def delete_ScheduleBoard_handler(sender, **kwargs):
    Episode.rearrange_episodes(programme=None, after=datetime.datetime.now())


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
            return self.recurrences.dtstart
        else:
            start_date_board = datetime.datetime.combine(
                self.schedule_board.start_date, datetime.time(0))
        if not self.recurrences.dtstart:
            return start_date_board
        return max(start_date_board, self.recurrences.dtstart)

    @start.setter
    def start(self, start_date):
        self.recurrences.dtstart = start_date

    @property
    def end(self):
        if not self.schedule_board.end_date:
            return self.recurrences.dtend
        else:
            end_date_board = datetime.datetime.combine(
                self.schedule_board.end_date, datetime.time(23, 59, 59))
        if not self.recurrences.dtend:
            return end_date_board
        return min(end_date_board, self.recurrences.dtend)

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

    def _merge_before(self, before):
        if not self.end:
            return before
        return min(before, self.end)

    def _merge_after(self, after):
        # XXX add date if the programme hasn't finished
        # after -= self.runtime

        if not self.schedule_board.start_date:
            return after

        return max(after, datetime.datetime.combine(
            self.schedule_board.start_date, datetime.time(0)))

#    def clean(self):
#        now = datetime.datetime.now()
#        if self.schedule_board.start_date:
#            dt = datetime.datetime.combine(self.schedule_board.start_date, datetime.time(0, 0))
#            if now > dt:
#                dt = now
#            # get the next emission date
#            first_date_start = self.date_after(dt)
#            if first_date_start:
#                first_date_end = first_date_start + self.runtime
#                schedules, dates_list_list = Schedule.between(
#                    after=first_date_start, before=first_date_end, exclude=self, schedule_board=self.schedule_board
#                )
#                index = 0
#                if schedules:
#                    for date_list in dates_list_list:
#                        for date in date_list:
#                            if date != first_date_end:
#                                schedule = schedules[index]
#                                start_date = date
#                                end_date = start_date + schedule.runtime()
#                                raise ValidationError(
#                                    _('This settings collides with: {name} [{start_date} - {end_date}]').format(
#                                        name=schedule.programme.name,
#                                        start_date=start_date.strftime("%H:%M %d/%m/%Y"),
#                                        end_date=end_date.strftime("%H:%M %d/%m/%Y")
#                                    )
#                                )
#                        index += 1

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
    def between(cls, after, before):
        # XXX filter board, filter schedule start / end
        schedules = Schedule.objects.all()
        for schedule in schedules:
            for date in schedule.dates_between(after, before):
                yield cls(schedule, date)

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
