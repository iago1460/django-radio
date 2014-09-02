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
from radio.apps.programmes.models import Programme, Podcast

class iTunesFeed(feedgenerator.Rss201rev2Feed):

    def __init__(self, title, link, description, language=None, author_email=None,
            author_name=None, author_link=None, subtitle=None, categories=None,
            feed_url=None, feed_copyright=None, feed_guid=None, ttl=None, **kwargs):
        self.programme = kwargs['programme']
        feedgenerator.Rss201rev2Feed.__init__(self, title, link, description, self.programme.language.lower(), author_email, author_name, author_link, subtitle, categories, feed_url, feed_copyright, feed_guid, ttl)


    def rss_attributes(self):
        attrs = super(iTunesFeed, self).rss_attributes()
        attrs['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        return attrs

    def add_root_elements(self, handler):
        super(iTunesFeed, self).add_root_elements(handler)
        handler.addQuickElement('itunes:explicit', 'clean')
        handler.addQuickElement('itunes:summary', self.programme.synopsis)
        if self.programme.category:
            handler.addQuickElement('itunes:category', self.programme.category)

    def add_item_elements(self, handler, item):
        super(iTunesFeed, self).add_item_elements(handler, item)

        podcast = item["podcast"]
        handler.addQuickElement("itunes:subtitle", podcast.episode.title)
        handler.addQuickElement("itunes:summary", podcast.episode.summary)
        handler.addQuickElement("itunes:duration", str(datetime.timedelta(seconds=podcast.duration)))


class ProgrammeFeed(Feed):

    def title(self, programme):
        return programme.name

    def get_object(self, request, slug):
        self.programme = get_object_or_404(Programme, slug=slug)
        return self.programme

    def link(self, programme):
        return programme.get_absolute_url()

    def description(self, programme):
        return programme.synopsis

    # feed_copyright = podcast_config.copyright

    def feed_extra_kwargs(self, programme):
        return {'programme':programme}

    def items(self, programme):
        return Podcast.objects.filter(episode__programme=programme).order_by('-episode__issue_date').select_related('episode')

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


    def item_guid(self, episode):
        return None

    def description(self, programme):
        return programme.synopsis





