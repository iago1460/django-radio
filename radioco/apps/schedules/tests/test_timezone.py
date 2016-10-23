import datetime

import pytz
import recurrence
from django.test import TestCase

from radioco.apps.programmes.models import Programme
from radioco.apps.radio.tests import TestDataMixin
from radioco.apps.schedules.models import Schedule


SPAIN_TZ = pytz.timezone('Europe/Madrid')

BEFORE_CEST_TRANSITION = SPAIN_TZ.localize(datetime.datetime(2017, 3, 26, 1, 59, 59))  # CET+1:00:00
AFTER_CEST_TRANSITION = SPAIN_TZ.localize(datetime.datetime(2017, 3, 26, 3, 0, 0))  # CEST+2:00:00

BEFORE_CET_TRANSITION = SPAIN_TZ.localize(datetime.datetime(2017, 10, 29, 2, 59, 59), is_dst=True) # CEST+2:00:00
AFTER_CET_TRANSITION = SPAIN_TZ.localize(datetime.datetime(2017, 10, 29, 2, 0, 0), is_dst=False) # CET+1:00:00


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
        start_date = pytz.utc.localize(datetime.datetime(2015, 1, 1, 8, 0, 0))
        
        
        
        Schedule.objects.get_or_create(
            programme=programme,
            type='L',
            schedule_board=self.schedule_board,
            recurrences=recurrence.Recurrence(
                dtend=datetime.datetime(2014, 1, 31, 14, 0, 0),
                rrules=[recurrence.Rule(recurrence.WEEKLY)]
            ),
            start_date=SPAIN_TZ.localize(datetime.datetime(2017, 3, 26, 1, 30, 00)))

    def test_CET_transitions(self):
        assert BEFORE_CEST_TRANSITION == pytz.utc.localize(datetime.datetime(2017, 3, 26, 0, 59, 59))
        assert AFTER_CEST_TRANSITION == pytz.utc.localize(datetime.datetime(2017, 3, 26, 1, 0, 0))
        
        assert BEFORE_CET_TRANSITION == pytz.utc.localize(datetime.datetime(2017, 10, 29, 0, 59, 59))
        assert AFTER_CET_TRANSITION == pytz.utc.localize(datetime.datetime(2017, 10, 29, 1, 0, 0))
