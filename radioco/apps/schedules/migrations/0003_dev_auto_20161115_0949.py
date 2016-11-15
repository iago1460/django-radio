# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0002_dev_schedules'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ScheduleBoard',
            new_name='Calendar',
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='start_date',
            new_name='start_dt',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='end_date',
        ),
        migrations.AddField(
            model_name='schedule',
            name='effective_end_dt',
            field=models.DateTimeField(help_text='This field is dynamically generated to improve performance', null=True, verbose_name='last effective end date', blank=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='effective_start_dt',
            field=models.DateTimeField(help_text='This field is dynamically generated to improve performance', null=True, verbose_name='first effective start date', blank=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='end_dt',
            field=models.DateTimeField(help_text='This field is dynamically generated based on the programme duration', null=True, verbose_name='end date', blank=True),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='calendar',
            field=models.ForeignKey(verbose_name='calendar', to='schedules.Calendar'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='from_collection',
            field=models.ForeignKey(related_name='child_schedules', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='schedules.Schedule', help_text='Parent schedule (only happens when it is changed from recurrence.', null=True),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='schedules.Schedule', help_text='Main schedule when (if this is a broadcast).', null=True, verbose_name='source'),
        ),
    ]
