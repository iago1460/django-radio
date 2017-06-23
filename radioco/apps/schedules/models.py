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
import heapq
from functools import partial
from itertools import imap

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from recurrence.fields import RecurrenceField

from radioco.apps.programmes.models import Programme, Episode
from radioco.apps.radioco.tz_utils import transform_datetime_tz, fix_recurrence_dst, transform_dt_to_default_tz, \
    fix_recurrence_date, recurrence_after, recurrence_before

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


class CalendarManager(models.Manager):

    def current(self):
        return Calendar.objects.get(is_active=True)


class Calendar(models.Model):
    class Meta:
        verbose_name = _('calendar')
        verbose_name_plural = _('calendar')

    name = models.CharField(max_length=255, unique=True, verbose_name=_("name"))
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_active:
            active_calendars = Calendar.objects.filter(is_active=True)
            active_calendars.update(is_active=False)
            self.rearrange_episodes()
        super(Calendar, self).save(*args, **kwargs)

    def rearrange_episodes(self):
        now = timezone.now()
        for programme in Programme.objects.filter(Q(end_date__gte=now) | Q(end_date__isnull=True)):
            programme.rearrange_episodes(now, self)

    @classmethod
    def get_active(cls):
        try:
            return cls.objects.get(is_active=True)
        except Calendar.DoesNotExist:
            return None

    def __unicode__(self):
        return u"%s" % (self.name)

# We are not rearranging episodes during deletion


class ExcludedDates(models.Model):
    """
    Helper to improve performance
    """
    schedule = models.ForeignKey('Schedule')
    datetime = models.DateTimeField(db_index=True)

    @property
    def date(self):
        local_dt = transform_dt_to_default_tz(self.datetime)
        return local_dt.date()

    def get_new_excluded_datetime(self, new_dt):
        """
        Returns: A new dt to be excluded in that date
        """
        default_tz = timezone.get_default_timezone()
        new_dt_in_default_tz = transform_datetime_tz(new_dt, tz=default_tz)
        return default_tz.localize(datetime.datetime.combine(self.date, new_dt_in_default_tz.time()))


