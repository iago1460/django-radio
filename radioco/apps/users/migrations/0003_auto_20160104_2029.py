# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_change_textfield_to_richtextfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(default=b'defaults/default-userprofile-avatar.jpg', upload_to=b'avatars/', verbose_name='avatar'),
        ),
    ]
