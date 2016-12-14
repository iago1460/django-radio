import datetime

import pytz
from dateutil.tz import tzoffset
from django.utils import timezone

from radioco.apps.radioco.utils import memorize

timestamp = datetime.datetime(2009, 1, 1)  # any unambiguous timestamp will work here


class GMT(tzoffset):
    """
    GMT implementation, it has a fixed offset
    """

    def __init__(self, seconds):
        hours = int(seconds / 3600)
        if hours < 0:
            self._name = 'GMT-%s' % abs(hours)
        else:
            self._name = 'GMT+%s' % hours
        self._offset = datetime.timedelta(seconds=seconds)

    def localize(self, dt, is_dst=False):
        '''Convert naive time to local time'''
        if dt.tzinfo is not None:
            raise ValueError('Not naive datetime (tzinfo is already set)')
        return dt.replace(tzinfo=self)

    def normalize(self, dt, is_dst=False):
        '''Correct the timezone information on the given datetime'''
        if dt.tzinfo is self:
            return dt
        if dt.tzinfo is None:
            raise ValueError('Naive time - no tzinfo set')
        return dt.astimezone(self)

    def __repr__(self):
        return '<%s>' % self._name

    def __str__(self):
        return '%s' % self._name


@memorize
def get_timezone_offset(tz):
    return GMT((tz.utcoffset(timestamp) - tz.dst(timestamp)).total_seconds())


def get_active_timezone():
    """
    Same method as timezone.get_current_timezone but returning utc if nothing was set
    """
    return getattr(timezone._active, "value", pytz.utc)


def transform_datetime_tz(dt, tz=None):
    """
    Transform a datetime in other timezone to the current one
    """
    if not tz:
        tz = timezone.get_current_timezone()
    return tz.normalize(dt.astimezone(tz))


def transform_dt_to_default_tz(dt):
    """
    Transform a datetime in other timezone to the current one
    """
    tz = timezone.get_default_timezone()
    return tz.normalize(dt.astimezone(tz))


def fix_recurrence_date(start_dt, dt):
    """
    Fix for django-recurrence 1.3
    rdates and exdates needs a datetime, we are combining the date with the time from start_date.

    Return: A datetime in the default timezone with the offset required to work in the recurrence
    """
    current_dt = transform_dt_to_default_tz(dt)
    current_start_dt = transform_dt_to_default_tz(start_dt)

    tz = GMT(current_start_dt.utcoffset().total_seconds())  # tz without DST
    # We are localising a new dt in the DST naive tz
    fixed_dt = transform_dt_to_default_tz(
        tz.localize(datetime.datetime.combine(current_dt.date(), current_start_dt.time())))
    return fixed_dt


def fix_recurrence_dst(dt):
    """
    Fix for django-recurrence 1.3
    Function to fix a datetime tz aware with an incorrect offset

    Returns: A datetime in the same timezone but with the offset fixed
    """
    if dt:
        tz = dt.tzinfo
        return tz.localize(datetime.datetime.combine(dt.date(), dt.time()))
    return None