class Schedule(models.Model):
    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')

    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    type = models.CharField(verbose_name=_("type"), choices=EMISSION_TYPE, max_length=1)
    calendar = models.ForeignKey(Calendar, verbose_name=_("calendar"))
    recurrences = RecurrenceField(
        verbose_name=_("recurrences"),
        help_text=_("Excluded dates will appear in this list as result of dragging and dropping.")
    )

    start_dt = models.DateTimeField(verbose_name=_('start date'))

    effective_start_dt = models.DateTimeField(
        blank=True, null=True, verbose_name=_('first effective start date'),
        help_text=_('This field is dynamically generated to improve performance')
    )

    effective_end_dt = models.DateTimeField(
        blank=True, null=True, verbose_name=_('last effective end date'),
        help_text=_('This field is dynamically generated to improve performance')
    )

    from_collection = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL, related_name='child_schedules',
        help_text=_("Parent schedule (only happens when it is changed from recurrence.")
    )

    source = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("source"),
        help_text=_("Main schedule when (if this is a broadcast).")
    )

    def save(self, *args, **kwargs):
        assert self.start_dt, 'start_dt is required'
        self._update_recurrence_dates()

        # Do this every time to avoid users to delete/add exdates manually
        self._update_excluded_dates()

        self._update_effective_dates()

        super(Schedule, self).save(*args, **kwargs)

        self.programme.rearrange_episodes(timezone.now(), Calendar.get_active())

    def _update_recurrence_dates(self):
        """
        Fix for django-recurrence 1.3
        We need to update the internal until datetime to include the whole day
        """
        default_tz = timezone.get_default_timezone()
        for rrule in self.recurrences.rrules:
            if rrule.until:
                rrule.until = default_tz.localize(datetime.datetime.combine(
                    transform_dt_to_default_tz(rrule.until).date(),
                    datetime.time(23, 59, 59)))

    def _update_excluded_dates(self):
        """
        We need to update dates inside ExcludedDates and the recurrence library
        """
        exdates = []
        for excluded in ExcludedDates.objects.filter(schedule=self):
            new_excluded_dt = excluded.get_new_excluded_datetime(self.start_dt)
            excluded.datetime = new_excluded_dt
            excluded.save()
            exdates.append(fix_recurrence_date(self.start_dt, new_excluded_dt))
        self.recurrences.exdates = exdates

    def _update_effective_dates(self):
        # Start date has to be calculated first
        self.effective_start_dt = calculate_effective_schedule_start_dt(self)
        self.effective_end_dt = calculate_effective_schedule_end_dt(self)

    @property
    def runtime(self):
        return self.programme.runtime

    @staticmethod
    def get_schedule_which_excluded_dt(programme, dt):
        try:
            return ExcludedDates.objects.get(schedule__programme=programme, datetime=dt).schedule
        except ExcludedDates.DoesNotExist:
            return None

    def exclude_date(self, dt):
        local_dt = transform_dt_to_default_tz(dt)
        self.recurrences.exdates.append(fix_recurrence_date(self.start_dt, local_dt))
        ExcludedDates.objects.create(schedule=self, datetime=dt)

    def include_date(self, dt):
        local_dt = transform_dt_to_default_tz(dt)
        self.recurrences.exdates.remove(fix_recurrence_date(self.start_dt, local_dt))
        ExcludedDates.objects.get(schedule=self, datetime=dt).delete()

    def has_recurrences(self):
        return self.recurrences

    def dates_between(self, after, before):
        """
            Return a sorted list of dates between after and before
        """
        after_date = self._merge_after(after)
        if not after_date:
            return
        after_date = transform_dt_to_default_tz(after_date)
        before_date = transform_dt_to_default_tz(self._merge_before(before))
        start_dt = transform_dt_to_default_tz(self.start_dt)

        # We need to send the dates in the default timezone
        recurrence_dates_between = self.recurrences.between(after_date, before_date, inc=True, dtstart=start_dt)

        # Special case to include started episodes
        date_before = self.date_before(after_date)
        if date_before and date_before < after_date < date_before + self.runtime:
            yield date_before  # Date was already fixed

        for date in recurrence_dates_between:
            yield fix_recurrence_dst(date)  # Fixing date

    def date_before(self, before):
        before_date = transform_dt_to_default_tz(self._merge_before(before))
        start_dt = transform_dt_to_default_tz(self.start_dt)
        date = recurrence_before(self.recurrences, before_date, start_dt)
        return fix_recurrence_dst(date)

    def date_after(self, after):
        after_date = self._merge_after(after)
        if not after_date:
            return
        after_date = transform_dt_to_default_tz(after_date)
        start_dt = transform_dt_to_default_tz(self.start_dt)
        date = recurrence_after(self.recurrences, after_date, start_dt)
        return fix_recurrence_dst(date)

    def _merge_after(self, after):
        """
        Return the greater first date taking into account the programme constraints
        Can return None if there is no effective_start_dt
        """
        if not self.effective_start_dt:
            return None
        return max(after, self.effective_start_dt)

    def _merge_before(self, before):
        """
        Return the smaller last date taking into account the programme constraints
        """
        if not self.effective_end_dt:
            return before
        return min(before, self.effective_end_dt)

    def __unicode__(self):
        return ' - '.join([self.start_dt.strftime('%A'), self.start_dt.strftime('%X')])


def calculate_effective_schedule_start_dt(schedule):
    """
    Calculation of the first start date to improve performance
    """
    programme_start_dt = schedule.programme.start_dt
    programme_end_dt = schedule.programme.end_dt

    # If there are no rrules
    if not schedule.has_recurrences():
        if programme_start_dt and programme_start_dt > schedule.start_dt:
            return None
        if programme_end_dt and schedule.start_dt > programme_end_dt:
            return None
        return schedule.start_dt

    # Get first date
    after_dt = schedule.start_dt
    if programme_start_dt:
        after_dt = max(schedule.start_dt, programme_start_dt)
    first_start_dt = fix_recurrence_dst(recurrence_after(
        schedule.recurrences, transform_dt_to_default_tz(after_dt), transform_dt_to_default_tz(schedule.start_dt)))
    if first_start_dt:
        if programme_end_dt and programme_end_dt < first_start_dt:
            return None
        return first_start_dt
    return None


