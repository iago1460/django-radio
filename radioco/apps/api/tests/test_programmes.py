import datetime

from rest_framework import status
from rest_framework.test import APITestCase

from radioco.apps.programmes.models import Programme
from radioco.apps.radioco.test_utils import TestDataMixin


class TestProgrammesAPI(TestDataMixin, APITestCase):
    def setUp(self):
        self.summer_programme = Programme.objects.create(
            name='Summer Programme',
            synopsis='',
            language='en',
            current_season=1,
            _runtime=60,
            start_date=datetime.date(2015, 6, 1),
            end_date=datetime.date(2015, 8, 31),
        )

    def test_programmes_get_all(self):
        response = self.client.get('/api/2/programmes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            {
                'category': None,
                'id': self.summer_programme.id,
                'language': 'en',
                'name': 'Summer Programme',
                'photo_url': 'http://testserver/media/defaults/default-programme-photo.jpg',
                'rss_url': 'http://testserver/programmes/summer-programme/rss/',
                'runtime': '01:00:00',
                'slug': 'summer-programme',
                'synopsis': ''
            },
            response.data)

    def test_programmes_before(self):
        response = self.client.get(
            '/api/2/programmes',
            {
                'before': datetime.date(2015, 6, 1),
            })
        self.assertIn('summer-programme', [t['slug'] for t in response.data])

        response = self.client.get(
            '/api/2/programmes',
            {
                'before': datetime.date(2015, 5, 30),
            })
        self.assertNotIn('summer-programme', [t['slug'] for t in response.data])

    def test_programmes_after(self):
        response = self.client.get(
            '/api/2/programmes',
            {
                'after': datetime.date(2015, 8, 31),
            })
        self.assertIn('summer-programme', [t['slug'] for t in response.data])

        response = self.client.get(
            '/api/2/programmes',
            {
                'after': datetime.date(2015, 9, 1),
            })
        self.assertNotIn('summer-programme', [t['slug'] for t in response.data])

    def test_programmes_between(self):
        response = self.client.get(
            '/api/2/programmes',
            {
                'after': datetime.date(2015, 1, 1),
                'before': datetime.date(2015, 12, 31),
            })
        self.assertIn('summer-programme', [t['slug'] for t in response.data])

        response = self.client.get(
            '/api/2/programmes',
            {
                'after': datetime.date(2015, 1, 1),
                'before': datetime.date(2015, 5, 30),
            })
        self.assertNotIn('summer-programme', [t['slug'] for t in response.data])

    def test_episodes_get_all(self):
        response = self.client.get('/api/2/episodes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_episodes_get_by_programme(self):
        response = self.client.get(
            '/api/2/episodes', {'programme': self.programme.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['programme'], self.programme.slug)


class TestNotAllowedMethodsProgrammesAPI(TestDataMixin, APITestCase):

    def test_programmes_post(self):
        response = self.client.post('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN)

    def test_programmes_put(self):
        response = self.client.put('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN)

    def test_programmes_delete(self):
        response = self.client.delete('/api/2/programmes')
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN)

    def test_episodes_post(self):
        response = self.client.post('/api/2/episodes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_episodes_put(self):
        response = self.client.put('/api/2/episodes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_episodes_delete(self):
        response = self.client.delete('/api/2/episodes')
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)