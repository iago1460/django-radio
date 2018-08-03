# -*- coding: utf-8 -*-


from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=ckeditor.fields.RichTextField(verbose_name='biography', blank=True),
            preserve_default=True,
        ),
    ]