def calculate_effective_schedule_end_dt(schedule):
    """
    Calculation of the last end date to improve performance
    """
    programme_start_dt = schedule.programme.start_dt
    programme_end_dt = schedule.programme.end_dt

    # If there are no rrules
    if not schedule.has_recurrences():
        if not schedule.effective_start_dt:
            # WARNING: this depends on effective_start_dt
            return None  # returning None if there is no effective_start_dt
        return schedule.start_dt + schedule.runtime

    # If we have a programme restriction
    if programme_end_dt:
        last_effective_start_date = fix_recurrence_dst(recurrence_before(
            schedule.recurrences, transform_dt_to_default_tz(programme_end_dt), transform_dt_to_default_tz(schedule.start_dt)))
        if last_effective_start_date:
            if programme_start_dt and programme_start_dt > last_effective_start_date:
                return None
            return last_effective_start_date + schedule.runtime

    rrules_until_dates = [_rrule.until for _rrule in schedule.recurrences.rrules]

    # If we have a rrule without a until date we don't know the last date
    if any(map(lambda x: x is None, rrules_until_dates)):
        return None

    possible_limit_dates = schedule.recurrences.rdates + rrules_until_dates
    if not possible_limit_dates:
        return None

    # Get the biggest possible start_date. It could be that the biggest date is excluded
    biggest_date = max(possible_limit_dates)
    last_effective_start_date = schedule.recurrences.before(
        transform_dt_to_default_tz(biggest_date), True, dtstart=transform_dt_to_default_tz(schedule.start_dt))
    if last_effective_start_date:
        if programme_start_dt and programme_start_dt > last_effective_start_date:
            return None
        return fix_recurrence_dst(last_effective_start_date) + schedule.runtime
    return None


class Transmission(object):
    """
    Temporal object generated according to recurrence rules or schedule information
    It contains concrete dates
    """
    def __init__(self, schedule, date, episode=None):
        self.schedule = schedule
        self.programme = schedule.programme
        self.start = date
        self.episode = episode

    @property
    def name(self):
        return self.programme.name

    @property
    def slug(self):
        return self.programme.slug

    @property
    def end(self):
        return self.start + self.programme.runtime

    @property
    def programme_url(self):
        return reverse('programmes:detail', args=[self.programme.slug])

    @property
    def episode_url(self):
        if not self.episode:
            return None
        return reverse(
            'programmes:episode_detail',
            args=(self.slug, self.episode.season, self.episode.number_in_season)
        )

    @classmethod
    def at(cls, at):
        schedules = Schedule.objects.filter(
            calendar__is_active=True, effective_start_dt__lte=at
        ).filter(
            Q(effective_end_dt__gt=at) |
            Q(effective_end_dt__isnull=True)
        ).select_related('programme')
        for schedule in schedules:
            date = schedule.date_before(at)
            if date and date <= at < date + schedule.runtime:
                # Get episode
                try:
                    episode = Episode.objects.get(issue_date=date)
                except Episode.DoesNotExist:
                    episode = None
                # yield transmission
                yield cls(schedule, date, episode)

    @classmethod
    def between(cls, after, before, schedules=None):
        """
        Return a tuple of Schedule and Transmissions sorted by date
        """
        if schedules is None:
            schedules = Schedule.objects.filter(calendar__is_active=True)

        schedules = schedules.filter(
            effective_start_dt__lt=before
        ).filter(
            Q(effective_end_dt__gt=after) |
            Q(effective_end_dt__isnull=True)
        ).select_related('programme')

        # Querying episodes episodes in that period of time
        episodes = Episode.objects.filter(
            issue_date__lt=before, issue_date__gte=after
        )
        episodes = {_episode.issue_date: _episode for _episode in episodes}

        transmission_dates = [
            imap(partial(_return_tuple, item2=schedule), schedule.dates_between(after, before))
            for schedule in schedules
        ]
        sorted_transmission_dates = heapq.merge(*transmission_dates)
        for sorted_transmission_date, schedule in sorted_transmission_dates:
            # Adding episodes matching by date, we don't care about if this info is not correct
            yield cls(schedule, sorted_transmission_date, episodes.get(sorted_transmission_date))


def _return_tuple(item1, item2):
    return item1, item2
