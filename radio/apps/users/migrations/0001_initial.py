# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bio', models.TextField(verbose_name='biography', blank=True)),
                ('avatar', models.ImageField(default=b'/static/radio/images/default-userprofile-avatar.jpg', upload_to=b'avatars/', verbose_name='avatar')),
                ('display_personal_page', models.BooleanField(default=False, verbose_name='display personal page')),
                ('slug', models.SlugField(max_length=30)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('change',),
                'verbose_name': 'user profile',
                'verbose_name_plural': 'user profile',
            },
            bases=(models.Model,),
        ),
    ]
