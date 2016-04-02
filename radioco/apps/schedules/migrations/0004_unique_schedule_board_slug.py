# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0003_add_schedule_board_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleboard',
            name='slug',
            field=models.SlugField(unique=True, max_length=255),
        ),
    ]
