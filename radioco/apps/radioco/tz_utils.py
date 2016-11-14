import datetime

from dateutil.tz import tzoffset
from django.utils import timezone

from radioco.apps.radioco.utils import memorize

timestamp = datetime.datetime(2009, 1, 1)  # any unambiguous timestamp will work here


class GMT(tzoffset):
    """UTC

    Optimized UTC implementation. It unpickles using the single module global
    instance defined beneath this class declaration.
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

# def transform_datetime_tz_to_fixed_tz(dt, time=None, tz=None):
#     """
#     Transform a datetime in other timezone to the current one
#     """
#     if not tz:
#         tz = timezone.get_current_timezone()
#     dst_tz_naive = tzoffset(None, get_timezone_offset(tz))
#
#     if time:
#         return timezone.make_aware(datetime.datetime.combine(dt.date(), time), timezone=dst_tz_naive)
#
#     return dt.astimezone(dst_tz_naive)


def convert_date_to_datetime(date, time=datetime.time(0), tz=None):
    """
    Transform a date into a timezone aware datetime taking into account the current timezone
    Returns: A datetime in the timezone provided or in the current timezone by default
    """
    if tz:
        return tz.normalize(timezone.make_aware(datetime.datetime.combine(date, time)).astimezone(tz))
    return timezone.make_aware(datetime.datetime.combine(date, time))


def transform_dt_checking_dst(dt): # TODO Maybe not necessary
    dst_tz = timezone.get_default_timezone()  # Timezone in settings.py
    tz = timezone.get_current_timezone()  # Timezone in current use
    dst_offset = dt.astimezone(dst_tz).dst()
    if dst_offset:  # If dst return a date plus the offset
        return tz.normalize((dt + dst_offset).astimezone(tz))
    return tz.normalize(dt.astimezone(tz))


def fix_recurrence_dst(dt, requested_tz=None):
    """
    Function to fix a datetime tz aware with an incorrect offset
    Returns: A datetime tz aware in the new time
    """
    if dt:
        tz = dt.tzinfo
        fixed_dt = tz.localize(datetime.datetime.combine(dt.date(), dt.time()))
        if requested_tz:
            fixed_dt = transform_datetime_tz(fixed_dt, requested_tz)
        return fixed_dt
    return None


def fix_dst_tz(dt, start_dt): #TODO
    # if dt.tzinfo == pytz.UTC:
    #     return dt # the date was already cleaned? FIXME problem when start_date changes

    dst_tz = start_dt.tzinfo
    dst_offset = dt.astimezone(dst_tz).dst()
    start_dst_offset = start_dt.dst()
    if dst_offset and not start_dst_offset:  # If dst return a date plus the offset
        # FIXME there is no solution, every time we are going to incremet this
        return tz.normalize((dt + dst_offset).astimezone(tz))

    return tz.localize(datetime.datetime.combine(dt.date(), dt.time()))


# def transform_dt_according_to_dst(dt):
#     """
#     Return a datetime adding the DST offset if the start_date was created in DST
#     :return:
#     """
#
#     dst_tz = timezone.get_default_timezone()  # Timezone in settings.py
#     tz = dt.tzinfo
#     dst_offset = dt.astimezone(dst_tz).dst()
#     if dst_offset:
#         return tz.normalize(dt + dst_offset)
#     return dt

# def transform_dt_according_to_dst(dt, start_date):
#     """
#     Return a datetime adding the DST offset if the start_date was created in DST
#     :return:
#     """
#
#     dst_tz = timezone.get_default_timezone()  # Timezone in settings.py
#     # tz = timezone.get_current_timezone()  # Timezone in current use
#     date = dt.astimezone(dst_tz)
#     start_dst_offset = start_date.astimezone(dst_tz).dst()
#     date_dst_offset = date.astimezone(dst_tz).dst()
#     if start_dst_offset:
#         if not date_dst_offset:  # If start_date was created in summer but this date is not
#             return dst_tz.normalize(date - start_dst_offset)
#     elif date_dst_offset:  # If start_date wasn't created in summer but this date is in summer
#         return dst_tz.normalize(date + start_dst_offset)
#     return dst_tz.normalize(date)
