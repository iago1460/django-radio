# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('start_hour', models.TimeField(verbose_name='start time')),
                ('type', models.CharField(max_length=1, verbose_name='type', choices=[(b'L', 'live'), (b'B', 'broadcast'), (b'S', 'broadcast syndication')])),
                ('programme', models.ForeignKey(verbose_name='programme', to='programmes.Programme')),
            ],
            options={
                'verbose_name': 'schedule',
                'verbose_name_plural': 'schedules',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScheduleBoard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='name')),
                ('start_date', models.DateField(null=True, verbose_name='start date', blank=True)),
                ('end_date', models.DateField(null=True, verbose_name='end date', blank=True)),
            ],
            options={
                'verbose_name': 'schedule board',
                'verbose_name_plural': 'schedule board',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='schedule',
            name='schedule_board',
            field=models.ForeignKey(verbose_name='schedule board', to='schedules.ScheduleBoard'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='schedule',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='schedules.Schedule', help_text='It is used when is a broadcast.', null=True, verbose_name='source'),
            preserve_default=True,
        ),
    ]
