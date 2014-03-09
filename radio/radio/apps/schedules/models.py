from datetime import date
import datetime

from dateutil import rrule
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from radio.apps.programmes.models import Programme


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




class Schedule(models.Model):
    programme = models.ForeignKey(Programme, verbose_name=_("programme"))
    day = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_hour = models.TimeField(verbose_name=_('start date'))
    type = models.CharField(verbose_name=_("type"), choices=emission_type, max_length=1)

    def runtime(self):
        return self.programme.runtime

    def __get_rrule(self):
        if self.programme.end_date is not None:
            return rrule.rrule(rrule.WEEKLY, byweekday=[self.day], dtstart=datetime.datetime.combine(self.programme.start_date, self.start_hour), until=self.programme.end_date)
        else:
            return rrule.rrule(rrule.WEEKLY, byweekday=[self.day], dtstart=datetime.datetime.combine(self.programme.start_date, self.start_hour))

    def dates_between(self, after, before):
        dates = self.__get_rrule().between(after, before, True)
        # add programme if this is not finished
        start_date = self.date_before(after)
        if start_date and start_date != after:
            if start_date + self.runtime() > after:
                dates.insert(0, start_date)
        return dates

    def date_before(self, dt):
        return self.__get_rrule().before(dt, True)

    def date_after(self, dt):
        return self.__get_rrule().after(dt, True)

    def clean(self, mock_now=None):
        now = datetime.datetime.now()
        if mock_now:
            now = mock_now
        # get the next emission date
        first_date_start = self.date_after(now)
        first_date_end = first_date_start + self.runtime()
        """
        last_date = None
        if self.programme.end_date():
            last_date = self.date_before(self.programme.end_date())

        programme_list = Programme.actives(first_date, last_date);
        for programme in programme_list:
            pass
        """
        schedules, dates_list_list = Schedule.between(first_date_start, first_date_end, self)
        index = 0
        if schedules:
            for date_list in dates_list_list:
                for date in date_list:
                    if date != first_date_end:
                        schedule = schedules[index]
                        start_date = date
                        end_date = start_date + schedule.runtime()
                        raise ValidationError(_('This settings collides with: %(name)s [%(start_date)s %(start_day)s/%(start_month)s/%(start_year)s \
                            - %(end_date)s %(end_day)s/%(end_month)s/%(end_year)s ]')
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
    def between(cls, after, before, exclude=None):
        list_schedules = cls.objects.filter(programme__start_date__lte=before, programme__end_date__isnull=True).order_by('-programme__start_date').select_related('programme') | cls.objects.filter(programme__start_date__lte=before, programme__end_date__gte=after).order_by('-programme__start_date').select_related('programme')
        dates = []
        schedules = []
        for schedule in list_schedules:
            if schedule != exclude:
                list_dates = schedule.dates_between(after, before)
                if list_dates:
                    schedules.append(schedule)
                    dates.append(list_dates)
        return schedules, dates

    @classmethod
    def schedule(cls, dt, exclude=None):
        list_schedules = cls.objects.filter(programme__start_date__lte=dt, programme__end_date__isnull=True).select_related('programme') | cls.objects.filter(programme__start_date__lte=dt, programme__end_date__gte=dt).select_related('programme')
        earlier_date = None
        earlier_schedule = None
        for schedule in list_schedules:
            if schedule != exclude:
                date = schedule.date_before(dt)
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


