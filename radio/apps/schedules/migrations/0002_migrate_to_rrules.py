# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import recurrence


def migrate_schedules(apps, schema_editor):
    Schedule = apps.get_model("schedules", "Schedule")
    for schedule in Schedule.objects.all():
        day = datetime.date(2016, 1, 4) + datetime.timedelta(days=schedule.day)
        hour = schedule.start_hour
        schedule.recurrences.dtstart = datetime.datetime.combine(day, hour)
        schedule.save()


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='recurrences',
            field=recurrence.fields.RecurrenceField(
                default=recurrence.Recurrence(
                    rrules=[recurrence.Rule(recurrence.WEEKLY)])),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_schedules),
        migrations.RemoveField(
            model_name='schedule',
            name='day',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='start_hour',
        ),
    ]
