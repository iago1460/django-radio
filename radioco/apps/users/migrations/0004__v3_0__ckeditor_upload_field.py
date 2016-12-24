# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20160104_2029'),
        ('radioco', '0001__v3_0__mysql_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=ckeditor_uploader.fields.RichTextUploadingField(verbose_name='biography', blank=True),
        ),
    ]
