import datetime

from dateutil import rrule
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from radio.apps.programmes.models import Episode, Programme


emission_type = (("L", _("live")),
    ("B", _("broadcast")),
    ("S", _("broadcast syndication")))


class Schedule(models.Model):
    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    active = models.BooleanField(default=True, verbose_name=_("active"))
    start_date = models.DateTimeField(verbose_name=_('start date'))
    end_date = models.DateTimeField(verbose_name=_('end date'), help_text=_("The end time must be later than the start time."))
    type = models.CharField(verbose_name=_("type"), choices=emission_type, max_length=1)

    def next_dates(self, after, before):
        list = []
        try:
            if self.active:
                list = self.recurrence.ocurrences(dtstart=self.start_date, after=after, before=before)
        except Recurrence.DoesNotExist:
            pass
        if after <= self.start_date <= before and self.start_date not in list:
            list.insert(0, self.start_date)
        return list

    def before(self, dt):
        datetime = None
        try:
            if self.active:
                datetime = self.recurrence.before(dtstart=self.start_date, dt=dt)
        except Recurrence.DoesNotExist:
            pass
        if datetime:
            return datetime
        elif self.start_date <= dt:
            return self.start_date

    def clean(self):
        if self.start_date is None or self.end_date is None or self.start_date >= self.end_date:
            raise ValidationError(_('start date must be before end date.'))

        schedule, start_date = Schedule.schedule(self.start_date)
        if schedule is None or schedule == self or self.start_date == (start_date + schedule.runtime()):
            schedule, start_date = Schedule.schedule(self.start_date + self.runtime())

        if schedule and schedule != self and start_date != (self.start_date + self.runtime()):
            end_date = start_date + schedule.runtime()
            raise ValidationError(_('This settings collides with: %(name)s [%(start_date)s %(start_day)s/%(start_month)s/%(start_year)s \
            - %(end_date)s %(end_day)s/%(end_month)s/%(end_year)s ]')
                                  % {'name': schedule.programme.name, 'start_date': start_date.strftime("%H:%M"), 'start_day': start_date.strftime("%d"),
                                     'start_month': start_date.strftime("%m"), 'start_year': start_date.strftime("%Y"),
                                     'end_date': end_date.strftime("%H:%M"), 'end_day': end_date.strftime("%d"), 'end_month': end_date.strftime("%m"), 'end_year': end_date.strftime("%Y"), })

    def runtime(self):
        return self.end_date - self.start_date

    @classmethod
    def between(cls, after, before):
        list_schedules = cls.objects.filter(active=True, start_date__lte=before).order_by('-start_date').select_related('recurrence','programme')
        dates = []
        schedules = []
        for schedule in list_schedules:
            list_dates = schedule.next_dates(after, before)
            if list_dates:
                schedules.append(schedule)
                dates.append(list_dates)
        return schedules, dates

    @classmethod
    def schedule(cls, dt):
        list_schedules = cls.objects.filter(active=True, start_date__lte=dt).select_related('recurrence','programme')
        """
        if exclude and exclude in list_schedules:
            list_schedules = list_schedules.remove(exclude)
        """
        earlier_date = None
        earlier_schedule = None
        for schedule in list_schedules:
            date = schedule.before(dt)
            if date and (earlier_date is None or date > earlier_date):
                earlier_date = date
                earlier_schedule = schedule
        if earlier_schedule is None or dt > earlier_date + earlier_schedule.runtime():  # Todo: check
            return None, None
        return earlier_schedule, earlier_date

    def __unicode__(self):
        return self.programme.name

    class Meta:
        verbose_name = _('schedule')
        verbose_name_plural = _('schedules')
        ordering = ['start_date']


class Recurrence(models.Model):
    schedule = models.OneToOneField(Schedule, related_name='recurrence')
    repeat = models.BooleanField(default=False, verbose_name=_("Repeat?"))  # TODO:
    frequency_end_date = models.DateTimeField(blank=True, null=True, verbose_name=_('frequency end date'), help_text=_("This field can be null."))
    monday = models.BooleanField(default=False, verbose_name=_("Monday"))
    tuesday = models.BooleanField(default=False, verbose_name=_("Tuesday"))
    wednesday = models.BooleanField(default=False, verbose_name=_("Wednesday"))
    thursday = models.BooleanField(default=False, verbose_name=_("Thursday"))
    friday = models.BooleanField(default=False, verbose_name=_("Friday"))
    saturday = models.BooleanField(default=False, verbose_name=_("Saturday"))
    sunday = models.BooleanField(default=False, verbose_name=_("Sunday"))

    def __get_rrule(self, dtstart):
        day_list = []
        if self.monday:
            day_list.append(rrule.MO)
        if self.tuesday:
            day_list.append(rrule.TU)
        if self.wednesday:
            day_list.append(rrule.WE)
        if self.thursday:
            day_list.append(rrule.TH)
        if self.friday:
            day_list.append(rrule.FR)
        if self.saturday:
            day_list.append(rrule.SA)
        if self.sunday:
            day_list.append(rrule.SU)
        if (not day_list):
            day_list.append(dtstart.weekday())
        dtstart = timezone.get_current_timezone().normalize(dtstart)

        if self.frequency_end_date is not None:
            end_date = timezone.get_current_timezone().normalize(self.frequency_end_date)
            return rrule.rrule(rrule.WEEKLY, byweekday=day_list, dtstart=dtstart, until=end_date)
        else:
            return rrule.rrule(rrule.WEEKLY, byweekday=day_list, dtstart=dtstart)

    def ocurrences(self, dtstart, after, before):
        if not self.repeat:
            return []
        after = timezone.get_current_timezone().normalize(after)
        before = timezone.get_current_timezone().normalize(before)
        list = self.__get_rrule(dtstart).between(after, before, True)
        return list
        """
         dtstart = dtstart.replace(tzinfo=None)
        r = rrule.rrule(rrule.WEEKLY, byweekday=day_list, dtstart=dtstart)
        if before > self.frequency_end_date:
            before = self.frequency_end_date
        after = after.replace(tzinfo=None)
        before = before.replace(tzinfo=None)
        list = r.between(after, before, True)
        aware_list = []
        for dt in list:
            # now we must get back to aware datetime - since we are using naive (local) datetime,
            # we must convert it back to local timezone
            aware_list.append(dt.replace(tzinfo=timezone.utc).astimezone(timezone.get_current_timezone()))
        return aware_list
        """

    def before(self, dtstart, dt):
        if not self.repeat:
            return None
        dt = timezone.get_current_timezone().normalize(dt)
        return self.__get_rrule(dtstart).before(dt, True)

    def clean(self):
        if self.frequency_end_date is not None and self.frequency_end_date < self.schedule.end_date:
            raise ValidationError(_('start date must be before end date.'))

    class Meta:
            verbose_name = _('recurrence')
            verbose_name_plural = _('recurrences')

    def __unicode__(self):
        return self.schedule.programme.name

