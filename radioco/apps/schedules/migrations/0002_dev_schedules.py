# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple

from django.db import migrations, models
import datetime
import recurrence.fields
from django.utils import timezone
from django.utils.timezone import utc
import django.db.models.deletion


def migrate_daily_recurrences(apps, schema_editor):
    """
    Migration to convert weekly recurrences into new complex recurrences
    """
    Schedule = apps.get_model("schedules", "Schedule")
    for schedule in Schedule.objects.all():
        schedule.recurrences = recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.WEEKLY, byday=schedule.day)]),
        schedule.save()


def migrate_board(apps, schema_editor):
    """
    Renaming previous Calendars and creating a new one
    """
    ScheduleBoard = apps.get_model("schedules", "ScheduleBoard")
    for board in ScheduleBoard.objects.all():
        board.name = 'Legacy - {name}'.format(name=board.name)
        board.save()

    ScheduleBoard.objects.create(name='Active Calendar', is_active=True)


def migrate_schedules(apps, schema_editor):
    """
    Final Migration

    Before this migration Calendar (ScheduleBoard) had a date limit and all the schedules were repeated weekly
    We want to move constraint dates from Calendar to programmes and clone the active schedules into the active calendar
    """
    Board = namedtuple('Board', ['start_date', 'end_date'])
    Schedule = apps.get_model("schedules", "Schedule")
    ScheduleBoard = apps.get_model("schedules", "ScheduleBoard")
    tz = timezone.get_default_timezone()

    boards = {}
    for board in ScheduleBoard.objects.all():
        boards[board.id] = Board(board.start_date, board.end_date)

    active_board = ScheduleBoard.objects.get(name='Active Calendar', is_active=True)  # Created by previous migration
    for schedule in Schedule.objects.all().select_related('programme'):
        schedule_board = boards[schedule.schedule_board.id]
        if schedule_board.start_date:
            schedule.start_date = tz.localize(datetime.datetime.combine(schedule_board.start_date, schedule.start_hour))
            schedule.save()

            # Create a copy, keeping previous schedule
            schedule.id = schedule.pk = None
            schedule.schedule_board = active_board
            schedule.save()

            # Add the lower start_date to the programme
            if schedule.programme.start_date is None or schedule.programme.start_date > schedule_board.start_date:
                schedule.programme.start_date = schedule_board.start_date
                schedule.programme.save()

            # Add the bigger end_date to the programme
            if schedule_board.end_date and (schedule.programme.end_date is None or schedule.programme.end_date < schedule_board.end_date):
                schedule.programme.end_date = schedule_board.end_date
                schedule.programme.save()

        else:
            # case when start_date and end_date doesn't exist
            # this schedules are disable, we don't need to migrate them but at least we fix the weekday
            date = datetime.date(2016, 1, 4) + datetime.timedelta(days=schedule.day)
            schedule.start_date = tz.localize(datetime.datetime.combine(date, schedule.start_hour))
            schedule.save()


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0001_initial'),
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
            model_name='schedule',
            name='end_date',
            field=models.DateTimeField(help_text='This field is dynamically generated to improve performance', null=True, verbose_name='end date', blank=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='from_collection',
            field=models.ForeignKey(related_name='child_schedules', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='schedules.Schedule', null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='recurrences',
            field=recurrence.fields.RecurrenceField(default=recurrence.Recurrence(rrules=[recurrence.Rule(recurrence.WEEKLY)]), verbose_name='recurrences'),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_daily_recurrences),
        migrations.AddField(
            model_name='schedule',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 1, 1, 0, 0, 0, 0, tzinfo=utc), verbose_name='start date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scheduleboard',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='excludeddates',
            name='schedule',
            field=models.ForeignKey(to='schedules.Schedule'),
        ),
        migrations.RunPython(migrate_board),
        migrations.RunPython(migrate_schedules),
        migrations.RemoveField(
            model_name='schedule',
            name='day',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='start_hour',
        ),
        migrations.RemoveField(
            model_name='scheduleboard',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='scheduleboard',
            name='start_date',
        ),
    ]
