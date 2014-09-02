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


from datetime import date
import datetime

from dateutil import rrule
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from radio.apps.programmes.models import Programme, Episode


emission_type = (("L", _("live")),
    ("B", _("broadcast")),
    ("S", _("broadcast syndication")))

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


class ScheduleBoard(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("name"))
    start_date = models.DateField(blank=True, null=True, verbose_name=_('start date'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('end date'))


    def clean(self):
        if self.start_date:
            if self.end_date:
                if self.start_date > self.end_date:
                    raise ValidationError(_('end date must be greater than or equal to start date.'))
                # check date collision
                qs = ScheduleBoard.objects.filter(start_date__lte=self.end_date, end_date__isnull=True) | ScheduleBoard.objects.filter(start_date__lte=self.end_date, end_date__gte=self.start_date)
                if self.pk is not None:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    raise ValidationError(_('there is another object between this dates.'))

            else:
                # start_date != None and end_date == None only one can exist
                qs = ScheduleBoard.objects.filter(start_date__isnull=False, end_date__isnull=True) | ScheduleBoard.objects.filter(end_date__gte=self.start_date)
                if self.pk is not None:
                    qs = qs.exclude(pk=self.pk)
                if qs.exists():
                    raise ValidationError(_('there is another object without end_date'))
                pass


        elif self.end_date:
            raise ValidationError(_('start date cannot be null if end date exists'))
        else:
            # both None = disable
            pass

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

    @classmethod
    def get_current(cls, dt):
        schedule_board = cls.objects.filter(start_date__lte=dt, end_date__isnull=True).order_by('-start_date') | cls.objects.filter(start_date__lte=dt, end_date__gte=dt).order_by('-start_date')
        return schedule_board.first()

    class Meta:
        verbose_name = _('schedule board')
        verbose_name_plural = _('schedule board')

    def __unicode__(self):
        return u"%s" % (self.name)


@receiver(post_delete, sender=ScheduleBoard)
def delete_ScheduleBoard_handler(sender, **kwargs):
    Episode.rearrange_episodes(programme=None, after=datetime.datetime.now())

class Schedule(models.Model):
    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    day = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_hour = models.TimeField(verbose_name=_('start time'))
    type = models.CharField(verbose_name=_("type"), choices=emission_type, max_length=1)
    schedule_board = models.ForeignKey(ScheduleBoard, verbose_name=_("schedule board"))
    source = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("source"), help_text=_("It is used when is a broadcast."))

    def runtime(self):
        return self.programme.runtime

    def __get_rrule(self):
        start_date = self.programme.start_date
        if self.schedule_board.start_date and start_date < self.schedule_board.start_date:
            start_date = self.schedule_board.start_date
        if self.programme.end_date:
            end_date = self.programme.end_date
            if self.schedule_board.end_date and end_date > self.schedule_board.end_date:
                end_date = self.schedule_board.end_date
            # Due to rrule we need to add 1 day
            end_date = end_date + datetime.timedelta(days=1)
            return rrule.rrule(rrule.WEEKLY, byweekday=[self.day], dtstart=datetime.datetime.combine(start_date, self.start_hour), until=end_date)
        else:
            end_date = self.schedule_board.end_date
            if end_date:
                # Due to rrule we need to add 1 day
                end_date = end_date + datetime.timedelta(days=1)
                return rrule.rrule(rrule.WEEKLY, byweekday=[self.day], dtstart=datetime.datetime.combine(start_date, self.start_hour), until=end_date)
            else:
                return rrule.rrule(rrule.WEEKLY, byweekday=[self.day], dtstart=datetime.datetime.combine(start_date, self.start_hour))

    def dates_between(self, after, before):
        '''
            Return a sorted list of dates between after and before
        '''
        dates = self.__get_rrule().between(after, before, True)
        # add date if the programme hasn't finished
        start_date = self.date_before(after)
        if start_date and start_date != after:
            if start_date + self.runtime() > after:
                dates.insert(0, start_date)
        return dates

    def date_before(self, dt):
        return self.__get_rrule().before(dt, True)

    def date_after(self, dt):
        return self.__get_rrule().after(dt, True)

    def clean(self):
        now = datetime.datetime.now()
        if self.schedule_board.start_date:
            dt = datetime.datetime.combine(self.schedule_board.start_date, datetime.time(0, 0))
            if now > dt:
                dt = now
            # get the next emission date
            first_date_start = self.date_after(dt)
            if first_date_start:
                first_date_end = first_date_start + self.runtime()
                """
                last_date = None
                if self.programme.end_date():
                    last_date = self.date_before(self.programme.end_date())
        
                programme_list = Programme.actives(first_date, last_date);
                for programme in programme_list:
                    pass
                """
                schedules, dates_list_list = Schedule.between(after=first_date_start, before=first_date_end, exclude=self, schedule_board=self.schedule_board)
                index = 0
                if schedules:
                    for date_list in dates_list_list:
                        for date in date_list:
                            if date != first_date_end:
                                schedule = schedules[index]
                                start_date = date
                                end_date = start_date + schedule.runtime()
                                raise ValidationError(_('This settings collides with: %(name)s [%(start_date)s %(start_day)s/%(start_month)s/%(start_year)s - %(end_date)s %(end_day)s/%(end_month)s/%(end_year)s ]')
                                                          % {'name': schedule.programme.name, 'start_date': start_date.strftime("%H:%M"), 'start_day': start_date.strftime("%d"),
                                                             'start_month': start_date.strftime("%m"), 'start_year': start_date.strftime("%Y"),
                                                             'end_date': end_date.strftime("%H:%M"), 'end_day': end_date.strftime("%d"), 'end_month': end_date.strftime("%m"), 'end_year': end_date.strftime("%Y"), })
                        index = index + 1

    def save(self, *args, **kwargs):
        # convert dates due MySQL
        # if timezone.is_aware(self.start_hour):
        #    self.start_hour = timezone.get_current_timezone().normalize(self.start_hour)
        super(Schedule, self).save(*args, **kwargs)


    @classmethod
    def between(cls, after, before, exclude=None, live=False, schedule_board=None):
        list_schedules = cls.objects.filter(programme__start_date__lte=before, programme__end_date__isnull=True) | cls.objects.filter(programme__start_date__lte=before, programme__end_date__gte=after)
        if live:
            list_schedules = list_schedules.filter(type='L')
        if schedule_board:
            list_schedules = list_schedules.filter(schedule_board=schedule_board)
        else:
            list_schedules = list_schedules.filter(schedule_board__start_date__lte=before, schedule_board__end_date__isnull=True) | list_schedules.filter(schedule_board__start_date__lte=before, schedule_board__end_date__gte=after)
        if exclude:
            list_schedules = list_schedules.exclude(id=exclude.id)
        list_schedules = list_schedules.order_by('-programme__start_date').select_related('programme', 'schedule_board', 'source__programme', 'source__schedule_board')

        dates = []
        schedules = []
        for schedule in list_schedules:
            list_dates = schedule.dates_between(after, before)
            if list_dates:
                schedules.append(schedule)
                dates.append(list_dates)
        return schedules, dates

    @classmethod
    def schedule(cls, dt, exclude=None):
        list_schedules = cls.objects.filter(programme__start_date__lte=dt, programme__end_date__isnull=True) | cls.objects.filter(programme__start_date__lte=dt, programme__end_date__gte=dt)
        if exclude:
            list_schedules = list_schedules.exclude(id=exclude.id)
        list_schedules = list_schedules.select_related('programme', 'schedule_board')
        earlier_date = None
        earlier_schedule = None
        for schedule in list_schedules:
            # if schedule != exclude:
            date = schedule.date_before(dt)
            if date and (earlier_date is None or date > earlier_date):
                earlier_date = date
                earlier_schedule = schedule
        if earlier_schedule is None or dt > earlier_date + earlier_schedule.runtime():  # Todo: check
            return None, None
        return earlier_schedule, earlier_date

    @classmethod
    def get_next_date(cls, programme, after):
        list_schedules = cls.objects.filter(programme=programme, type='L')
        list_schedules = list_schedules.filter(programme__end_date__isnull=True) | list_schedules.filter(programme__end_date__gte=after)
        list_schedules = list_schedules.filter(schedule_board__start_date__isnull=False, schedule_board__end_date__isnull=True) | list_schedules.filter(schedule_board__end_date__gte=after)
        # list_schedules = list_schedules.select_related('programme', 'schedule_board', 'source__programme', 'source__schedule_board')
        closer_date = None
        closer_schedule = None
        for schedule in list_schedules:
            # if schedule != exclude:
            date = schedule.date_after(after)
            if date and (closer_date is None or date < closer_date):
                closer_date = date
                closer_schedule = schedule
        if closer_schedule is None:  # Todo: check
            return None, None
        return closer_schedule, closer_date

    def __unicode__(self):
        return self.get_day_display() + ' - ' + self.start_hour.strftime('%H:%M')

    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')


