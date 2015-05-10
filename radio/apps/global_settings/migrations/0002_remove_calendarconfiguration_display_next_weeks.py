# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendarconfiguration',
            name='display_next_weeks',
        ),
    ]
