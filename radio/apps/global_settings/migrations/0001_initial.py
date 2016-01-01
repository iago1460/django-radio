# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scroll_time', models.TimeField(default=datetime.time(0, 0), help_text='Determines how far down the scroll pane is initially scrolled down.', verbose_name='scroll time')),
                ('first_day', models.IntegerField(default=0, help_text='The day that the calendar begins', verbose_name='first day', choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('min_time', models.TimeField(default=datetime.time(0, 0), help_text='Determines the starting time that will be displayed, even when the scrollbars have been scrolled all the way up.', verbose_name='min time')),
                ('max_time', models.TimeField(default=datetime.time(23, 59, 59), help_text='Determines the end time (exclusively) that will be displayed, even when the scrollbars have been scrolled all the way down.', verbose_name='max time')),
                ('display_next_weeks', models.PositiveIntegerField(default=1, verbose_name='display next weeks')),
            ],
            options={
                'default_permissions': ('change',),
                'verbose_name': 'Calendar Configuration',
                'verbose_name_plural': 'Calendar Configuration',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PodcastConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url_source', models.CharField(default=b'', help_text='The source url where the recordings will be available after the upload. For example: "http://RadioCo.org/recordings/"', max_length=500, verbose_name='URL Source', blank=True)),
                ('start_delay', models.PositiveIntegerField(default=0, help_text='In seconds. Initial delay of recordings', verbose_name='start delay')),
                ('end_delay', models.PositiveIntegerField(default=0, help_text='In seconds.', verbose_name='end delay')),
                ('next_events', models.PositiveIntegerField(default=32, help_text='In hours. The next events supplied to the recorder program', verbose_name='next events')),
            ],
            options={
                'default_permissions': ('change',),
                'verbose_name': 'Podcast Configuration',
                'verbose_name_plural': 'Podcast Configuration',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('site_name', models.CharField(default=b'RadioCo', max_length=255, verbose_name='Site Name')),
            ],
            options={
                'default_permissions': ('change',),
                'verbose_name': 'Global Configuration',
                'verbose_name_plural': 'Global Configuration',
            },
            bases=(models.Model,),
        ),
    ]
