# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0002_remove_calendarconfiguration_display_next_weeks'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='footer',
            field=models.TextField(default=b'', help_text='Can contain raw HTML.', verbose_name='Footer', blank=True),
            preserve_default=True,
        ),
    ]
