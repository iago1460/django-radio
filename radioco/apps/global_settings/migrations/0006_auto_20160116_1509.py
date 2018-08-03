# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0005_auto_20150606_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteconfiguration',
            name='google_analytics_id',
            field=models.CharField(default='', help_text='Example "UA-00000-0"', max_length=255, verbose_name='Google Analytics ID', blank=True),
        ),
    ]
