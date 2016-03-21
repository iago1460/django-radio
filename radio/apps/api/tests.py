from apps.programmes.models import Programme, Episode
from apps.radio.tests import TestDataMixin
from apps.schedules.models import ScheduleBoard, Schedule, Transmission
from apps.schedules.models import WE
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
import datetime
import mock
import serializers
import views


def mock_now():
    return datetime.datetime(2015, 1, 6, 14, 30, 0)


class TestSerializers(TestDataMixin, TestCase):
    def test_programme(self):
        serializer = serializers.ProgrammeSerializer(self.programme)
        self.assertEqual(
            serializer.fields.keys(),
            ['id', 'url', 'name', 'synopsis', 'runtime',
             'photo', 'language', 'category'])

    def test_schedule(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        self.assertDictEqual(serializer.data, {
            'end': None, 'title': u'Classic hits',
            'start': datetime.datetime(2015, 1, 1, 14, 0), 'source': None,
            'backgroundColor': '#F9AD81', 'schedule_board': 1,
            'textColor': 'black', 'type': 'L', 'id': 5, 'programme': 5})

    def test_transmission(self):
        serializer = serializers.TransmissionSerializer(Transmission(
            self.schedule, datetime.datetime(2015, 1, 6, 14, 0, 0)))
        self.assertDictEqual(serializer.data, {
            'start': '2015-01-06T14:00:00',
            'end': '2015-01-06T15:00:00',
            'name': u'Classic hits',
            'slug': u'classic-hits',
            'url': u'/programmes/classic-hits/'})


class TestViews(TestDataMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmission_list(self):
        view = views.TransmissionViewSet()
        response = view.list(self.factory.get('/'))
        self.assertIsNotNone(response.data)

    @mock.patch('django.utils.timezone.now', mock_now)
    def test_transmission_now(self):
        view = views.TransmissionViewSet()
        response = view.now(self.factory.get('/'))
        self.assertListEqual(response.data, [{
            'start': '2015-01-06T14:00:00',
            'end': '2015-01-06T15:00:00',
            'name': u'Classic hits',
            'slug': u'classic-hits',
            'url': u'/programmes/classic-hits/'}])


class TestAPI(TestDataMixin, APITestCase):
    def setUp(self):
        super(TestAPI, self).setUp()
        admin = User.objects.create_user(
            username='klaus', password='topsecret')
        admin.user_permissions.add(
            Permission.objects.get(codename='add_schedule'))

        someone = User.objects.create_user(
            username='someone', password='topsecret')

    def test_api(self):
        response = self.client.get('/api/2/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_programmes_get_all(self):
        response = self.client.get('/api/2/programmes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_programmes_post(self):
        response = self.client.post('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_programmes_put(self):
        response = self.client.put('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_programmes_delete(self):
        response = self.client.delete('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_schedules_get_all(self):
        response = self.client.get('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schedules_get_by_programme(self):
        response = self.client.get(
            '/api/2/schedules?programme={}'.format(self.programme.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.programme.name)

    def test_schedules_get_by_nonexisting_programme(self):
        response = self.client.get('/api/2/schedules?programme=4223')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_schedules_get_by_board(self):
        response = self.client.get('/api/2/schedules?schedule_board={}'.format(
            self.schedule_board.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(
            response.data[0]['schedule_board'], self.schedule_board.id)

    def test_schedules_get_by_nonexisting_board(self):
        response = self.client.get('/api/2/schedules?schedule_board=4223')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_schedules_get_by_type(self):
        response = self.client.get('/api/2/schedules?type=L')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(
            response.data[0]['schedule_board'], self.schedule_board.id)

    def test_schedules_get_by_nonexiting_type(self):
        response = self.client.get('/api/2/schedules?type=B')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_schedules_post(self):
        response = self.client.post('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_schedules_post_authenticated_no_permission(self):
        self.client.login(username="someone", password="topsecret")
        response = self.client.post('/api/2/schedules')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_schedules_post_authenticated(self):
        self.client.login(username="klaus", password="topsecret")
        data = {
            "programme": self.programme.id,
            "schedule_board": self.schedule_board.id,
            "day": 0, "start_hour": "07:30:00", "type": "L"}
        response = self.client.post('/api/2/schedules', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_transmissions(self):
        response = self.client.get('/api/2/transmissions')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_transmissions_now(self):
        response = self.client.get('/api/2/transmissions/now')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
