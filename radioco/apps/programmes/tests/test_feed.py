from rest_framework import status
from rest_framework.test import APITestCase

from radioco.apps.radioco.test_utils import TestDataMixin


EXPECTED_RESULT = '''<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0"><channel><title>Morning News</title><link>http://example.com/programmes/morning-news/</link><description>
        Lorem Ipsum is simply dummy text of the printing and typesetting industry.
        Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
        when an unknown printer took a galley of type and scrambled it to make a type specimen book.
    </description><atom:link href="http://example.com/programmes/morning-news/rss/" rel="self"></atom:link><language>en</language><lastBuildDate>Thu, 01 Jan 2015 08:00:00 +0000</lastBuildDate><itunes:explicit>clean</itunes:explicit><itunes:summary>
        Lorem Ipsum is simply dummy text of the printing and typesetting industry.
        Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
        when an unknown printer took a galley of type and scrambled it to make a type specimen book.
    </itunes:summary><itunes:image href="http://testserver/media/_versions/defaults/example/radio_1_itunes_image.jpg"></itunes:image><itunes:category text="News &amp; Politics"></itunes:category><image url="http://testserver/media/_versions/defaults/example/radio_1_rss_image.jpg" link="http://testserver/programmes/morning-news/" title="Morning News"></image><item><title>1x1 Episode 1</title><link>http://example.com/programmes/morning-news/1x1/</link><description>
        Lorem Ipsum is simply dummy text of the printing and typesetting industry.
        Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
        when an unknown printer took a galley of type and scrambled it to make a type specimen book.
    </description><pubDate>Thu, 01 Jan 2015 08:00:00 +0000</pubDate><enclosure url="https://archive.org/download/Backstate_Wife/1945-08-10_-_1600_-_Backstage_Wife_-_Mary_And_Larry_See_A_Twenty_Year_Old_Portrait_That_Looks_Exactly_Like_Mary_-_32-22_-_14m13s.mp3" length="0" type="audio/mp3"></enclosure><itunes:subtitle>Episode 1</itunes:subtitle><itunes:summary>
        Lorem Ipsum is simply dummy text of the printing and typesetting industry.
        Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
        when an unknown printer took a galley of type and scrambled it to make a type specimen book.
    </itunes:summary><itunes:duration>0:14:13</itunes:duration></item></channel></rss>'''


class TestFeed(TestDataMixin, APITestCase):

    def test_schedules_get_by_programme(self):
        response = self.client.get('/programmes/morning-news/rss/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, EXPECTED_RESULT)
