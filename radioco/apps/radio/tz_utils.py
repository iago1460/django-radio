import datetime

import pytz
from django.utils import timezone


def transform_datetime_tz(dt, tz=None):
    """
    Transform a datetime in other timezone to the current one
    """
    if not tz:
        tz = timezone.get_current_timezone()
    return dt.astimezone(tz)


def convert_date_to_datetime(date, time=datetime.time(0), tz=None):
    """
    Transform a date into a timezone aware datetime taking into account the current timezone
    """
    if not tz:
        tz = timezone.get_current_timezone()
    return timezone.make_aware(datetime.datetime.combine(date, time)).astimezone(tz)
