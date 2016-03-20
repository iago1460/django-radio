from apps.programmes.models import Programme
from apps.schedules.models import Schedule, ScheduleBoard
from apps.schedules.models import MO, TU, WE, TH, FR, SA, SU
from django.test import TestCase
from rest_framework.test import APIClient
import datetime
import serializers


class TestSerializers(TestCase):
    def test_programme(self):
        serializer = serializers.ProgrammeSerializer()
        self.assertEqual(
            serializer.fields.keys(),
            ['url', 'slug', 'name', 'synopsis', 'photo', 'language', 'category'])


class TestAPI(TestCase):
    client_class = APIClient

    @classmethod
    def setUpTestData(cls):
        midnight_programme = Programme.objects.create(
            name="Programme 00:00 - 09:00",
            synopsis="This is a description",
            start_date=datetime.datetime(2014, 1, 1, 0, 0, 0, 0),
            end_date=datetime.datetime(2014, 1, 31, 12, 0, 0, 0),
            current_season=1, runtime=540)

        schedule_board = ScheduleBoard(
            name='Board', start_date=datetime.datetime(2014, 1, 1, 0, 0, 0, 0))
        schedule_board.save()

        start_hour = datetime.time(0, 0, 0)
        for day in (MO, TU, WE, TH, FR, SA, SU):
            Schedule.objects.create(
                programme=midnight_programme,
                day=day,
                start_hour=start_hour,
                type='L',
                schedule_board=schedule_board)

        programme = Programme.objects.create(
            name="Programme 09:00 - 10:00",
            synopsis="This is a description",
            start_date=datetime.datetime(2014, 1, 1),
            end_date=datetime.datetime(2014, 1, 31),
            current_season=1, runtime=60)

        for day in (MO, WE, FR):
            Schedule.objects.create(
                programme=programme,
                day=day,
                start_hour=datetime.time(9, 0, 0),
                type='L',
                schedule_board=schedule_board)

        programme = Programme.objects.create(
            name="Programme 10:00 - 12:00",
            synopsis="This is a description",
            start_date=datetime.datetime(2014, 1, 1),
            end_date=datetime.datetime(2014, 1, 31),
            current_season=1, runtime=120)

        for day in (MO, WE, FR):
            Schedule.objects.create(
                programme=programme,
                day=day,
                start_hour=datetime.time(10, 0, 0),
                type='L',
                schedule_board=schedule_board)


    def test_api(self):
        response = self.client.get('/api/2/')
        self.assertEqual(response.status_code, 200)

    def test_programmes_get_all(self):
        response = self.client.get('/api/2/programmes')
        self.assertEqual(response.status_code, 200)

    def test_programmes_post(self):
        response = self.client.post('/api/2/programmes')
        self.assertEqual(response.status_code, 405)

    def test_programmes_put(self):
        response = self.client.put('/api/2/programmes')
        self.assertEqual(response.status_code, 405)

    def test_programmes_delete(self):
        response = self.client.delete('/api/2/programmes')
        self.assertEqual(response.status_code, 405)

    def test_schedules_get(self):
        response = self.client.get('/api/2/schedules')
        self.assertEqual(response.status_code, 200)

    def test_schedules_post(self):
        response = self.client.post('/api/2/schedules')
        self.assertEqual(response.status_code, 405)
