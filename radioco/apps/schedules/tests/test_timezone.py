import datetime

import pytz
import recurrence
from django.test import TestCase
from django.test import override_settings

from radioco.apps.radioco.tz_utils import transform_dt_to_default_tz
from radioco.apps.programmes.models import Programme
from radioco.apps.radioco.tests import TestDataMixin, SPAIN_TZ
from radioco.apps.schedules.models import Schedule


BEFORE_CEST_TRANSITION = SPAIN_TZ.localize(datetime.datetime(2017, 3, 26, 1, 59, 59))  # CET+1:00:00
AFTER_CEST_TRANSITION = SPAIN_TZ.localize(datetime.datetime(2017, 3, 26, 3, 0, 0))  # CEST+2:00:00

BEFORE_CET_TRANSITION = SPAIN_TZ.localize(datetime.datetime(2017, 10, 29, 2, 59, 59), is_dst=True)  # CEST+2:00:00
AFTER_CET_TRANSITION = SPAIN_TZ.localize(datetime.datetime(2017, 10, 29, 2, 0, 0), is_dst=False)  # CET+1:00:00


def test_CET_transitions(self):
    assert BEFORE_CEST_TRANSITION == pytz.utc.localize(datetime.datetime(2017, 3, 26, 0, 59, 59))
    assert AFTER_CEST_TRANSITION == pytz.utc.localize(datetime.datetime(2017, 3, 26, 1, 0, 0))

    assert BEFORE_CET_TRANSITION == pytz.utc.localize(datetime.datetime(2017, 10, 29, 0, 59, 59))
    assert AFTER_CET_TRANSITION == pytz.utc.localize(datetime.datetime(2017, 10, 29, 1, 0, 0))


@override_settings(TIME_ZONE='Europe/Madrid')
# @mock.patch('django.utils.timezone.get_default_timezone', spain_tz)
# @mock.patch('django.utils.timezone.get_current_timezone', spain_tz)
class ScheduleModelTests(TestDataMixin, TestCase):

    def setUp(self):
        synopsis = '''
             This programme has complex schedules to test timezone changes.
             Only active between March and October 2017
         '''
        programme, created = Programme.objects.get_or_create(
            name='Timezone', defaults={
                'synopsis': synopsis,
                'language': 'en',
                'photo': 'defaults/example/radio_1.jpg',
                'current_season': 1,
                'category': 'News & Politics',
                '_runtime': 60,
                'start_date': datetime.date(2017, 3, 1),
                'end_date': datetime.date(2017, 10, 31),
            }
        )
        self.cest_schedule, created = Schedule.objects.get_or_create(
            programme=programme,
            type='L',
            calendar=self.calendar,
            recurrences=recurrence.Recurrence(
                rrules=[recurrence.Rule(
                    recurrence.DAILY, until=SPAIN_TZ.localize(datetime.datetime(2017, 3, 27)))]
            ),
            start_dt=SPAIN_TZ.localize(datetime.datetime(2017, 3, 25, 10, 00, 00)))

        self.cet_schedule, created = Schedule.objects.get_or_create(
            programme=programme,
            type='L',
            calendar=self.calendar,
            recurrences=recurrence.Recurrence(
                rrules=[recurrence.Rule(recurrence.DAILY)],
            ),
            start_dt=SPAIN_TZ.localize(datetime.datetime(2017, 10, 28, 14, 00, 00)))

    def test_transform_dt_to_default_tz(self):
        utc_dt = pytz.utc.localize(datetime.datetime(2017, 1, 1, 0, 00, 00))
        spain_dt = transform_dt_to_default_tz(utc_dt)
        self.assertEquals(spain_dt.tzinfo.zone, 'Europe/Madrid')
        self.assertEquals(spain_dt, SPAIN_TZ.localize(datetime.datetime(2017, 1, 1, 1, 0, 0)))

    def test_cleaned_internal_recurrence_dates(self):
        self.assertEquals(
            self.cest_schedule.recurrences.rrules[0].until,
            SPAIN_TZ.localize(datetime.datetime(2017, 3, 27, 23, 59, 59)))

    def test_CEST_transition(self):
        after = SPAIN_TZ.localize(datetime.datetime(2017, 2, 1, 0, 0, 00))
        before = SPAIN_TZ.localize(datetime.datetime(2017, 11, 30, 0, 0, 00))

        dates_between = self.cest_schedule.dates_between(after, before)

        expected_dates = (
            SPAIN_TZ.localize(datetime.datetime(2017, 3, 25, 10, 0, 0)),
            SPAIN_TZ.localize(datetime.datetime(2017, 3, 26, 10, 0, 0)),
            SPAIN_TZ.localize(datetime.datetime(2017, 3, 27, 10, 0, 0)),
        )
        self.assertItemsEqual(expected_dates, dates_between)

    def test_CET_transition(self):
        after = SPAIN_TZ.localize(datetime.datetime(2017, 10, 28, 14, 0, 0))
        before = SPAIN_TZ.localize(datetime.datetime(2017, 10, 30, 14, 0, 0))

        dates_between = self.cet_schedule.dates_between(after, before)

        expected_dates = (
            SPAIN_TZ.localize(datetime.datetime(2017, 10, 28, 14, 0, 0)),
            SPAIN_TZ.localize(datetime.datetime(2017, 10, 29, 14, 0, 0)),
            SPAIN_TZ.localize(datetime.datetime(2017, 10, 30, 14, 0, 0)),
        )
        self.assertItemsEqual(expected_dates, dates_between)