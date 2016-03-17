# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import recurrence


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='day',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='start_hour',
        ),
        migrations.AddField(
            model_name='schedule',
            name='recurrences',
            # XXX clean migration dstart
            field=recurrence.fields.RecurrenceField(
                default=recurrence.Recurrence(
                    rrules=[recurrence.Rule(recurrence.WEEKLY)])),
            preserve_default=False,
        ),
    ]
