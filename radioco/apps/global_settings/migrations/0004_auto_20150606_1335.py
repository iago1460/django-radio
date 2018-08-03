# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('global_settings', '0003_siteconfiguration_footer'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='address',
            field=models.TextField(default='', help_text='Can contain raw HTML.', verbose_name='Address', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='facebook_address',
            field=models.CharField(max_length=255, null=True, verbose_name='facebook address', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='google_analytics_id',
            field=models.CharField(default='', max_length=255, verbose_name='Example "UA-00000-0"', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='siteconfiguration',
            name='twitter_address',
            field=models.CharField(max_length=255, null=True, verbose_name='Twitter address', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='siteconfiguration',
            name='footer',
            field=models.TextField(default='', verbose_name='Footer', blank=True),
            preserve_default=True,
        ),
    ]
