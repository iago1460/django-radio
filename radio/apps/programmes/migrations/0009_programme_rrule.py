# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import recurrence
from django.db import migrations, models
from recurrence.fields import RecurrenceField
from apps.programmes.models import Programme


def keep_weekly(apps, schema_editor):
    rrule = recurrence.Rule(recurrence.WEEKLY)

    for programme in Programme.objects.all():
        if not programme.recurrences:
            programme.recurrences = recurrence.Recurrence(rrules=[rrule])
            programme.save()


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0008_auto_20160116_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='programme',
            name='recurrences',
            field=RecurrenceField(blank=True, null=True),
        ),
        migrations.RunPython(keep_weekly),
    ]

