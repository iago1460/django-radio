# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0007__v3_0__calendarconfiguration_tweaks'),
    ]

    operations = [
        migrations.CreateModel(
            name='RadiocomConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('station_name', models.CharField(default=b'RadioCo', help_text='The name of radio station', max_length=255, verbose_name='station name')),
                ('icon_url', models.URLField(help_text='The icon url where the store icon is.', max_length=255, verbose_name='big icon url', blank=True)),
                ('big_icon_url', models.URLField(help_text='The icon url where the store icon is.', max_length=255, verbose_name='icon url', blank=True)),
                ('history', models.TextField(default=b'', help_text='The history of the station', verbose_name='history', blank=True)),
                ('latitude', models.FloatField(default=0, verbose_name='latitude', blank=True)),
                ('longitude', models.FloatField(default=0, verbose_name='longitude', blank=True)),
                ('news_rss', models.URLField(help_text='The news rss url where the recordings news rss', max_length=255, verbose_name='news_rss', blank=True)),
                ('station_photos', models.TextField(default=b'', help_text='A list of urls to the station photos', verbose_name='station photos', blank=True)),
                ('stream_url', models.URLField(help_text='The stream url where its hear actual program', max_length=255, verbose_name='stream url', blank=True)),
            ],
            options={
                'default_permissions': ('change',),
                'verbose_name': 'Radiocom Configuration',
                'verbose_name_plural': 'Radiocom Configuration',
            },
        ),
    ]
