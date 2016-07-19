# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0004_unique_schedule_board_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='end_date',
            field=models.DateTimeField(null=True, verbose_name='end date', blank=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='from_collection',
            field=models.ForeignKey(related_name='child_schedules', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='schedules.Schedule', null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 13, 21, 33, 36, 883435), verbose_name='start date'),
            preserve_default=False,
        ),
    ]
