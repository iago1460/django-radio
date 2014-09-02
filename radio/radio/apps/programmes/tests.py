import datetime
from django.test import TestCase

from radio.apps.programmes.models import Programme, Episode


class ProgrammeMethodTests(TestCase):

    def test_save_programme(self):
        programme = Programme.objects.create(name="Test programme", synopsis="This is a description", _runtime=60, start_date=datetime.date(2014, 1, 31), current_season=1)
        self.assertEqual(programme, Programme.objects.get(id=programme.id))
        self.assertTrue(programme in Programme.objects.all())

    def test_save_episode(self):
        date_published = datetime.datetime(2014, 1, 31, 0, 0, 0, 0)
        programme = Programme.objects.create(name="Test programme", synopsis="This is a description", _runtime=60, start_date=datetime.date(2014, 1, 31), current_season=1)
        episode = Episode.create_episode(date=date_published, programme=programme)

        self.assertEqual(episode, Episode.objects.get(id=episode.id))
        self.assertEqual(programme, Programme.objects.get(id=programme.id))
        self.assertEqual(episode.programme, Programme.objects.get(id=episode.programme.id))

