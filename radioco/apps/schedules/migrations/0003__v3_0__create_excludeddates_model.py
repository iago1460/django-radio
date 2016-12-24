# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0002__v3_0__renaming_calendar_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcludedDates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='excludeddates',
            name='schedule',
            field=models.ForeignKey(to='schedules.Schedule'),
        ),
    ]
