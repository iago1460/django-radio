# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_board(apps, schema_editor):
    """
    Renaming previous Calendars and creating a new one
    """
    Calendar = apps.get_model("schedules", "Calendar")
    for board in Calendar.objects.all():
        board.name = 'Legacy - {name}'.format(name=board.name)
        board.save()

    Calendar.objects.create(name='Active Calendar', is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0001_initial'),
        ('radioco', '0001__v3_0__mysql_timezone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='schedule_board',
            new_name='calendar',
        ),
        migrations.RenameModel(
            old_name='ScheduleBoard',
            new_name='Calendar',
        ),
        migrations.AlterField(
            model_name='schedule',
            name='calendar',
            field=models.ForeignKey(verbose_name='calendar', to='schedules.Calendar'),
        ),
        migrations.AlterModelOptions(
            name='calendar',
            options={'verbose_name': 'calendar', 'verbose_name_plural': 'calendar'},
        ),
        migrations.AddField(
            model_name='calendar',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(migrate_board)
    ]
