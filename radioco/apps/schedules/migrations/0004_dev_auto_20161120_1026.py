# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0003_dev_auto_20161115_0949'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='calendar',
            options={'verbose_name': 'calendar', 'verbose_name_plural': 'calendar'},
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='end_dt',
        ),
    ]
