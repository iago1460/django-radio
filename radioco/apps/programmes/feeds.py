# Radioco - Broadcasting Radio Recording Scheduling system.
# Copyright (C) 2014  Iago Veloso Abalo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import datetime

from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils import feedgenerator
from filebrowser.base import FileObject
from filebrowser.sites import get_default_site

from radioco.apps.global_settings.models import RadiocomConfiguration
from radioco.apps.programmes.models import Programme, Podcast

# TODO:
# Tag values are limited to 255 characters, except for <itunes:summary>, which can be up to 4000 characters.
# Don't add leading or trailing spaces to your values.
# Enclose all portions of your XML that contain embedded links in a CDATA section to prevent formatting issues,
# and to ensure proper link functionality.
# For example: <itunes:summary><![CDATA[<a href="http://www.apple.com">Apple</a>]]></itunes:summary>


class iTunesFeed(feedgenerator.Rss201rev2Feed):
    def __init__(self, title, link, description, language=None, author_email=None,
                 author_name=None, author_link=None, subtitle=None, categories=None,
                 feed_url=None, feed_copyright=None, feed_guid=None, ttl=None, **kwargs):
        self.programme = kwargs['programme']
        self.request = kwargs['request']
        feedgenerator.Rss201rev2Feed.__init__(
            self, title, link, description, self.programme.language.lower(), author_email, author_name,
            author_link, subtitle, categories, feed_url, feed_copyright, feed_guid, ttl
        )

    def rss_attributes(self):
        attrs = super(iTunesFeed, self).rss_attributes()
        attrs['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        return attrs

    def add_root_elements(self, handler):
        super(iTunesFeed, self).add_root_elements(handler)
        image_file = FileObject(self.programme.photo.name, site=get_default_site())
        image_url = self.request.build_absolute_uri(image_file.version_generate('rss_image').url)
        itunes_image_url = self.request.build_absolute_uri(image_file.version_generate('itunes_image').url)
        handler.addQuickElement('itunes:explicit', 'clean')
        handler.addQuickElement('itunes:summary', self.programme.synopsis_text)
        handler.addQuickElement('itunes:image', '', {'href': itunes_image_url})
        if self.programme.category:
            handler.addQuickElement('itunes:category', '', {'text': self.programme.category})
        handler.addQuickElement(
            'image',
            '',
            {
                 'url': image_url,
                 'title': self.programme.name,
                 'link': self.request.build_absolute_uri(self.programme.get_absolute_url()),
            }
        )
        handler.addQuickElement('itunes:author', RadiocomConfiguration.get_global().station_name)

    def add_item_elements(self, handler, item):
        super(iTunesFeed, self).add_item_elements(handler, item)

        podcast = item["podcast"]
        handler.addQuickElement("itunes:subtitle", podcast.episode.title)
        handler.addQuickElement("itunes:summary", podcast.episode.summary_text)
        handler.addQuickElement("itunes:duration", str(datetime.timedelta(minutes=podcast.duration)))
        handler.addQuickElement("itunes:season", str(podcast.episode.season))
        handler.addQuickElement("itunes:epsiode", str(podcast.episode.number_in_season))
        handler.addQuickElement("guid", str(podcast.episode.id))


class ProgrammeFeed(Feed):
    def title(self, programme):
        return programme.name

    def get_object(self, request, slug):
        self.request = request
        self.programme = get_object_or_404(Programme, slug=slug)
        return self.programme

    def link(self, programme):
        return programme.get_absolute_url()

    def description(self, programme):
        return programme.synopsis

    # feed_copyright = podcast_config.copyright

    def feed_extra_kwargs(self, programme):
        return {'programme': programme, 'request': self.request}

    def items(self, programme):
        return Podcast.objects.filter(
            episode__programme=programme
        ).order_by('-episode__issue_date').select_related('episode__programme')

    def item_title(self, podcast):
        return podcast.episode

    def item_description(self, podcast):
        return podcast.episode.summary

    def item_pubdate(self, podcast):
        return podcast.episode.issue_date

    def item_enclosure_url(self, podcast):
        return podcast.url

    def item_enclosure_length(self, podcast):
        return podcast.length

    def item_enclosure_mime_type(self, podcast):
        return podcast.mime_type

    def item_keywords(self, podcast):
        return podcast.keywords

    def item_extra_kwargs(self, podcast):
        extra = {}
        extra["podcast"] = podcast
        return extra


class RssProgrammeFeed(ProgrammeFeed):
    feed_type = iTunesFeed

    def item_guid(self, podcast):
        return None
