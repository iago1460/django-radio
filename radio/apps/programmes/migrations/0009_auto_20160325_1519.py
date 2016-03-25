# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0008_auto_20160116_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='people',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='people', through='programmes.Participant', blank=True),
        ),
        migrations.AlterField(
            model_name='programme',
            name='announcers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='announcers', through='programmes.Role', blank=True),
        ),
    ]
