from apps.programmes.models import Programme, Episode
from apps.schedules.models import ScheduleBoard, Schedule
from apps.schedules.models import WE
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

import serializers
import datetime


class TestSerializers(TestCase):
    def setUp(self):
        self.programme = Programme(
            name="Test-Programme", current_season=1, runtime=540,
            start_date=datetime.datetime(2014, 1, 1, 0, 0, 0, 0))

        schedule_board = ScheduleBoard(
            name='Board',
            start_date=datetime.datetime(2014, 1, 1, 0, 0, 0, 0))

        self.schedule = Schedule(
            schedule_board=schedule_board, programme=self.programme,
            start_hour=datetime.time(0, 0, 0), day=WE, type='L')

    def test_programme(self):
        serializer = serializers.ProgrammeSerializer()
        self.assertEqual(
            serializer.fields.keys(),
            ['url', 'name', 'synopsis', 'photo', 'language', 'category'])

    def test_schedule(self):
        serializer = serializers.ScheduleSerializer()
        self.assertEqual(
            serializer.fields.keys(),
            ['id', 'programme', 'schedule_board', 'day', 'start_hour',
             'start', 'end', 'allDay', 'title', 'type',
             'textColor', 'backgroundColor'])

    def test_schedule_title(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        self.assertEqual(serializer.data['title'], self.programme.name)

    def test_schedule_start(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        self.assertEqual(
            serializer.data['start'], datetime.datetime(2014, 1, 1, 0, 0))

    def test_schedule_end(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        self.assertEqual(
            serializer.data['end'], datetime.datetime(2014, 1, 1, 9, 0))

    def test_schedule_allDay(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        self.assertEqual(serializer.data['allDay'], False)

    def test_schedule_textColor(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        self.assertEqual(serializer.data['textColor'], 'black')

    def test_schedule_backgroundColor(self):
        serializer = serializers.ScheduleSerializer(self.schedule)
        self.assertEqual(serializer.data['backgroundColor'], '#F9AD81')


class TestAPI(APITestCase):
    def setUp(self):
        admin = User.objects.create_user(
            username='admin', password='topsecret')
        admin.user_permissions.add(
            Permission.objects.get(codename='add_schedule'))

        someone = User.objects.create_user(
            username='someone', password='topsecret')

        self.programme = Programme.objects.create(
            name="Test-Programme",
            start_date=datetime.datetime(2014, 1, 1, 0, 0, 0, 0),
            current_season=1,
            runtime=540)

        self.schedule_board = ScheduleBoard.objects.create(
            name='Board',
            start_date=datetime.datetime(2014, 1, 1, 0, 0, 0, 0))

        self.schedule = Schedule.objects.create(
            programme=self.programme,
            schedule_board=self.schedule_board,
            day=WE, start_hour=datetime.time(0, 0, 0), type='L')

    def test_api(self):
        response = self.client.get('/api/2/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_programmes_get_all(self):
        response = self.client.get('/api/2/programmes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_programmes_post(self):
        response = self.client.post('/api/2/programmes/')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_programmes_put(self):
        response = self.client.put('/api/2/programmes/')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_programmes_delete(self):
        response = self.client.delete('/api/2/programmes/')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_schedules_get_all(self):
        response = self.client.get('/api/2/schedules/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schedules_post(self):
        response = self.client.post('/api/2/schedules/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_schedules_post_authenticated_no_permission(self):
        self.client.login(username="someone", password="topsecret")
        response = self.client.post('/api/2/schedules/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_schedules_post_authenticated(self):
        self.client.login(username="admin", password="topsecret")
        data = {
            "programme": self.programme.id,
            "schedule_board": self.schedule_board.id,
            "day": 0, "start_hour": "07:30:00", "type": "L"}
        response = self.client.post('/api/2/schedules/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
