# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2024-11-30 16:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0008__v3_0__radiocomconfiguration'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='site_color',
            field=models.CharField(default='00B3FE', max_length=6, verbose_name='Site Color'),
        ),
    ]
