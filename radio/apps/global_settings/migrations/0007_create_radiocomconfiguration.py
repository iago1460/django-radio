# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    # dependencies = [
    # ]

    dependencies = [
        ('global_settings', '0006_auto_20160116_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='RadiocomConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('station_name', models.CharField(default=b'',
                                                  help_text='The name of radio station',
                                                  max_length=50, verbose_name='station_name', blank=True)),
                ('icon_url', models.CharField(default=b'',
                                              help_text='The big icon url where the store icon.',
                                              max_length=500, verbose_name='big icon url', blank=True)),
                ('big_icon_url', models.CharField(default=b'',
                                                  help_text='The big icon url where the store icon.',
                                                  max_length=500, verbose_name='big icon url', blank=True)),
                ('history', models.CharField(default=b'',
                                             help_text='The history url where the show history of the station',
                                             max_length=500, verbose_name='history', blank=True)),
                ('latitude', models.FloatField(default=0,
                                               help_text='The latitude where place the radio station',
                                               max_length=10, verbose_name='latitude', blank=True)),
                ('longitude', models.FloatField(default=0,
                                                help_text='The longitude where the place the radio station',
                                                max_length=10, verbose_name='longitude', blank=True)),
                ('news_rss', models.CharField(default=b'',
                                              help_text='The news rss url where the recordings news rss',
                                              max_length=500, verbose_name='news_rss', blank=True)),
                ('station_photos', models.CharField(default=b'',
                                                    help_text='The source url where the place the images of team radio station',
                                                    max_length=500, verbose_name='station_photos', blank=True)),
                ('stream_url', models.CharField(default=b'',
                                                help_text='The stream url where its hear actual program',
                                                max_length=500, verbose_name='stream_url', blank=True))
            ],
            options={
                'default_permissions': ('change',),
                'verbose_name': 'Radiocom_Configuration',
                'verbose_name_plural': 'Radiocom_Configuration',
            },
            bases=(models.Model,),
        )
    ]
