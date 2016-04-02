# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0008_auto_20160116_1509'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='programme',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='programme',
            name='start_date',
        ),
    ]
