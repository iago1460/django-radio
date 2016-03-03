from django.test import TestCase
from rest_framework.test import APIClient

import serializers


class TestSerializers(TestCase):
    def test_programme(self):
        serializer = serializers.ProgrammeSerializer()
        self.assertEqual(
            serializer.fields.keys(),
            ['url', 'name', 'synopsis', 'photo', 'language', 'category'])


class TestAPI(TestCase):
    client_class = APIClient

    def test_api(self):
        response = self.client.get('/api/2/')
        self.assertEqual(response.status_code, 200)

    def test_programmes_get_all(self):
        response = self.client.get('/api/2/programmes/')
        self.assertEqual(response.status_code, 200)

    def test_programmes_post(self):
        response = self.client.post('/api/2/programmes/')
        self.assertEqual(response.status_code, 405)

    def test_programmes_put(self):
        response = self.client.put('/api/2/programmes/')
        self.assertEqual(response.status_code, 405)

    def test_programmes_delete(self):
        response = self.client.delete('/api/2/programmes/')
        self.assertEqual(response.status_code, 405)
