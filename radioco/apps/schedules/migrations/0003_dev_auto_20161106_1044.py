# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0002_dev_schedules'),
    ]

    operations = [
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
            field=models.DateTimeField(help_text='This field is dynamically generated to improve performance', null=True, verbose_name='last possible end date', blank=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='effective_start_dt',
            field=models.DateTimeField(help_text='This field is dynamically generated to improve performance', null=True, verbose_name='first possible start date', blank=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='end_dt',
            field=models.DateTimeField(help_text='This field is dynamically generated based on the programme duration', null=True, verbose_name='end date', blank=True),
        ),
    ]
