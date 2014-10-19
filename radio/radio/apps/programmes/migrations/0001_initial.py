# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, null=True, verbose_name='title', blank=True)),
                ('summary', models.TextField(verbose_name='summary', blank=True)),
                ('issue_date', models.DateTimeField(db_index=True, null=True, verbose_name='issue date', blank=True)),
                ('season', models.PositiveIntegerField(verbose_name='season', validators=[django.core.validators.MinValueValidator(1)])),
                ('number_in_season', models.PositiveIntegerField(verbose_name='No. in season', validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'verbose_name': 'episode',
                'verbose_name_plural': 'episodes',
                'permissions': (('see_all_episodes', 'Can see all episodes'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(default=b'NO', max_length=2, verbose_name='role', choices=[(b'NO', 'Not specified'), (b'PR', 'Presenter'), (b'IN', 'Informer'), (b'CO', 'Contributor')])),
                ('description', models.TextField(verbose_name='description', blank=True)),
            ],
            options={
                'verbose_name': 'contributor',
                'verbose_name_plural': 'contributors',
                'permissions': (('see_all_participants', 'Can see all participants'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('episode', models.OneToOneField(primary_key=True, serialize=False, to='programmes.Episode')),
                ('url', models.CharField(max_length=2048)),
                ('mime_type', models.CharField(max_length=20)),
                ('length', models.PositiveIntegerField()),
                ('duration', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text="Please DON'T change this value. It's used to build URL's.", unique=True, max_length=100, verbose_name='name')),
                ('start_date', models.DateField(verbose_name='start date')),
                ('end_date', models.DateField(help_text='This field can be null.', null=True, verbose_name='end date', blank=True)),
                ('synopsis', models.TextField(verbose_name='synopsis', blank=True)),
                ('photo', models.ImageField(default=b'/static/radio/images/default-programme-photo.jpg', upload_to=b'photos/', verbose_name='photo')),
                ('language', models.CharField(default=b'ES', max_length=2, verbose_name='language', choices=[(b'ES', 'Spanish'), (b'GA', 'Galician')])),
                ('current_season', models.PositiveIntegerField(verbose_name='current season', validators=[django.core.validators.MinValueValidator(1)])),
                ('category', models.CharField(blank=True, max_length=50, null=True, verbose_name='category', choices=[(b'Arts', 'Arts'), (b'Business', 'Business'), (b'Comedy', 'Comedy'), (b'Education', 'Education'), (b'Games & Hobbies', 'Games & Hobbies'), (b'Government & Organizations', 'Government & Organizations'), (b'Health', 'Health'), (b'Kids & Family', 'Kids & Family'), (b'Music', 'Music'), (b'News & Politics', 'News & Politics'), (b'Religion & Spirituality', 'Religion & Spirituality'), (b'Science & Medicine', 'Science & Medicine'), (b'Society & Culture', 'Society & Culture'), (b'Sports & Recreation', 'Sports & Recreation'), (b'Technology', 'Technology'), (b'TV & Film', 'TV & Film')])),
                ('slug', models.SlugField(unique=True, max_length=100)),
                ('_runtime', models.PositiveIntegerField(help_text='In minutes.', verbose_name='runtime', validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'verbose_name': 'programme',
                'verbose_name_plural': 'programmes',
                'permissions': (('see_all_programmes', 'Can see all programmes'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(default=b'NO', max_length=2, verbose_name='role', choices=[(b'NO', 'Not specified'), (b'PR', 'Presenter'), (b'IN', 'Informer'), (b'CO', 'Contributor')])),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('date_joined', models.DateField(auto_now_add=True)),
                ('person', models.ForeignKey(verbose_name='person', to=settings.AUTH_USER_MODEL)),
                ('programme', models.ForeignKey(verbose_name='programme', to='programmes.Programme')),
            ],
            options={
                'verbose_name': 'role',
                'verbose_name_plural': 'roles',
                'permissions': (('see_all_roles', 'Can see all roles'),),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together=set([('person', 'programme', 'role')]),
        ),
        migrations.AddField(
            model_name='programme',
            name='announcers',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, verbose_name='announcers', through='programmes.Role', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participant',
            name='episode',
            field=models.ForeignKey(verbose_name='episode', to='programmes.Episode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='participant',
            name='person',
            field=models.ForeignKey(verbose_name='person', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='participant',
            unique_together=set([('person', 'episode', 'role')]),
        ),
        migrations.AddField(
            model_name='episode',
            name='people',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, verbose_name='people', through='programmes.Participant', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='episode',
            name='programme',
            field=models.ForeignKey(verbose_name='programme', to='programmes.Programme'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='episode',
            unique_together=set([('season', 'number_in_season', 'programme')]),
        ),
    ]
