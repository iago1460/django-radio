# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0004_auto_20150606_1335'),
    ]

    operations = [
        migrations.RenameField(
            model_name='siteconfiguration',
            old_name='footer',
            new_name='about_footer',
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='more_about_us',
            field=models.TextField(default='', verbose_name='More info', blank=True),
            preserve_default=True,
        ),
    ]
