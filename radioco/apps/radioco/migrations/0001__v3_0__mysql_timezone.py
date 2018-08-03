# -*- coding: utf-8 -*-


import datetime
import pytz
from django.conf import settings
from django.db import migrations
from django.utils import timezone


def _new_date(dt, default_tz):
    """
    MySQL and other db store datetimes without timezone info,
    so django is given us back a dt with a utc timezone (wrong)
    """
    wrong_utc_date = dt.astimezone(pytz.utc)
    return default_tz.localize(datetime.datetime.combine(wrong_utc_date.date(), wrong_utc_date.time())).astimezone(pytz.utc)


def _migrate_dates(model, fields):
    default_tz = timezone.get_default_timezone()
    for obj in model.objects.all():
        for field in fields:
            dt = getattr(obj, field)
            if dt:
                setattr(obj, field, _new_date(dt, default_tz))
        obj.save()


def migrate_datetime_to_utc(apps, schema_editor):
    """
    version 3 introduces timezone support, this migration will fix the Episode issue_date
    Since Postgres is the only database which is already storing the datetimes in utc we don't need to run on it
    """
    Episode = apps.get_model("programmes", "Episode")

    if Episode.objects.all().exists():
        try:
            db_engine = settings.DATABASES['default']['ENGINE']
        except:
            db_engine = ''

        if 'postgresql' not in db_engine:
            print(' ')
            print('A database engine different than postgresql was detected!')
            print('Applying a special datetime migration')

            _migrate_dates(Episode, ['issue_date'])

            # I can migrate the following two but are not important
            # Token = apps.get_model("authtoken", "token")
            # Auth = apps.get_model("auth", "User")

            # I can't migrate the following apps but are not important
            # Session = apps.get_model("sessions", "Session")
            # Migrations = apps.get_model("django", "Migrations")
            # AdminLog = apps.get_model("django", "AdminLog")


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0001_initial'),
        ('programmes', '0008_auto_20160116_1509'),
        ('global_settings', '0006_auto_20160116_1509'),
        ('users', '0003_auto_20160104_2029'),
    ]

    operations = [
        migrations.RunPython(migrate_datetime_to_utc)
    ]
