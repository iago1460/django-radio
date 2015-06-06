# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('programmes', '0004_change_photo_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='podcast',
            name='episode',
            field=models.OneToOneField(related_name='podcast', primary_key=True, serialize=False, to='programmes.Episode'),
            preserve_default=True,
        ),
    ]
