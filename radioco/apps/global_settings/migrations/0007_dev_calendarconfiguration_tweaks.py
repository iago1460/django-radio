# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0006_auto_20160116_1509'),
        ('radioco', '0001_mysql_timezone'),
    ]

    operations = [
        migrations.RemoveField( 
            model_name='calendarconfiguration',
            name='scroll_time',
        ),
        migrations.AddField(
            model_name='calendarconfiguration',
            name='slot_duration',
            field=models.DurationField(default=datetime.timedelta(0, 1800), help_text='The frequency for displaying time slots. Format hh:mm:ss', verbose_name='slot duration'),
        ),
    ]
