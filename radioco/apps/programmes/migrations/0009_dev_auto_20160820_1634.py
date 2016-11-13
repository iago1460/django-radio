# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0008_auto_20160116_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programme',
            name='end_date',
            field=models.DateField(null=True, verbose_name='end date', blank=True),
        ),
        migrations.AlterField(
            model_name='programme',
            name='name',
            field=models.CharField(unique=True, max_length=100, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='programme',
            name='slug',
            field=models.SlugField(help_text="Please DON'T change this value. It's used to build URL's.", unique=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='programme',
            name='start_date',
            field=models.DateField(null=True, verbose_name='start date', blank=True),
        ),
    ]
