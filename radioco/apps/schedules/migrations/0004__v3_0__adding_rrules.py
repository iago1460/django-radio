# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django.db.models.deletion
import recurrence.fields
from django.db import migrations, models
from django.utils.timezone import utc


def migrate_daily_recurrences(apps, schema_editor):
    """
    Migration to convert weekly recurrences into new complex recurrences
    """
    Schedule = apps.get_model("schedules", "Schedule")
    for schedule in Schedule.objects.all():
        schedule.recurrences = recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.WEEKLY, byday=(int(schedule.day), ))])
        schedule.save()


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0003__v3_0__create_excludeddates_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='end_date',
            field=models.DateTimeField(help_text='This field is dynamically generated to improve performance', null=True, verbose_name='end date', blank=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='from_collection',
            field=models.ForeignKey(related_name='child_schedules', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='schedules.Schedule', null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='recurrences',
            field=recurrence.fields.RecurrenceField(default=recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.WEEKLY)]), help_text='Excluded dates will appear in this list as result of dragging and dropping.', verbose_name='recurrences'),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_daily_recurrences),
        migrations.AddField(
            model_name='schedule',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 1, 0, 0, 0, 0, tzinfo=utc),
                                       verbose_name='start date'),
            preserve_default=False,
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
        migrations.RenameField(
            model_name='schedule',
            old_name='start_date',
            new_name='start_dt',
        ),
    ]
