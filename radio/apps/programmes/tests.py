import datetime
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from radio.apps.schedules.models import Programme, Episode


class ProgrammeMethodTests(TestCase):

    def test_save_programme(self):
        programme = Programme(name="Test programme", synopsis="This is a description")
        programme.save()
        self.assertEqual(programme, Programme.objects.get(id=programme.id))
        self.assertTrue(programme in Programme.objects.all())

    def test_save_episode(self):
        date_published = datetime.datetime(2014, 1, 31, 0, 0, 0, 0, tzinfo=timezone.utc)
        programme = Programme(name="My programme", synopsis="This is a description")
        programme.save()
        episode = Episode(summary='Summary', published=date_published, programme=programme)
        episode.save()

        self.assertEqual(episode, Episode.objects.get(id=episode.id))
        self.assertEqual(programme, Programme.objects.get(id=programme.id))
        self.assertEqual(episode.programme, Programme.objects.get(id=episode.programme.id))

